import os
import time
import requests
import subprocess
import platform
import tempfile
from tqdm import tqdm
from .logging_config import get_logger

logger = get_logger(__name__)

OLLAMA_URL = "http://localhost:11434"
REQUIRED_MODEL = "llama3.1:8b"
DOWNLOAD_TIMEOUT = 1800
SERVICE_TIMEOUT = 60


class OllamaManager:
    """Gerenciador para instalação e configuração automática do Ollama."""

    def __init__(self):
        self.system = platform.system().lower()
        self.architecture = platform.machine().lower()

    def ensure_ollama_ready(self) -> bool:
        """
        Garante que o Ollama esteja instalado, rodando e com o modelo necessário.

        Returns:
            bool: True se tudo estiver configurado corretamente
        """
        try:
            logger.info("Verificando instalação e configuração do Ollama...")

            if not self._is_ollama_installed():
                logger.info(
                    "Ollama não encontrado. Iniciando instalação automática...")
                if not self._install_ollama():
                    logger.error("Falha na instalação automática do Ollama")
                    return False

            if not self._is_service_running():
                logger.info("Iniciando serviço Ollama...")
                if not self._start_ollama_service():
                    logger.error("Falha ao iniciar serviço Ollama")
                    return False

            if not self._is_model_available(REQUIRED_MODEL):
                logger.info(
                    f"Modelo {REQUIRED_MODEL} não encontrado. Iniciando download...")
                if not self._pull_model(REQUIRED_MODEL):
                    logger.error(
                        f"Falha no download do modelo {REQUIRED_MODEL}")
                    return False

            logger.info("Ollama configurado e pronto para uso!")
            return True

        except Exception as e:
            logger.exception(f"Erro na configuração do Ollama: {e}")
            return False

    def _is_ollama_installed(self) -> bool:
        """Verifica se o Ollama está instalado no sistema."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                logger.debug(f"Ollama encontrado: {result.stdout.strip()}")
                return True
            return False
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return False

    def _is_service_running(self) -> bool:
        """Verifica se o serviço Ollama está rodando."""
        try:
            response = requests.get(f"{OLLAMA_URL}/api/version", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def _is_model_available(self, model_name: str) -> bool:
        """Verifica se um modelo específico está disponível localmente."""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                return model_name in result.stdout
            return False
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            return False

    def _install_ollama(self) -> bool:
        """Instala o Ollama no Windows."""
        try:
            logger.info("Baixando instalador do Ollama para Windows...")
            installer_url = "https://ollama.com/download/OllamaSetup.exe"

            with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as tmp_file:
                head_response = requests.head(installer_url, timeout=30)
                total_size = int(
                    head_response.headers.get('content-length', 0))

                response = requests.get(
                    installer_url, stream=True, timeout=300)
                response.raise_for_status()

                with tqdm(
                    total=total_size,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc="Baixando Ollama",
                    ncols=70
                ) as pbar:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            tmp_file.write(chunk)
                            pbar.update(len(chunk))

                installer_path = tmp_file.name

            logger.info("Executando instalador do Ollama...")

            result = subprocess.run(
                [installer_path, "/S"],
                timeout=300,
                capture_output=True,
                text=True
            )

            try:
                os.unlink(installer_path)
            except OSError:
                pass

            if result.returncode == 0:
                logger.info("Ollama instalado com sucesso no Windows")

                time.sleep(5)

                self._ensure_ollama_in_path_windows()
                return True
            else:
                logger.error(f"Falha na instalação: {result.stderr}")
                return False

        except Exception as e:
            logger.exception(f"Erro na instalação do Ollama no Windows: {e}")
            return False

    def _ensure_ollama_in_path_windows(self):
        """Garante que o Ollama esteja no PATH do Windows."""
        try:
            common_paths = [
                os.path.expanduser("~\\AppData\\Local\\Programs\\Ollama"),
                "C:\\Program Files\\Ollama",
                "C:\\Program Files (x86)\\Ollama"
            ]

            ollama_path = None
            for path in common_paths:
                ollama_exe = os.path.join(path, "ollama.exe")
                if os.path.exists(ollama_exe):
                    ollama_path = path
                    break

            if ollama_path:
                current_path = os.environ.get("PATH", "")
                if ollama_path not in current_path:
                    os.environ["PATH"] = f"{ollama_path};{current_path}"
                    logger.debug(f"Adicionado {ollama_path} ao PATH")

        except Exception as e:
            logger.debug(f"Erro ao adicionar Ollama ao PATH: {e}")

    def _start_ollama_service(self) -> bool:
        """Inicia o serviço Ollama."""
        try:
            logger.info("Iniciando serviço Ollama...")

            subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            for i in range(SERVICE_TIMEOUT):
                if self._is_service_running():
                    logger.info("Serviço Ollama iniciado com sucesso")
                    return True
                time.sleep(1)

                if i % 10 == 0:
                    logger.debug(
                        f"Aguardando serviço Ollama iniciar... ({i}s/{SERVICE_TIMEOUT}s)")

            logger.error("Timeout ao aguardar serviço Ollama iniciar")
            return False

        except Exception as e:
            logger.exception(f"Erro ao iniciar serviço Ollama: {e}")
            return False

    def _pull_model(self, model_name: str) -> bool:
        """Faz o download de um modelo específico."""
        try:
            logger.info(f"Iniciando download do modelo {model_name}...")

            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                errors='replace'
            )

            if process.stdout:
                for line in process.stdout:
                    line = line.strip()
                    if line:
                        logger.info(f"Ollama: {line}")

            return_code = process.wait()

            if return_code == 0:
                logger.info(f"Modelo {model_name} baixado com sucesso!")
                return True
            else:
                logger.error(
                    f"Falha no download do modelo (código: {return_code})")
                return False

        except Exception as e:
            logger.exception(f"Erro no download do modelo {model_name}: {e}")
            return False


def ensure_ollama_ready() -> bool:
    """
    Função de conveniência para garantir que o Ollama esteja pronto.

    Returns:
        bool: True se o Ollama estiver configurado e pronto para uso
    """
    manager = OllamaManager()
    return manager.ensure_ollama_ready()


def wait_for_ollama_service(timeout: float = 60.0, check_interval: float = 0.5, url: str = OLLAMA_URL) -> bool:
    """
    Aguarda o serviço Ollama ficar disponível.

    Args:
        timeout: Tempo limite em segundos
        check_interval: Intervalo entre verificações em segundos  
        url: URL do serviço Ollama

    Returns:
        bool: True se o serviço estiver disponível, False se timeout
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/api/version", timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(check_interval)
    return False

from .logging_config import get_logger
from .get_settings import get_settings
from .ollama_manager import ensure_ollama_ready
from pathlib import Path
from utils import get_root_path
import speech_recognition as sr
import time
import requests

logger = get_logger(__name__)


def validate_user_environment() -> bool:
    """
    Validate that all required files and directories exist and that valid input devices are available.

    Returns:
        bool: True if environment is valid
    """
    try:
        root_path = get_root_path()
        modules_dir = Path(root_path + "binaries")
        if not modules_dir.exists():
            logger.error(
                f"Diretório de binários não encontrado: {modules_dir.absolute()}")
            return False

        notification_sound = Path(root_path + "assets/notification.mp3")
        if not notification_sound.exists():
            logger.warning(
                f"Som de notificação não encontrado: {notification_sound.absolute()}")

        prompts_dir = Path(root_path + "prompts")
        if not prompts_dir.exists():
            logger.error(
                f"Diretório de prompts não encontrado: {prompts_dir.absolute()}")
            return False

        if not validate_input_devices():
            logger.error("Nenhum dispositivo de entrada válido encontrado")
            return False

        settings = get_settings()
        provider = (settings or {}).get("llm_provider", "ollama").lower()
        if provider == "ollama":
            if not ensure_ollama_ready():
                logger.error("Falha ao configurar Ollama e modelo necessário")
                return False
        else:
            logger.info(
                "Provedor LLM configurado como OpenAI; pulando preparação do Ollama.")

        logger.info("Validação do ambiente concluída com sucesso")
        return True

    except Exception as e:
        logger.exception(f"Erro ao validar ambiente: {e}")
        return False


def validate_input_devices() -> bool:
    """
    Validate that at least one audio input device (microphone) is available.

    Returns:
        bool: True if at least one input device is available
    """
    try:
        mic_list = sr.Microphone.list_microphone_names()

        if not mic_list:
            logger.error("Nenhum microfone encontrado no sistema")
            return False

        try:
            with sr.Microphone() as _:
                logger.info("Teste de acesso ao microfone bem-sucedido")
                return True
        except Exception as mic_error:
            logger.exception(f"Falha ao acessar microfone: {mic_error}")
            return False

    except Exception as e:
        logger.exception(f"Erro ao verificar dispositivos de entrada: {e}")
        return False

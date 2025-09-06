from .logging_config import get_logger
from pathlib import Path
import subprocess
from .find_best_exe import find_best_exe

logger = get_logger(__name__)


def exec_ahk_command(cmd: dict, modules_dir: Path):
    """
    Execute a single AutoHotkey command.

    Args:
        cmd (dict): Command to execute
        modules_dir (Path): Path to modules directory

    Returns:
        bool: True if command executed successfully
    """
    try:
        script_name = cmd.get("script", "")
        params = cmd.get("params", [])
        app_name = None

        if '--app' in params:
            app_name = params[params.index('--app') + 1]

        if not script_name:
            error_msg = "Comando está faltando nome do script"
            logger.error(error_msg)
            return error_msg

        script_path = modules_dir / script_name
        if not script_path.exists():
            error_msg = f"Script não encontrado: {script_path}"
            logger.error(error_msg)
            return error_msg

        call_params = [str(script_path)] + [str(p) for p in params]
        logger.info(f"Executando comando: {' '.join(call_params)}")
        result = subprocess.run(call_params, shell=True,
                                capture_output=True, text=True)

        if (result.returncode != 0 and app_name):
            logger.info(
                f"Falha ao executar app do caminho simples, tentando com exe melhorado.")
            improved_exe = find_best_exe(app_name, verbose=False)
            if (not improved_exe):
                error_msg = f"Falha ao encontrar exe melhorado para {app_name}, execução do app falhou completamente."
                logger.error(error_msg)
                return error_msg

            call_params[call_params.index('--app') + 1] = str(improved_exe)
            logger.info(f"Executando comando: {' '.join(call_params)}")
            result = subprocess.run(call_params, shell=True,
                                    capture_output=True, text=True)
            return result.stdout

        logger.info(f"Comando executado com sucesso: {script_name}")
        return result.stdout

    except Exception as e:
        logger.exception(f"Erro ao executar comando {cmd}: {e}")
        return f"Erro ao executar comando {cmd}: {e}"


if __name__ == "__main__":
    cmd = {
        "script": "app_is_easy_to_find.ahk",
        "params": ["--app", "aaa"]
    }

    exec_ahk_command(cmd, Path(
        "C:\\Users\\verdant\\projects\\os-assistant\\modules"))

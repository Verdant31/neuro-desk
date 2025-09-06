import logging
from pathlib import Path
from typing import Optional
# Import update_health_status for health check updates
from health_check import update_health_status


class LoggerWrapper:
    def __init__(self, logger):
        self.logger = logger

    def info(self, msg, *args, update_health_check: Optional[dict] = None, **kwargs):
        self.logger.info(msg, *args, **kwargs)
        if update_health_check:
            if 'message' not in update_health_check or not update_health_check['message']:
                update_health_check = {
                    **update_health_check, 'message': str(msg)}
            update_health_status(**update_health_check)

    def warning(self, msg, *args, update_health_check: Optional[dict] = None, **kwargs):
        self.logger.warning(msg, *args, **kwargs)
        if update_health_check:
            if 'message' not in update_health_check or not update_health_check['message']:
                update_health_check = {
                    **update_health_check, 'message': str(msg)}
            update_health_status(**update_health_check)

    def error(self, msg, *args, update_health_check: Optional[dict] = None, **kwargs):
        self.logger.error(msg, *args, **kwargs)
        if update_health_check:
            if 'message' not in update_health_check or not update_health_check['message']:
                update_health_check = {
                    **update_health_check, 'message': str(msg)}
            update_health_status(**update_health_check)

    def exception(self, msg, *args, update_health_check: Optional[dict] = None, **kwargs):
        self.logger.exception(msg, *args, **kwargs)
        if update_health_check:
            if 'message' not in update_health_check or not update_health_check['message']:
                update_health_check = {
                    **update_health_check, 'message': str(msg)}
            update_health_status(**update_health_check)

    def __getattr__(self, attr):
        return getattr(self.logger, attr)


def setup_logging(root_path: str, log_level: str = "INFO", log_file: str = "os_assistant.log") -> None:
    """
    Setup centralized logging configuration for the OS Assistant.

    Args:
        log_level (str): Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str): Name of the log file
    """
    log_dir = Path(root_path + "logs")
    log_dir.mkdir(exist_ok=True)

    log_file_path = log_dir / log_file

    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_path, encoding='utf-8')
        ],
        force=True
    )

    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging configurado - Nível: {log_level}, Arquivo: {log_file_path}")


def get_logger(name: str) -> LoggerWrapper:
    """
    Get a logger instance with the given name, wrapped to support health check updates.
    """
    return LoggerWrapper(logging.getLogger(name))

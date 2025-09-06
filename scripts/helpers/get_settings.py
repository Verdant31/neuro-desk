import json
from pathlib import Path
from typing import Dict, Any

from .config import get_root_path
from .logging_config import get_logger

logger = get_logger(__name__)


def get_settings() -> Dict[str, Any]:
    """
    Loads and returns the application settings from the settings.json file, or returns default settings if the file is missing or invalid.

    No arguments.

    Returns:
        Dict[str, Any]: Dictionary containing application settings.
    """
    root_path = get_root_path()
    settings_file = Path(root_path + 'settings.json')

    default_settings = {
        "wake_phrase": "ola jarvis",
        "execution_plans": [],
        "chrome_profiles": [],
        "llm_provider": "ollama",
        "llm_model": None,
        "openai_api_key": None,
        "openai_base_url": None
    }

    try:
        if not settings_file.exists():
            logger.warning(
                f"Arquivo de configurações não encontrado em {settings_file.absolute()}. Usando configurações padrão.")
            return default_settings

        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        merged_settings = {**default_settings, **settings}

        logger.info("Configurações carregadas com sucesso")
        return merged_settings

    except json.JSONDecodeError as e:
        logger.error(
            f"Erro ao analisar settings.json: {e}. Usando configurações padrão.")
        return default_settings
    except Exception as e:
        logger.exception(
            f"Erro inesperado ao carregar configurações: {e}. Usando configurações padrão.")
        return default_settings

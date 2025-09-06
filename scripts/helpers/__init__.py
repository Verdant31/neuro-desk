"""
Módulo helpers para OS Assistant.

Este módulo contém funções auxiliares e utilitários para o funcionamento
do OS Assistant, incluindo configurações, logging, validações e outros helpers.
"""

# Importações principais que serão disponibilizadas no módulo
from .config import get_root_path
from .get_settings import get_settings
from .logging_config import setup_logging, get_logger
from .auth_validator import validate_script_access
from .validate_user_enviroment import validate_user_environment
from .run_startup_plans import run_startup_plans
from .exec_ahk_command import exec_ahk_command
from .validate_agent_output import validate_agent_output
from .find_best_exe import find_best_exe
from .ollama_manager import OllamaManager

__all__ = [
    'get_root_path',
    'get_settings',
    'setup_logging',
    'get_logger',
    'validate_script_access',
    'validate_user_environment',
    'run_startup_plans',
    'exec_ahk_command',
    'validate_agent_output',
    'find_best_exe',
    'OllamaManager'
]

__version__ = '1.0.0'
__author__ = 'OS Assistant Team'

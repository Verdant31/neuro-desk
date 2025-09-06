from .get_settings import get_settings
from .logging_config import get_logger
from .config import get_root_path
import psutil
import json
settings = get_settings()

root_path = get_root_path()
logger = get_logger(__name__)


def is_first_run_since_boot():
    return True
    boot_time = int(psutil.boot_time())
    last_boot_time = settings.get('last_boot_time')

    if last_boot_time == boot_time:
        return False
    settings['last_boot_time'] = boot_time

    with open(root_path + 'settings.json', 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)
    return True


def run_startup_plans(executor):
    is_first_run = is_first_run_since_boot()
    if (not is_first_run):
        logger.info(
            "Planos de inicialização já executados para esta inicialização.")
        return

    startup_plans = [plan for plan in settings.get(
        'execution_plans', []) if plan.get('run_on_startup') == True]

    for plan in startup_plans:
        logger.info(
            f"Executando plano de execução de inicialização: {plan.get('name')}")
        user_request = f'Execute action plan named "{plan['name']}"'
        executor.run(data={'input': user_request})

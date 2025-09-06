from assistant import Assistant
from executor import Executor
from utils import initiate_shutdown, shutdown_listener, normalize_text
from helpers import get_settings, validate_user_environment, validate_script_access, setup_logging, get_logger, run_startup_plans, get_root_path
from playsound import playsound
import os
import threading
from health_check import start_health_server

root_path = get_root_path()

setup_logging(root_path, log_level="DEBUG")
logger = get_logger(__name__)


def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    logger.info("Iniciando OS Assistant...")

    health_server = start_health_server()
    if not health_server:
        logger.error("Falha ao iniciar servidor de saúde. Encerrando.")
        return

    logger.info("OS Assistant está iniciando...", update_health_check=({
        "status": "starting", "message": "OS Assistant está iniciando..."
    }))

    if not validate_user_environment():
        logger.error("Validação do ambiente falhou. Encerrando.",
                     update_health_check=({"status": "offline"}))
        return

    try:
        settings = get_settings()
        assistant = Assistant(wake_phrase=settings['wake_phrase'])
        executor = Executor(mode="manual")

        logger.info("OS Assistant inicializado com sucesso", update_health_check=({
            "status": "running", "message": "OS Assistant está rodando e escutando pela frase de ativação"
        }))

    except Exception as e:
        logger.exception(f"Erro inesperado no loop principal: {e}", update_health_check=(
            {"status": "offline"}))
        return

    listener_thread = threading.Thread(
        target=shutdown_listener, args=(initiate_shutdown,), daemon=True)
    listener_thread.start()

    run_startup_plans(executor)

    while True:
        try:
            captured_text = assistant.listen()
            if not captured_text:
                continue

            normalized_text = normalize_text(captured_text)

            if normalized_text == "encerrar":
                logger.info("Comando de saída recebido. Encerrando.", update_health_check=(
                    {"status": "offline"}))
                break

            if assistant.check_wake(normalized_text):
                logger.info(
                    "Frase de ativação detectada! Processando solicitação do usuário.")
                playsound(root_path + "assets/notification.mp3")

                user_request = assistant.listen_with_timeout(
                    timeout_seconds=10)

                if not user_request:
                    logger.debug(
                        "Nenhuma solicitação do usuário detectada em 10 segundos, retornando à escuta da frase de ativação...")
                    continue

                logger.info(f"Solicitação do usuário: {user_request}")
                executor.run(data={'input': user_request})

            else:
                logger.debug("Escutando pela frase de ativação...")

        except KeyboardInterrupt:
            logger.info("Interrompido pelo usuário. Encerrando.")
            break
        except Exception as e:
            logger.exception(f"Erro inesperado no loop principal: {e}", update_health_check=(
                {"status": "offline"}))


if __name__ == "__main__":
    main()

from typing import Any
from helpers.logging_config import get_logger

logger = get_logger(__name__)


def validate_agent_output(result: dict[str, Any]):
    steps = result.get('intermediate_steps', [])
    seen = set()

    for step in steps:
        log_str = step[0].log.replace(
            "\n", " ").replace("\r", " ")
        logger.info(log_str)
        tool_call = str(step)
        if tool_call in seen:
            logger.warning(
                f"Chamada de ferramenta repetida detectada: {tool_call}")
        else:
            seen.add(tool_call)
    if 'output' in result:
        if 'Agent stopped due to max iterations' in result['output']:
            logger.warning(
                "Agente parou devido ao máximo de iterações - considere aumentar max_iterations")
        elif 'Agent stopped due to' in result['output']:
            logger.warning(
                f"Agente parou cedo: {result['output']}")
        else:
            logger.info("Agente completou tarefa com sucesso")

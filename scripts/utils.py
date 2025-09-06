import unicodedata
import re
import json
import os
import dotenv
import string
import re
from typing import Optional, Dict, Any, List
from helpers import get_logger, get_root_path
import socket

dotenv.load_dotenv()
logger = get_logger(__name__)


def get_api_url():
    root_path = get_root_path()
    if ("resources" in root_path):
        return "https://os-assistant-landing.vercel.app"

    return "http://localhost:3000"


def shutdown_listener(shutdown_callback, port=5001):
    """
    Listens for shutdown commands on a local TCP port and triggers the provided callback when a shutdown command is received.

    Args:
        shutdown_callback (callable): Function to call when a shutdown command is received.
        port (int, optional): TCP port to listen on. Defaults to 5001.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('127.0.0.1', port))
        s.listen(1)
        while True:
            conn, _ = s.accept()
            with conn:
                data = conn.recv(1024)
                if data == b"shutdown":
                    shutdown_callback()


def initiate_shutdown():
    """
    Immediately stops the OS Assistant process.
    No arguments.
    """
    logger.info("Sistema foi encerrado pelo cliente.",
                update_health_check=({"status": "offline"}))
    os._exit(0)


def get_custom_apps_paths(settings: Dict[str, Any]):
    """
    Returns a formatted string listing all custom applications from the settings.

    Args:
        settings (Dict[str, Any]): Settings dictionary containing a 'custom_apps' key.

    Returns:
        str: Formatted string listing custom app names and their executable paths.
    """
    app_paths = settings.get("custom_apps", [])
    app_paths_str = "\n".join([
        f"- {entry.get('name', '')}: {entry.get('exe_path', '')}" for entry in app_paths
    ]) if app_paths else "(none)"

    return app_paths_str


def get_execution_plans_str(settings: Dict[str, Any]):
    """
    Returns a formatted string describing all execution plans from the settings.

    Args:
        settings (Dict[str, Any]): Settings dictionary containing an 'execution_plans' key.

    Returns:
        str: Formatted string listing execution plans and their actions.
    """
    execution_plans = settings.get("execution_plans", [])
    if not execution_plans:
        return "(none)"

    plans_str = []
    for plan in execution_plans:
        plan_name = plan.get('name', '')
        actions = plan.get('actions', [])

        if not actions:
            plans_str.append(f"- {plan_name}: (no actions)")
            continue

        action_details = []
        for i, action in enumerate(actions, 1):
            action_type = action.get('action_type', 'unknown')
            target = action.get('target', '')
            position = action.get('position', '')
            monitor_index = action.get('monitor_index', '')

            details = f"{action_type}"
            if target:
                details += f" target={target}"
            if position:
                details += f" position={position}"
            if monitor_index is not None:
                details += f" monitor={monitor_index}"

            action_details.append(f"  {i}. {details}")

        plans_str.append(f"- {plan_name}:")
        plans_str.extend(action_details)

    return "\n".join(plans_str)


def parse_cmd_params_to_dict(cmd_params: List[str]) -> Dict[str, Any]:
    """
    Parses command parameters from an array of strings into a dictionary.

    Args:
        cmd_params (List[str]): List of command-line arguments like ['--app', 'path/to/app.exe']

    Returns:
        Dict[str, Any]: Dictionary with keys as parameter names (without --) and values as their corresponding values
    """
    result = {}
    i = 0

    while i < len(cmd_params):
        arg = cmd_params[i]
        if arg.startswith('--'):
            param_name = arg[2:]
            if i + 1 < len(cmd_params) and not cmd_params[i + 1].startswith('--'):
                result[param_name] = cmd_params[i + 1]
                i += 2
            else:
                result[param_name] = True
                i += 1
        else:
            i += 1

    return result


def parse_json_params_to_dict(cmd_params: str) -> Dict[str, Any]:
    """
    Parses the command parameters string (JSON format) into a dictionary.
    This is kept for backward compatibility.
    """
    return json.loads(cmd_params)


def parse_llm_output(ai_msg: str) -> Optional[Dict[str, Any]]:
    """
    Parses the output from the LLM to extract JSON data.

    Args:
        ai_msg (str): The message content from the LLM.

    Returns:
        dict or None: Parsed JSON object if found, otherwise None.
    """
    try:
        match = re.search(r"```json\s*(\{.*?\})\s*```", ai_msg, re.DOTALL)
        if match:
            json_str = match.group(1)
            parsed = json.loads(json_str)
            return parsed
        else:
            logger.warning("Nenhum JSON válido encontrado na saída do LLM")
            return None
    except json.JSONDecodeError as e:
        logger.error(f"Falha ao analisar JSON da saída do LLM: {e}")
        return None
    except Exception as e:
        logger.exception(f"Erro inesperado ao analisar saída do LLM: {e}")
        return None


def normalize_text(text: str) -> str:
    """
    Normalizes text by removing accents, non-alphanumeric characters, and converting to lowercase.

    Args:
        text (str): The input text to normalize.

    Returns:
        str: Normalized text.
    """
    try:
        if not text:
            return ""

        text = unicodedata.normalize('NFD', text)
        text = text.encode('ascii', 'ignore').decode('utf-8')
        text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
        normalized = text.strip().lower()
        return normalized
    except Exception as e:
        logger.exception(f"Erro ao normalizar texto '{text}': {e}")
        return text.lower() if text else ""


def get_all_drives() -> list:
    """
    Returns a list of all available drive root paths (Windows only).

    Returns:
        list: List of drive root paths.
    """
    try:
        drives = []
        for letter in string.ascii_uppercase:
            drive = f"{letter}:\\"
            if os.path.exists(drive):
                drives.append(drive)
        return drives
    except Exception as e:
        logger.exception(f"Erro ao obter drives: {e}")
        return []


def token_overlap_score(a: str, b: str) -> float:
    """
    Calculates the token-based overlap score (Jaccard index) between two strings.

    Args:
        a (str): First string.
        b (str): Second string.

    Returns:
        float: Jaccard index score.
    """
    try:
        if not a or not b:
            return 0.0

        a_tokens = set(re.findall(r'\w+', a.lower()))
        b_tokens = set(re.findall(r'\w+', b.lower()))

        if not a_tokens or not b_tokens:
            return 0.0

        score = len(a_tokens & b_tokens) / len(a_tokens | b_tokens)
        return score
    except Exception as e:
        logger.exception(f"Erro ao calcular sobreposição de tokens: {e}")
        return 0.0


def parse_args_to_dict(args_list):
    """
    Parse command-line arguments in --param value format into a dictionary.

    Args:
        args_list (list): List of arguments like ['--app', 'path/to/app.exe', '--param', 'value']

    Returns:
        dict: Dictionary with keys as parameter names (without --) and values as their corresponding values

    Example:
        >>> parse_args_to_dict(['--app', 'C:\\path\\to\\app.exe', '--timeout', '30'])
        {'app': 'C:\\path\\to\\app.exe', 'timeout': '30'}
    """
    result = {}
    i = 0

    while i < len(args_list):
        arg = args_list[i]

        # Check if it's a parameter (starts with --)
        if arg.startswith('--'):
            param_name = arg[2:]  # Remove the -- prefix

            # Check if there's a value after this parameter
            if i + 1 < len(args_list) and not args_list[i + 1].startswith('--'):
                # Next argument is the value
                result[param_name] = args_list[i + 1]
                i += 2  # Skip both parameter and value
            else:
                # Parameter with no value (boolean flag)
                result[param_name] = True
                i += 1
        else:
            # Skip arguments that don't start with --
            i += 1

    return result


# Example usage and test
if __name__ == "__main__":
    # Test cases
    test_args = [
        '--app', 'C:\\Users\\verdant\\AppData\\Local\\Microsoft\\WindowsApps\\Spotify.exe',
        '--timeout', '30',
        '--verbose',
        '--output', 'C:\\temp\\output.txt'
    ]

    result = parse_args_to_dict(test_args)
    print("Parsed arguments:")
    for key, value in result.items():
        print(f"  {key}: {value}")

    # Expected output:
    # app: C:\Users\verdant\AppData\Local\Microsoft\WindowsApps\Spotify.exe
    # timeout: 30
    # verbose: True
    # output: C:\temp\output.txt

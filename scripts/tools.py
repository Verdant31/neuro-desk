from pathlib import Path
from helpers import exec_ahk_command, get_settings, get_root_path
from langchain_core.tools import tool
from rapidfuzz import fuzz
import pyaudio
import re
import unicodedata
from typing import Mapping, Any

settings = get_settings()
root_path = get_root_path()
MODULES_DIR = Path(root_path+"/binaries")


@tool
def launch_app(app_name_or_exe: str) -> str:
    """
    Launches a program if it is not already open and focuses its window. If already open, just focuses the existing window.

    Parameters:
        app_name_or_exe (str): Name of the application or window (e.g., 'chrome', 'vscode', 'spotify').
            - Accepts simplified names or executables.

    Notes:
    - This command should be called before any window manipulation (move, maximize, etc.).
    - For Chrome, use 'chrome'.
    - Automatically normalizes application names.
    """
    cmd = {
        "script": "launch_app.exe",
        "params": ["--app", app_name_or_exe]
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def move_window(app: str, position: str = "Maximized", monitor_index: int = 1, title: str = "") -> str:
    """
    Moves an application's window to a specific position (Top, Bottom, Left, Right, Maximized) on a target monitor.

    Parameters:
        app (str): Name of the application or window (required).
        position (str): Window position. Accepted values: "Top", "Bottom", "Left", "Right", "Maximized" (default: "Maximized").
        monitor_index (int): Target monitor index (default: 1).
        title (str): Specific window title (optional, used ONLY for Chrome when there are multiple windows).

    Special behavior for Chrome:
    - If there are multiple Chrome windows:
        - If 'title' is provided, searches for a window containing that title.
        - If not, uses the first window found.
    - For other programs, always uses the first window found.

    Notes:
    - If 'position' is not provided, the window will be maximized by default.
    - If 'monitor_index' is not provided, the primary monitor (1) will be used.
    - Automatically normalizes application and title names.
    """
    params = ["--app", app, "--position", position,
              "--monitor_index", str(monitor_index)]
    if title:
        params += ["--title", title]
    cmd = {
        "script": "move_window.exe",
        "params": params
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def monitor_control(action: str, monitor: int) -> str:
    """
    Enables or disables a specific monitor.

    Parameters:
        action (str): "enable" to enable, "disable" to disable.
        monitor (int): Number of the monitor to control (starts at 1).

    Notes:
    - Useful for multi-monitor setups.
    - The primary monitor is usually 1.
    """
    cmd = {
        "script": "monitor_control.exe",
        "params": ["--action", action, "--monitor", str(monitor)]
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def update_app_volume(action: str, value: int = 5, app: str = "") -> str:
    """
    Increases or decreases the system volume or the volume of a specific application.

    Parameters:
        action (str): "aumentar" to increase, "diminuir" to decrease.
        value (int): Change value (1-100, default: 5).
        app (str): Executable name (optional; if not provided, adjusts the system volume).

    Notes:
    - If 'app' is not provided, adjusts the global system volume.
    - Automatically normalizes application names.
    """
    params = ["--action", action, "--value", str(value)]
    if app:
        params += ["--app", app]
    cmd = {
        "script": "update_app_volume.exe",
        "params": params
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def close_app(app: str) -> str:
    """
    Closes the window of a specified application (sends WM_CLOSE).

    Parameters:
        app (str): Name of the application or window (required).

    Notes:
    - Automatically normalizes application names.
    """
    cmd = {
        "script": "close_app.exe",
        "params": ["--app", app]
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def split_screen(left: str, right: str, monitor: int = 1) -> str:
    """
    Splits the specified monitor into two halves and positions two applications side by side.

    Parameters:
        left (str): Name of the application/window on the left (required).
        right (str): Name of the application/window on the right (required).
        monitor (int): Monitor index (default: 1).

    Notes:
    - Useful for productivity and window organization.
    - Automatically normalizes application names.
    """
    params = ["--left", left, "--right", right, "--monitor", str(monitor)]
    cmd = {
        "script": "split_screen.exe",
        "params": params
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def launch_chrome(profile: str = "", tabs: str = "") -> str:
    """
    Opens Google Chrome with a specific profile and/or with defined tabs.

    Parameters:
        profile (str): Chrome profile name (optional; if not provided, uses the first from settings.json).
        tabs (list): List of URLs to open in tabs (optional; format: ['url1','url2']).
            - Must be passed as a JSON string with single quotes inside.

    Notes:
    - If no profile is provided, uses the default.
    - If 'tabs' is provided, opens the URLs in new tabs.
    - Automatically normalizes profile names.
    """
    if tabs is None:
        tabs = []
    params = []
    if profile:
        params += ["--profile", profile]
    if tabs:
        params += ["--tabs", str(tabs)]
    cmd = {
        "script": "launch_chrome.exe",
        "params": params
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def shutdown() -> str:
    """
    Shuts down the computer with optional delay and custom message.

    Parameters:
        delay (int): Delay in seconds (default: 30).
        message (str): Custom message (optional).

    Notes:
    - Useful for safe shutdown automations.
    - If no parameter is provided, uses defaults.
    """
    cmd = {
        "script": "shutdown.exe",
        "params": []
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def min_app(app: str) -> str:
    """
    Minimizes the window of a specified application.

    Parameters:
        app (str): Name of the application or window (required).

    Notes:
    - Automatically normalizes application names.
    """
    cmd = {
        "script": "min.exe",
        "params": ["--app", app]
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def max_app(app: str) -> str:
    """
    Maximizes the window of a specified application.

    Parameters:
        app (str): Name of the application or window (required).

    Notes:
    - Automatically normalizes application names.
    """
    cmd = {
        "script": "max.exe",
        "params": ["--app", app]
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def install_requirements() -> str:
    """
    Installs required PowerShell modules for monitor control functionalities.

    Parameters:
        module (str): Module name (default: DisplayConfig).
        scope (str): Installation scope (default: CurrentUser).

    Notes:
    - Useful for preparing the environment for monitor automations.
    - Uses default values if no parameter is provided.
    """
    cmd = {
        "script": "install_requirements.exe",
        "params": []
    }
    return exec_ahk_command(cmd, MODULES_DIR)


@tool
def set_audio_input_device(input_name: str) -> str:
    """
    Sets the system's current active audio device to the provided input name.
    The provided name does not need to be exact; the closest match will be used.

    Parameters:
        input_name (str): Name (or partial name) of the desired audio input device.

    Returns:
        str: Result message indicating success or failure.

    """
    def normalize(s: str) -> str:
        if not isinstance(s, str):
            s = str(s)
        s = s.lower()
        s = unicodedata.normalize("NFD", s)
        s = "".join(ch for ch in s if unicodedata.category(ch)
                    != "Mn")
        s = re.sub(r"[\(\)\[\]\{\}]", " ", s)
        s = re.sub(r"[^a-z0-9\s]", " ", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s

    def device_type(info: Mapping[str, Any]) -> str:
        if info.get('maxOutputChannels', 0) > 0:
            return 'output'
        if info.get('maxInputChannels', 0) > 0:
            return 'input'
        return 'unknown'

    def lexical_bonus(name_norm: str) -> int:
        bonus = 0
        if "logitech" in name_norm:
            bonus += 5
        tokens = set(name_norm.split())
        if {"pro", "x"}.issubset(tokens):
            bonus += 5
        return bonus

    GENERIC_PENALTY = {"driver", "primary", "primario", "default",
                       "digital", "output", "saida", "saída", "spdif", "realtek"}

    def lexical_penalty(name_norm: str) -> int:
        tokens = set(name_norm.split())
        return -5 if tokens.intersection(GENERIC_PENALTY) else 0

    pa = pyaudio.PyAudio()
    devices = []
    try:
        for i in range(pa.get_device_count()):
            info = pa.get_device_info_by_index(i)
            name = str(info.get('name', '') or '')
            if not name:
                continue
            devices.append({
                'index': i,
                'name': name,
                'name_norm': normalize(name),
                'type': device_type(info),
                'raw': info,
            })
    finally:
        pa.terminate()

    if not devices:
        return 'Nenhum dispositivo de áudio encontrado.'

    candidates = [d for d in devices if d['type'] == 'output']
    if not candidates:
        candidates = devices[:]

    q = normalize(input_name)
    scores = []
    for d in candidates:
        r1 = fuzz.token_set_ratio(q, d['name_norm'])
        r2 = fuzz.partial_token_set_ratio(q, d['name_norm'])
        score = max(
            r1, r2) + lexical_bonus(d['name_norm']) + lexical_penalty(d['name_norm'])
        scores.append((score, d))

    if not scores:
        return f'Nenhum dispositivo de saída encontrado para "{input_name}".'

    scores.sort(key=lambda x: x[0], reverse=True)
    best_score, best = scores[0]

    if best_score < 60:
        return f'Nenhum dispositivo de saída suficientemente similar para "{input_name}".'

    best_name = best['name']
    cmd = {
        "script": "set_input_device.exe",
        "params": ["--input_name", best_name]
    }
    return exec_ahk_command(cmd, MODULES_DIR)

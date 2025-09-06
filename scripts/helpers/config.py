import os
import sys


def get_root_path():
    """
    Returns the absolute root path for resources:
    - If a 'resources' directory exists next to the executable/script, use it.
    - Otherwise, use the executable/script directory.
    Always returns a path ending with a separator.
    """
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resources_dir = os.path.join(base_dir, 'resources')
    if os.path.isdir(resources_dir):
        return os.path.join(resources_dir, '')
    return os.path.join(base_dir, '')

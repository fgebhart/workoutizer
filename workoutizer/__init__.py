import os
import subprocess
from pathlib import Path


def _get_version() -> str:
    cwd = Path.cwd()
    os.chdir(Path(__file__).parent.parent)
    try:
        cmd = ["python", "-W", "ignore", "setup.py", "-V"]
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        if not isinstance(out, str):
            out = out.decode("utf-8")
        version = out.strip()
    except Exception:
        version = "unknown"
    os.chdir(cwd)
    return version


__version__ = _get_version()

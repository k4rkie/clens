import os
from pathlib import Path

APP = "clens"


def _xdg(env: str, fallback: Path) -> Path:
    base = os.environ.get(env)
    return Path(base) if base else fallback


CONFIG_DIR = _xdg("XDG_CONFIG_HOME", Path.home() / ".config") / APP
DATA_DIR = _xdg("XDG_DATA_HOME", Path.home() / ".local/share") / APP
STATE_DIR = _xdg("XDG_STATE_HOME", Path.home() / ".local/state") / APP

_runtime = os.environ.get("XDG_RUNTIME_DIR")
RUNTIME_DIR = (Path(_runtime) if _runtime else STATE_DIR) / APP

CONFIG_FILE = CONFIG_DIR / "config.json"
STORE_DIR = DATA_DIR / "chroma"
LOG_FILE = STATE_DIR / "logs" / "clens.log"
RUNTIME_FILE = RUNTIME_DIR / "runtime.json"

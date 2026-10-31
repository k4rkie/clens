from pydantic import BaseModel
from pathlib import Path
from clens.paths import RUNTIME_FILE
import json
import os
import time
import requests

LOCAL_HOST = "127.0.0.1"


class RuntimeState(BaseModel):
    active_port: int | None = None
    pid: int | None = None

    @classmethod
    def load_runtime(cls, path: Path = RUNTIME_FILE) -> "RuntimeState":
        if not path.exists():
            return cls()
        try:
            with open(path, "r") as f:
                runtime_data = json.load(f)
            return cls.model_validate(runtime_data)
        except OSError, ValueError:
            return cls()

    def save_runtime(self, path: Path = RUNTIME_FILE) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_name(f"{path.name}.tmp")
        with open(tmp_path, "w") as f:
            f.write(self.model_dump_json(indent=2))
        os.replace(tmp_path, path)

    def clear_runtime(self, path: Path = RUNTIME_FILE) -> None:
        if not path.exists():
            return
        current = RuntimeState.load_runtime(path)
        if current.pid == self.pid:
            os.remove(path)

    def is_pid_running(self) -> bool:
        if self.pid is None:
            return False
        try:
            os.kill(self.pid, 0)
        except ProcessLookupError:
            return False
        except PermissionError:
            return True
        except OSError:
            return False
        return True

    def is_healthy(self, timeout: float) -> bool:
        if self.active_port is None:
            return False
        health_url = f"http://{LOCAL_HOST}:{self.active_port}/api/health"
        try:
            res = requests.get(health_url, timeout=timeout)
            return res.status_code == 200
        except requests.RequestException:
            return False

    def is_running(self, timeout: float = 1.0) -> bool:
        return self.is_pid_running() and self.is_healthy(timeout)

    def wait_until_running(self, deadline: float = 60.0, interval: float = 0.1) -> bool:
        if not self.is_pid_running():
            return False

        start_time = time.monotonic()
        while time.monotonic() - start_time < deadline:
            if not self.is_pid_running():
                return False
            if self.is_healthy(timeout=0.2):
                return True
            time.sleep(interval)
        return False

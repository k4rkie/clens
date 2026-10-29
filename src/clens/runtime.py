from pydantic import BaseModel, Field
from pathlib import Path
from clens.paths import RUNTIME_FILE
import json
import os


class RuntimeState(BaseModel):
    active_host: str | None = None
    active_port: str | None = None
    pid: int | None = None

    @classmethod
    def load_runtime(cls, path: Path = RUNTIME_FILE) -> "RuntimeState":
        if not path.exists():
            return cls()
        try:
            with open(path, "r") as f:
                runtime_data = json.load(f)
            return cls.model_validate(runtime_data)
        except:
            return cls()

    def save_runtime(self, path: Path = RUNTIME_FILE) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=2))

    def clear_runtime(self, path: Path = RUNTIME_FILE) -> None:
        if path.exists():
            os.remove(path)

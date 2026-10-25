from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from pathlib import Path
import json


class UserPreferences(BaseModel):
    default_host: str = "127.0.0.1"
    default_port: int = 8080


class RuntimeState(BaseModel):
    active_host: Optional[str] = None
    active_port: Optional[int] = None
    pid: Optional[int] = None


class AppConfig(BaseModel):
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    runtime: RuntimeState = Field(default_factory=RuntimeState)

    @classmethod
    def load_from_file(cls, path: Path) -> "AppConfig":
        if not path.exists():
            return cls()
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return cls.model_validate(data)
        except Exception:
            return cls()

    def save_to_file(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=2))

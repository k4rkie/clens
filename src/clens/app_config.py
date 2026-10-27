from pydantic import BaseModel, Field
from pathlib import Path
from clens.paths import CONFIG_FILE
import json


class UserPreferences(BaseModel):
    default_host: str = "127.0.0.1"
    default_port: int = 6969


class AppConfig(BaseModel):
    preferences: UserPreferences = Field(default_factory=UserPreferences)

    @classmethod
    def load_from_file(cls, path: Path = CONFIG_FILE) -> "AppConfig":
        if not path.exists():
            return cls()
        try:
            with open(path, "r") as f:
                data = json.load(f)
            return cls.model_validate(data)
        except Exception:
            return cls()

    def save_to_file(self, path: Path = CONFIG_FILE) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write(self.model_dump_json(indent=2))

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

from .bootstrap import default_db_path

@dataclass(frozen=True)
class AppConfig:
    mode: str
    db_path: str
    secret_key: Optional[str]

    @staticmethod
    def from_env(env: Mapping[str, str]) -> "AppConfig":
        mode = (env.get("APP_MODE") or "vuln").strip().lower()
        if mode not in {"vuln", "secure"}:
            mode = "vuln"

        db_path = env.get("DB_PATH") or default_db_path()
        secret_key = env.get("SECRET_KEY") or None
        return AppConfig(mode=mode, db_path=db_path, secret_key=secret_key)

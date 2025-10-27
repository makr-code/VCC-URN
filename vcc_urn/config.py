import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    # DB
    db_url: str = os.getenv("URN_DB_URL", f"sqlite:///{Path.cwd() / 'urn_manifest.db'}")
    # URN config
    nid: str = os.getenv("URN_NID", "de")
    # allowed state code pattern (lowercase)
    state_pattern: str = os.getenv("URN_STATE_RE", r"^[a-z]{2,3}$")

settings = Settings()
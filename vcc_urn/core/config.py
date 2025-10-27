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
    # CORS: comma separated list of origins, e.g. "http://localhost:3000,https://example.com"; "*" to allow all (dev only)
    cors_origins: str = os.getenv("URN_CORS_ORIGINS", "*")
    # Federation peers: map of state->base URL (without trailing slash), e.g. "nrw=https://nrw.example,by=https://by.example"
    peers: str = os.getenv("URN_PEERS", "")
    # Federation: request timeout seconds
    fed_timeout: float = float(os.getenv("URN_FED_TIMEOUT", "3.0"))
    # Federation cache TTL seconds
    fed_cache_ttl: int = int(os.getenv("URN_FED_CACHE_TTL", "300"))
    # Auth
    auth_mode: str = os.getenv("URN_AUTH_MODE", "none")  # none | apikey | oidc
    api_keys: str = os.getenv("URN_API_KEYS", "")  # comma-separated
    # OIDC (optional)
    oidc_issuer: str = os.getenv("URN_OIDC_ISSUER", "")
    oidc_audience: str = os.getenv("URN_OIDC_AUDIENCE", "")
    oidc_jwks_url: str = os.getenv("URN_OIDC_JWKS_URL", "")
    oidc_jwks_ttl: int = int(os.getenv("URN_OIDC_JWKS_TTL", "3600"))
    # Kataloge
    allowed_domains: str = os.getenv("URN_ALLOWED_DOMAINS", "")
    allowed_obj_types: str = os.getenv("URN_ALLOWED_OBJ_TYPES", "")
    catalogs_json: str = os.getenv("URN_CATALOGS_JSON", "")

settings = Settings()

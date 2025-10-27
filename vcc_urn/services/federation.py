import time
from typing import Dict, Optional
import httpx
from vcc_urn.config import settings

class TTLCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._data: Dict[str, tuple[float, dict]] = {}

    def get(self, key: str) -> Optional[dict]:
        now = time.time()
        entry = self._data.get(key)
        if not entry:
            return None
        expires_at, value = entry
        if expires_at < now:
            self._data.pop(key, None)
            return None
        return value

    def set(self, key: str, value: dict):
        self._data[key] = (time.time() + self.ttl, value)

_cache = TTLCache(ttl_seconds=settings.fed_cache_ttl)


def _parse_peers(peers_str: str) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    if not peers_str:
        return mapping
    for item in peers_str.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            continue
        state, base = item.split("=", 1)
        mapping[state.strip().lower()] = base.strip().rstrip("/")
    return mapping


def resolve_via_peer(urn: str, state: str) -> Optional[dict]:
    manifest = _cache.get(urn)
    if manifest:
        return manifest
    peers = _parse_peers(settings.peers)
    base = peers.get(state.lower())
    if not base:
        return None
    url = f"{base}/api/v1/resolve"
    try:
        with httpx.Client(timeout=settings.fed_timeout) as client:
            resp = client.get(url, params={"urn": urn})
            if resp.status_code == 200:
                data = resp.json()
                if isinstance(data, dict) and data.get("urn") == urn:
                    _cache.set(urn, data)
                    return data
    except Exception:
        return None
    return None

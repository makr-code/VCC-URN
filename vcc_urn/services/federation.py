import time
import logging
from typing import Dict, Optional
import httpx
from pybreaker import CircuitBreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from vcc_urn.config import settings

logger = logging.getLogger(__name__)


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

# Circuit breaker for federation requests (Phase 1)
# fail_max=5: Open circuit after 5 consecutive failures
# reset_timeout=60: Keep circuit open for 60 seconds before half-open
_circuit_breaker = CircuitBreaker(fail_max=5, reset_timeout=60, name="federation_resolver")


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


# Retry logic with exponential backoff (Phase 1)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
    reraise=True
)
def _fetch_from_peer(url: str, urn: str) -> Optional[dict]:
    """Fetch manifest from peer with retry logic"""
    with httpx.Client(timeout=settings.fed_timeout) as client:
        resp = client.get(url, params={"urn": urn})
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, dict) and data.get("urn") == urn:
                return data
    return None


def resolve_via_peer(urn: str, state: str) -> Optional[dict]:
    """
    Resolve URN via peer with circuit breaker and retry logic (Phase 1)
    """
    # Check cache first
    manifest = _cache.get(urn)
    if manifest:
        logger.info("Federation cache hit", extra={"urn": urn, "state": state})
        return manifest
    
    # Parse peers
    peers = _parse_peers(settings.peers)
    base = peers.get(state.lower())
    if not base:
        logger.debug("No peer configured for state", extra={"state": state})
        return None
    
    url = f"{base}/api/v1/resolve"
    
    try:
        # Use circuit breaker to prevent cascading failures
        @_circuit_breaker
        def fetch_with_breaker():
            return _fetch_from_peer(url, urn)
        
        data = fetch_with_breaker()
        if data:
            _cache.set(urn, data)
            logger.info("Federation resolved via peer", extra={
                "urn": urn,
                "state": state,
                "peer_url": base
            })
            return data
        else:
            logger.warning("Peer returned no data", extra={
                "urn": urn,
                "state": state,
                "peer_url": base
            })
    except Exception as e:
        logger.error("Federation request failed", extra={
            "urn": urn,
            "state": state,
            "peer_url": base,
            "error": str(e),
            "circuit_breaker_state": _circuit_breaker.current_state
        })
    
    return None

import time
import logging
from typing import Dict, Optional
import httpx
from pybreaker import CircuitBreaker
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from vcc_urn.config import settings
from vcc_urn.core.redis_cache import get_redis_cache

logger = logging.getLogger(__name__)


class TTLCache:
    """Fallback in-memory cache (used when Redis is disabled)"""
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


# Phase 2: Use Redis cache if enabled, otherwise fallback to TTL cache
_redis_cache = get_redis_cache()
_fallback_cache = TTLCache(ttl_seconds=settings.fed_cache_ttl)

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
    Resolve URN via peer with circuit breaker and retry logic (Phase 1+2)
    Uses Redis cache if enabled, otherwise in-memory TTL cache
    """
    # Check cache first (Redis or in-memory)
    manifest = _redis_cache.get(urn)
    if manifest:
        logger.info("Federation cache hit (Redis)", extra={"urn": urn, "state": state})
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
            # Store in Redis cache
            _redis_cache.set(urn, data, ttl=settings.fed_cache_ttl)
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


# Phase 2: Batch resolution
def resolve_batch(urns: list[str]) -> Dict[str, Optional[dict]]:
    """
    Resolve multiple URNs efficiently (batch operation)
    Returns dict mapping URN -> manifest (or None if not found)
    """
    results: Dict[str, Optional[dict]] = {}
    
    # Check cache first for all URNs
    for urn in urns:
        cached = _redis_cache.get(urn)
        if cached:
            results[urn] = cached
            logger.debug("Batch cache hit", extra={"urn": urn})
    
    # Find URNs not in cache
    uncached_urns = [urn for urn in urns if urn not in results]
    
    if not uncached_urns:
        return results
    
    # Group by state for efficient peer requests
    by_state: Dict[str, list[str]] = {}
    peers = _parse_peers(settings.peers)
    
    for urn in uncached_urns:
        try:
            # Extract state from URN (format: urn:de:STATE:...)
            parts = urn.split(":")
            if len(parts) >= 3:
                state = parts[2].lower()
                if state not in by_state:
                    by_state[state] = []
                by_state[state].append(urn)
        except Exception:
            results[urn] = None
    
    # Resolve each state's URNs
    for state, state_urns in by_state.items():
        base = peers.get(state)
        if not base:
            for urn in state_urns:
                results[urn] = None
            continue
        
        # Fetch each URN from peer (could be parallelized further)
        for urn in state_urns:
            manifest = resolve_via_peer(urn, state)
            results[urn] = manifest
    
    return results


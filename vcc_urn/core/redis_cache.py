"""
Redis cache integration for VCC-URN
Phase 2: Federation Evolution
"""
import json
import logging
from typing import Optional
from redis import Redis
from redis.exceptions import RedisError

from vcc_urn.core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis-based cache with fallback to in-memory cache if Redis is unavailable"""
    
    def __init__(self):
        self.client: Optional[Redis] = None
        self._memory_cache: dict = {}  # Fallback in-memory cache
        
        if settings.redis_enabled and settings.redis_url:
            try:
                self.client = Redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=2,
                    socket_timeout=2
                )
                # Test connection
                self.client.ping()
                logger.info("Redis cache connected", extra={"redis_url": settings.redis_url})
            except (RedisError, Exception) as e:
                logger.warning("Redis connection failed, using in-memory cache fallback", extra={"error": str(e)})
                self.client = None
        else:
            logger.info("Redis disabled, using in-memory cache")
    
    def get(self, key: str) -> Optional[dict]:
        """Get value from cache"""
        if self.client:
            try:
                value = self.client.get(key)
                if value:
                    return json.loads(value)
            except (RedisError, json.JSONDecodeError) as e:
                logger.error("Redis get failed", extra={"key": key, "error": str(e)})
                # Fall back to memory cache
                return self._memory_cache.get(key)
        return self._memory_cache.get(key)
    
    def set(self, key: str, value: dict, ttl: Optional[int] = None):
        """Set value in cache with optional TTL (seconds)"""
        ttl = ttl or settings.fed_cache_ttl
        
        if self.client:
            try:
                self.client.setex(key, ttl, json.dumps(value))
                logger.debug("Redis set successful", extra={"key": key, "ttl": ttl})
                return
            except (RedisError, json.JSONEncodeError) as e:
                logger.error("Redis set failed", extra={"key": key, "error": str(e)})
        
        # Fallback to memory cache (note: no TTL support in memory fallback)
        self._memory_cache[key] = value
    
    def delete(self, key: str):
        """Delete key from cache"""
        if self.client:
            try:
                self.client.delete(key)
                logger.debug("Redis delete successful", extra={"key": key})
            except RedisError as e:
                logger.error("Redis delete failed", extra={"key": key, "error": str(e)})
        
        self._memory_cache.pop(key, None)
    
    def clear_pattern(self, pattern: str):
        """Clear all keys matching pattern (e.g., 'urn:de:nrw:*')"""
        if self.client:
            try:
                keys = self.client.keys(pattern)
                if keys:
                    self.client.delete(*keys)
                    logger.info("Redis pattern cleared", extra={"pattern": pattern, "count": len(keys)})
            except RedisError as e:
                logger.error("Redis clear pattern failed", extra={"pattern": pattern, "error": str(e)})
        
        # For memory cache, filter keys
        keys_to_delete = [k for k in self._memory_cache.keys() if self._match_pattern(k, pattern)]
        for key in keys_to_delete:
            del self._memory_cache[key]
    
    @staticmethod
    def _match_pattern(key: str, pattern: str) -> bool:
        """Simple pattern matching for memory cache (supports * wildcard)"""
        if '*' not in pattern:
            return key == pattern
        parts = pattern.split('*')
        if len(parts) == 2:
            return key.startswith(parts[0]) and key.endswith(parts[1])
        return False
    
    def health_check(self) -> bool:
        """Check if Redis is healthy"""
        if not self.client:
            return True  # Memory cache is always "healthy"
        try:
            return self.client.ping()
        except RedisError:
            return False


# Global cache instance
_redis_cache: Optional[RedisCache] = None


def get_redis_cache() -> RedisCache:
    """Get or create Redis cache instance (singleton)"""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache

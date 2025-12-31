"""
Redis Configuration and Utilities
Async Redis client for caching, rate limiting, and session management.
"""

from typing import Optional, Any
import json
import redis.asyncio as redis
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)

# Redis connection pool
redis_pool: Optional[redis.Redis] = None


async def get_redis() -> redis.Redis:
    """Get Redis connection from pool."""
    global redis_pool
    
    if redis_pool is None:
        redis_pool = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True
        )
    
    return redis_pool


async def close_redis() -> None:
    """Close Redis connection pool."""
    global redis_pool
    
    if redis_pool is not None:
        await redis_pool.close()
        redis_pool = None
        logger.info("Redis connection pool closed")


async def check_redis_connection() -> bool:
    """Check Redis connectivity."""
    try:
        client = await get_redis()
        await client.ping()
        return True
    except Exception as e:
        logger.error("Redis connection check failed", error=str(e))
        return False


class RedisCache:
    """
    Redis-based caching utility with JSON serialization.
    """
    
    def __init__(self, prefix: str = "cache"):
        self.prefix = prefix
    
    def _make_key(self, key: str) -> str:
        """Generate prefixed key."""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            client = await get_redis()
            value = await client.get(self._make_key(key))
            
            if value is not None:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Cache get error", key=key, error=str(e))
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: int = 300  # 5 minutes default
    ) -> bool:
        """Set value in cache with expiration."""
        try:
            client = await get_redis()
            serialized = json.dumps(value)
            await client.setex(self._make_key(key), expire, serialized)
            return True
        except Exception as e:
            logger.error("Cache set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            client = await get_redis()
            await client.delete(self._make_key(key))
            return True
        except Exception as e:
            logger.error("Cache delete error", key=key, error=str(e))
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            client = await get_redis()
            return await client.exists(self._make_key(key)) > 0
        except Exception as e:
            logger.error("Cache exists error", key=key, error=str(e))
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment a counter in cache."""
        try:
            client = await get_redis()
            return await client.incrby(self._make_key(key), amount)
        except Exception as e:
            logger.error("Cache increment error", key=key, error=str(e))
            return 0


class RateLimiter:
    """
    Redis-based rate limiter using sliding window algorithm.
    """
    
    def __init__(self, prefix: str = "ratelimit"):
        self.prefix = prefix
    
    def _make_key(self, identifier: str, window: str) -> str:
        """Generate rate limit key."""
        return f"{self.prefix}:{window}:{identifier}"
    
    async def is_allowed(
        self,
        identifier: str,
        limit: int,
        window_seconds: int
    ) -> tuple[bool, int]:
        """
        Check if request is allowed under rate limit.
        Returns (is_allowed, remaining_requests).
        """
        try:
            client = await get_redis()
            key = self._make_key(identifier, str(window_seconds))
            
            # Get current count
            current = await client.get(key)
            current_count = int(current) if current else 0
            
            if current_count >= limit:
                return False, 0
            
            # Increment counter
            pipe = client.pipeline()
            pipe.incr(key)
            
            if current_count == 0:
                pipe.expire(key, window_seconds)
            
            await pipe.execute()
            
            remaining = limit - current_count - 1
            return True, remaining
            
        except Exception as e:
            logger.error("Rate limit check error", identifier=identifier, error=str(e))
            # Fail open - allow request if Redis fails
            return True, limit
    
    async def get_remaining(
        self,
        identifier: str,
        limit: int,
        window_seconds: int
    ) -> int:
        """Get remaining requests for identifier."""
        try:
            client = await get_redis()
            key = self._make_key(identifier, str(window_seconds))
            
            current = await client.get(key)
            current_count = int(current) if current else 0
            
            return max(0, limit - current_count)
        except Exception as e:
            logger.error("Rate limit remaining error", identifier=identifier, error=str(e))
            return limit


class SessionStore:
    """
    Redis-based session store for user sessions.
    """
    
    def __init__(self, prefix: str = "session"):
        self.prefix = prefix
        self.default_ttl = 86400  # 24 hours
    
    def _make_key(self, session_id: str) -> str:
        """Generate session key."""
        return f"{self.prefix}:{session_id}"
    
    async def create(
        self,
        session_id: str,
        data: dict,
        ttl: int = None
    ) -> bool:
        """Create a new session."""
        try:
            client = await get_redis()
            key = self._make_key(session_id)
            serialized = json.dumps(data)
            
            await client.setex(key, ttl or self.default_ttl, serialized)
            return True
        except Exception as e:
            logger.error("Session create error", session_id=session_id, error=str(e))
            return False
    
    async def get(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        try:
            client = await get_redis()
            key = self._make_key(session_id)
            
            value = await client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error("Session get error", session_id=session_id, error=str(e))
            return None
    
    async def update(self, session_id: str, data: dict) -> bool:
        """Update session data."""
        try:
            client = await get_redis()
            key = self._make_key(session_id)
            
            # Get current TTL
            ttl = await client.ttl(key)
            if ttl < 0:
                return False
            
            serialized = json.dumps(data)
            await client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error("Session update error", session_id=session_id, error=str(e))
            return False
    
    async def delete(self, session_id: str) -> bool:
        """Delete a session."""
        try:
            client = await get_redis()
            key = self._make_key(session_id)
            
            await client.delete(key)
            return True
        except Exception as e:
            logger.error("Session delete error", session_id=session_id, error=str(e))
            return False
    
    async def refresh(self, session_id: str, ttl: int = None) -> bool:
        """Refresh session TTL."""
        try:
            client = await get_redis()
            key = self._make_key(session_id)
            
            await client.expire(key, ttl or self.default_ttl)
            return True
        except Exception as e:
            logger.error("Session refresh error", session_id=session_id, error=str(e))
            return False


# Create global instances
cache = RedisCache()
rate_limiter = RateLimiter()
session_store = SessionStore()

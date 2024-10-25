# app/core/caching/decorators.py
from functools import wraps
from logging import getLogger
from typing import Callable


from app.core.models import redis_db_helper


logger = getLogger(__name__)


def memoize(ttl: int = 3600):
    """Decorator for memoizing function results using Redis."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not redis_db_helper.cache:
                logger.warning("Redis session was not initialized")
                pass

            if not redis_db_helper.cache:
                logger.warning(f"Cache miss due to disconnected Redis session")
                return await func(*args, **kwargs)

            # Generate a cache key
            key = await redis_db_helper.cache.generate_key(func, args, kwargs)

            # Try to retrieve the value from Redis
            cached_value = await redis_db_helper.cache.get(key)
            if cached_value is not None:
                logger.warning(f"Cache hit for key: {key}")
                return cached_value

            # Call the function and cache the result
            result = await func(*args, **kwargs)
            await redis_db_helper.cache.set(key, result, ttl=ttl)
            logger.warning(f"Cache set for key: {key}")
            return result

        return wrapper

    return decorator

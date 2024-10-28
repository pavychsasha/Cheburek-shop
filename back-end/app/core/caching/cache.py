import hashlib
import inspect
from logging import getLogger

import dill as pickle
from typing import Any, Callable, Dict, Tuple
from redis.asyncio import Redis

from sqlalchemy.ext.asyncio import AsyncSession

logger = getLogger(__name__)


class RedisCache:
    OMITTED_INSTANCES: tuple = (
        inspect.Signature.empty,
        AsyncSession,
    )

    def __init__(self, redis: Redis):
        self.redis = redis

    @classmethod
    async def generate_key(
        cls, func: Callable, args: Tuple[Any], kwargs: Dict[str, Any]
    ) -> bytes:

        module_name = inspect.getmodule(func).__name__
        sig = inspect.signature(func)

        bound = sig.bind_partial(*args, **kwargs)
        bound.apply_defaults()
        bound_args = {
            key: repr(value)
            for key, value in bound.arguments.items()
            if not isinstance(value, cls.OMITTED_INSTANCES)
        }
        bound_args = str(sorted(bound_args.items()))
        logger.warning(f"BOUND_ARGS: {bound_args}")

        """Generate a unique cache key based on the function, module name, and arguments."""
        key_data = f"{module_name}.{func.__name__}:{bound_args}"
        hashed_key = hashlib.md5(key_data.encode()).hexdigest()
        full_key = f"{module_name}.{__name__}:{hashed_key}"
        return full_key

    async def get(self, key: str) -> Any:
        """Retrieve a value from the Redis cache and deserialize it using pickle."""
        value = await self.redis.get(key)
        if value:
            return pickle.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 120) -> None:
        """Serialize a value using pickle and store it in the Redis cache with an optional TTL."""
        serialized_value = pickle.dumps(value)
        await self.redis.set(key, serialized_value, ex=ttl)

    async def invalidate(
        self,
        func: Callable,
        *args: Any,
        invalidate_all: bool = False,
        **kwargs: Dict[str, Any],
    ) -> None:
        """
        Invalidate cache for a specific function or its arguments.

        Args:
            func (Callable): The function whose cache should be invalidated.
            *args: Positional arguments used for generating the cache key.
            invalidate_all (bool): If True, invalidates all cache entries related to the function.
            **kwargs: Keyword arguments used for generating the cache key.
        """

        # If `invalidate_all` is specified, remove all keys related to the function.
        if invalidate_all:
            # Get the module and function name.
            module_name = inspect.getmodule(func).__name__
            func_name = func.__name__
            async for key in self.redis.scan_iter(f"{module_name}.{func_name}:*"):

                await self.redis.delete(key)
                logger.info(f"Invalidated cache for key: {key}")
            return

        # Generate the cache key for the specific arguments.
        key = await self.generate_key(func, args, kwargs)

        # Invalidate the specific cache entry.
        await self.redis.delete(key)
        logger.info(f"Invalidated cache for specific key: {key}")

    async def remove_all_cache_keys(self) -> None:
        """Remove all keys from the Redis cache."""
        async for key in self.redis.scan_iter("*"):
            await self.redis.delete(key)
            logger.info(f"Deleted cache key: {key}")
        logger.info("All cache keys have been removed.")

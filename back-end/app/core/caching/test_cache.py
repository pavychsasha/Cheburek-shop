import time
import pytest
import asyncio

from app.core.caching.decorators import memoize
from app.core.models import redis_db_helper


# Example method with memoization
@memoize(ttl=600)  # Assuming you have a memoize decorator.
async def some_method(a, b):
    # Simulate a slow operation
    await asyncio.sleep(2)
    return a + b


# Example method without memoization
async def some_method_without_cache(a, b):
    # Simulate the same slow operation
    await asyncio.sleep(2)
    return a + b


@pytest.mark.asyncio
async def test_execution_time():
    # Clear the cache before running tests.
    await redis_db_helper.connect()
    await redis_db_helper.cache.invalidate(some_method, b=2, a=1)

    # Test without cache
    start_time = time.time()
    result_without_cache = await some_method_without_cache(1, 2)
    time_without_cache = time.time() - start_time
    print(f"Execution time without cache: {time_without_cache:.4f} seconds")

    # Test with cache (first run to populate cache)
    start_time = time.time()
    result_with_cache_first = await some_method(1, 2)
    time_with_cache_first = time.time() - start_time
    print(f"Execution time with cache (first run): {time_with_cache_first:.4f} seconds")

    # Test with cache (second run to utilize cache)
    start_time = time.time()
    result_with_cache_second = await some_method(1, 2)
    time_with_cache_second = time.time() - start_time
    print(
        f"Execution time with cache (second run): {time_with_cache_second:.4f} seconds"
    )

    # Assertions to check that the results are the same
    assert result_without_cache == result_with_cache_first == result_with_cache_second

    # Assert that the second cached call is significantly faster
    assert time_with_cache_first >= time_without_cache
    assert time_with_cache_second < time_with_cache_first
    assert time_with_cache_second < 0.1  # Assuming cache retrieval should be very fast

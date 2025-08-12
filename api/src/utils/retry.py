import asyncio
from collections.abc import Callable
from functools import wraps
from typing import Any

from logger import get_logger

log = get_logger(__name__)


def async_retry(
    max_retries: int = 3,
    exceptions: type[Exception] | tuple = Exception,
    delay: float = 0,
    backoff: float = 1,
):
    """
    Async retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        exceptions: Exception type(s) to catch and retry on
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        log.error(f"All {max_retries} attempts failed for {func.__name__}: {str(e)}")
                        raise

                    log.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")

                    if current_delay > 0:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff

            # This should never be reached
            raise RuntimeError(f"Unexpected error in retry decorator for {func.__name__}")

        return wrapper
    return decorator


def sync_retry(
    max_retries: int = 3,
    exceptions: type[Exception] | tuple = Exception,
    delay: float = 0,
    backoff: float = 1,
):
    """
    Sync retry decorator with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        exceptions: Exception type(s) to catch and retry on
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == max_retries - 1:
                        log.error(f"All {max_retries} attempts failed for {func.__name__}: {str(e)}")
                        raise

                    log.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {str(e)}")

                    if current_delay > 0:
                        time.sleep(current_delay)
                        current_delay *= backoff

            # This should never be reached
            raise RuntimeError(f"Unexpected error in retry decorator for {func.__name__}")

        return wrapper
    return decorator

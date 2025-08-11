"""
Retry utilities for MCP Memory Server
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Type, Union, Tuple

logger = logging.getLogger(__name__)


def retry_async(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    Async retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Exception types to retry on
        on_retry: Callback function called on each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, re-raise the exception
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    # Log retry attempt
                    logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}/{max_attempts}: {e}. Retrying in {current_delay}s...")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")
                    
                    # Wait before retry
                    await asyncio.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    on_retry: Optional[Callable[[int, Exception], None]] = None
):
    """
    Synchronous retry decorator with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier for delay
        exceptions: Exception types to retry on
        on_retry: Callback function called on each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, re-raise the exception
                        logger.error(f"Function {func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    
                    # Log retry attempt
                    logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}/{max_attempts}: {e}. Retrying in {current_delay}s...")
                    
                    # Call retry callback if provided
                    if on_retry:
                        try:
                            on_retry(attempt + 1, e)
                        except Exception as callback_error:
                            logger.error(f"Retry callback failed: {callback_error}")
                    
                    # Wait before retry
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            
        return wrapper
    return decorator


class RetryConfig:
    """Configuration for retry behavior"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff = backoff
        self.max_delay = max_delay
        self.jitter = jitter
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt"""
        import random
        
        delay = self.delay * (self.backoff ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            delay *= (0.5 + random.random() * 0.5)
        
        return delay


async def retry_with_config(
    func: Callable,
    config: RetryConfig,
    exceptions: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    on_retry: Optional[Callable[[int, Exception], None]] = None,
    *args,
    **kwargs
) -> Any:
    """
    Retry function with custom configuration
    
    Args:
        func: Function to retry
        config: Retry configuration
        exceptions: Exception types to retry on
        on_retry: Callback function called on each retry
        *args: Arguments to pass to function
        **kwargs: Keyword arguments to pass to function
    """
    last_exception = None
    
    for attempt in range(config.max_attempts):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        except exceptions as e:
            last_exception = e
            
            if attempt == config.max_attempts - 1:
                # Last attempt, re-raise the exception
                logger.error(f"Function {func.__name__} failed after {config.max_attempts} attempts: {e}")
                raise
            
            # Calculate delay
            delay = config.get_delay(attempt)
            
            # Log retry attempt
            logger.warning(f"Function {func.__name__} failed on attempt {attempt + 1}/{config.max_attempts}: {e}. Retrying in {delay:.2f}s...")
            
            # Call retry callback if provided
            if on_retry:
                try:
                    on_retry(attempt + 1, e)
                except Exception as callback_error:
                    logger.error(f"Retry callback failed: {callback_error}")
            
            # Wait before retry
            if asyncio.iscoroutinefunction(func):
                await asyncio.sleep(delay)
            else:
                time.sleep(delay)
    
    # This should never be reached, but just in case
    if last_exception:
        raise last_exception

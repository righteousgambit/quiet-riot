#!/usr/bin/env python3
"""
Retry handler for AWS API calls with exponential backoff.
Handles throttling and transient errors appropriately.
"""

from functools import wraps
import logging
import time

from botocore.config import Config
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

# Retryable exceptions that should trigger retry logic
RETRYABLE_EXCEPTIONS = (
    ClientError,  # Generic client errors (may include throttling)
)

# Specific error codes that indicate throttling
THROTTLING_ERROR_CODES = (
    "Throttling",
    "ThrottlingException",
    "ThrottledException",
    "RequestThrottled",
    "TooManyRequestsException",
    "ServiceUnavailable",
    "SlowDown",
)

# Non-retryable exceptions (should fail immediately)
NON_RETRYABLE_EXCEPTIONS = (
    "InvalidParameterException",
    "ValidationException",
    "AccessDenied",
    "UnauthorizedOperation",
)


def is_retryable_exception(exception):
    """
    Determine if an exception is retryable.

    Args:
        exception: The exception to check

    Returns:
        bool: True if the exception is retryable
    """
    # Check for specific non-retryable error codes
    if isinstance(exception, ClientError):
        error_code = exception.response.get("Error", {}).get("Code", "")
        if error_code in NON_RETRYABLE_EXCEPTIONS:
            return False
        # Check for throttling errors
        if error_code in THROTTLING_ERROR_CODES:
            return True
        # Other client errors might be retryable
        return True

    # Check exception type
    return isinstance(exception, RETRYABLE_EXCEPTIONS)


def get_botocore_retry_config(max_attempts=7):
    """
    Create a botocore Config with retry settings.

    Args:
        max_attempts: Maximum number of retry attempts (default: 7)

    Returns:
        Config: Botocore configuration object
    """
    return Config(
        retries={
            "max_attempts": max_attempts,
            "mode": "adaptive",  # Adaptive retry mode handles throttling better
        }
    )


def retry_with_backoff(max_retries=3, base_delay=1.0, max_delay=60.0, exponential_base=2.0):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation

    Returns:
        Decorated function
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # Don't retry if it's not a retryable exception
                    if not is_retryable_exception(e):
                        logger.debug(f"Non-retryable exception in {func.__name__}: {e}")
                        raise

                    # Don't retry on last attempt
                    if attempt >= max_retries:
                        logger.warning(f"Max retries ({max_retries}) exceeded for {func.__name__}: {e}")
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(base_delay * (exponential_base**attempt), max_delay)

                    # Add jitter to prevent thundering herd
                    jitter = delay * 0.1 * (0.5 - __import__("random").random())
                    delay += jitter

                    logger.debug(
                        f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__} after {delay:.2f}s: {e}"
                    )
                    time.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper

    return decorator

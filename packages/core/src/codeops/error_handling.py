"""Advanced error handling for Espalha pipeline"""

import logging
import asyncio
from typing import Optional, Callable, Any, Coroutine
from functools import wraps
from enum import Enum
import traceback

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class EspalhaException(Exception):
    """Base exception for Espalha"""
    
    def __init__(self, message: str, severity: ErrorSeverity = ErrorSeverity.ERROR):
        self.message = message
        self.severity = severity
        super().__init__(message)


class FireCrawlException(EspalhaException):
    """FireCrawl specific exception"""
    pass


class ComfyUIException(EspalhaException):
    """ComfyUI specific exception"""
    pass


class ChromaDBException(EspalhaException):
    """ChromaDB specific exception"""
    pass


class Neo4jException(EspalhaException):
    """Neo4j specific exception"""
    pass


class ValidationException(EspalhaException):
    """Validation error"""
    pass


class ErrorHandler:
    """Advanced error handling with retry logic"""
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.errors = []
    
    async def retry_async(
        self,
        func: Callable[..., Coroutine],
        *args,
        on_error: Optional[Callable] = None,
        **kwargs
    ) -> Any:
        """
        Retry async function with exponential backoff
        
        Args:
            func: Async function to retry
            args: Function arguments
            on_error: Callback on error
            kwargs: Function keyword arguments
            
        Returns:
            Function result on success
            
        Raises:
            Exception: After max retries
        """
        last_exception = None
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} for {func.__name__}")
                return await func(*args, **kwargs)
                
            except Exception as e:
                last_exception = e
                self.errors.append({
                    "function": func.__name__,
                    "attempt": attempt + 1,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                })
                
                if on_error:
                    await on_error(e, attempt + 1)
                
                if attempt < self.max_retries - 1:
                    wait_time = self.backoff_factor ** attempt
                    logger.warning(
                        f"Error in {func.__name__} (attempt {attempt + 1}): {e}. "
                        f"Retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(
                        f"Max retries exceeded for {func.__name__}: {e}"
                    )
        
        raise last_exception
    
    def log_error(self, error: Exception, context: dict = None):
        """Log error with context"""
        logger.error(
            f"Error: {error}",
            extra={
                "error_type": type(error).__name__,
                "context": context,
                "traceback": traceback.format_exc()
            }
        )


def async_error_handler(max_retries: int = 3):
    """Decorator for async functions with error handling"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            handler = ErrorHandler(max_retries=max_retries)
            try:
                return await handler.retry_async(
                    func,
                    *args,
                    **kwargs
                )
            except Exception as e:
                logger.error(f"Function {func.__name__} failed: {e}")
                raise
        
        return wrapper
    
    return decorator


def validate_input(**validators):
    """Decorator for input validation"""
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate kwargs
            for key, validator in validators.items():
                if key in kwargs:
                    try:
                        if not validator(kwargs[key]):
                            raise ValidationException(
                                f"Invalid {key}: {kwargs[key]}",
                                ErrorSeverity.ERROR
                            )
                    except ValidationException:
                        raise
                    except Exception as e:
                        raise ValidationException(
                            f"Validation error for {key}: {e}",
                            ErrorSeverity.ERROR
                        )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class CircuitBreaker:
    """Circuit breaker pattern for fault tolerance"""
    
    def __init__(self, failure_threshold: int = 5, timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half-open
    
    async def call(self, func: Callable, *args, **kwargs):
        """Execute function with circuit breaker"""
        
        if self.state == "open":
            # Check if timeout has passed
            import time
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "half-open"
            else:
                raise EspalhaException(
                    f"Circuit breaker is open for {func.__name__}",
                    ErrorSeverity.CRITICAL
                )
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "half-open":
                self.state = "closed"
                self.failure_count = 0
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
                import time
                self.last_failure_time = time.time()
                logger.error(
                    f"Circuit breaker opened for {func.__name__} "
                    f"after {self.failure_count} failures"
                )
            
            raise


class Logger:
    """Enhanced logging with context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
    
    def with_context(self, **context):
        """Create logger with context"""
        return ContextualLogger(self.logger, context)


class ContextualLogger:
    """Logger with context information"""
    
    def __init__(self, logger, context):
        self.logger = logger
        self.context = context
    
    def info(self, message: str):
        self.logger.info(f"{message} | {self.context}")
    
    def error(self, message: str):
        self.logger.error(f"{message} | {self.context}")
    
    def warning(self, message: str):
        self.logger.warning(f"{message} | {self.context}")


# Global error handler
global_error_handler = ErrorHandler()


def get_error_history():
    """Get error history"""
    return global_error_handler.errors


def clear_error_history():
    """Clear error history"""
    global_error_handler.errors = []

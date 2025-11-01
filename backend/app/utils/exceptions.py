"""Custom exceptions for the application."""


class BaseAppError(Exception):
    """Base application error."""
    
    def __init__(self, message: str, status_code: int = 500, details: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class ValidationError(BaseAppError):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: str = None, details: dict = None):
        super().__init__(message, status_code=400, details=details)
        self.field = field


class ScrapingError(BaseAppError):
    """Raised when content scraping fails."""
    
    def __init__(self, message: str, url: str = None, details: dict = None):
        super().__init__(message, status_code=422, details=details)
        self.url = url


class LLMServiceError(BaseAppError):
    """Raised when LLM service calls fail."""
    
    def __init__(self, message: str, service: str = None, details: dict = None):
        super().__init__(message, status_code=503, details=details)
        self.service = service


class DatabaseError(BaseAppError):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: str = None, details: dict = None):
        super().__init__(message, status_code=500, details=details)
        self.operation = operation


class FileProcessingError(BaseAppError):
    """Raised when file processing fails."""
    
    def __init__(self, message: str, filename: str = None, details: dict = None):
        super().__init__(message, status_code=422, details=details)
        self.filename = filename


class ContentValidationError(BaseAppError):
    """Raised when content validation fails."""
    
    def __init__(self, message: str, validation_type: str = None, details: dict = None):
        super().__init__(message, status_code=422, details=details)
        self.validation_type = validation_type


class ConfigurationError(BaseAppError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        super().__init__(message, status_code=500, details=details)
        self.config_key = config_key


class RateLimitError(BaseAppError):
    """Raised when rate limits are exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None, details: dict = None):
        super().__init__(message, status_code=429, details=details)
        self.retry_after = retry_after


def handle_app_error(error: BaseAppError) -> tuple:
    """Handle application errors and return Flask response format."""
    response_data = {
        'success': False,
        'error': error.message,
        'type': error.__class__.__name__
    }
    
    if error.details:
        response_data['details'] = error.details
    
    # Add specific error information based on error type
    if isinstance(error, ValidationError) and error.field:
        response_data['field'] = error.field
    elif isinstance(error, ScrapingError) and error.url:
        response_data['url'] = error.url
    elif isinstance(error, LLMServiceError) and error.service:
        response_data['service'] = error.service
    elif isinstance(error, DatabaseError) and error.operation:
        response_data['operation'] = error.operation
    elif isinstance(error, FileProcessingError) and error.filename:
        response_data['filename'] = error.filename
    elif isinstance(error, RateLimitError) and error.retry_after:
        response_data['retry_after'] = error.retry_after
    
    return response_data, error.status_code
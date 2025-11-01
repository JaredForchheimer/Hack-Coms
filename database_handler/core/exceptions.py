"""Custom exceptions for database operations."""


class DatabaseError(Exception):
    """Base exception for database-related errors."""
    
    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


class DatabaseConnectionError(DatabaseError):
    """Exception raised when database connection fails."""
    pass


class ValidationError(DatabaseError):
    """Exception raised when data validation fails."""
    
    def __init__(self, message: str, field: str = None, value=None):
        self.field = field
        self.value = value
        super().__init__(message)


class NotFoundError(DatabaseError):
    """Exception raised when requested resource is not found."""
    
    def __init__(self, resource_type: str, identifier, message: str = None):
        self.resource_type = resource_type
        self.identifier = identifier
        if message is None:
            message = f"{resource_type} with identifier '{identifier}' not found"
        super().__init__(message)


class DuplicateError(DatabaseError):
    """Exception raised when attempting to create duplicate resource."""
    
    def __init__(self, resource_type: str, field: str, value, message: str = None):
        self.resource_type = resource_type
        self.field = field
        self.value = value
        if message is None:
            message = f"{resource_type} with {field} '{value}' already exists"
        super().__init__(message)


class TransactionError(DatabaseError):
    """Exception raised when transaction operations fail."""
    pass


class MigrationError(DatabaseError):
    """Exception raised when database migration fails."""
    pass


class ConfigurationError(DatabaseError):
    """Exception raised when configuration is invalid."""
    pass
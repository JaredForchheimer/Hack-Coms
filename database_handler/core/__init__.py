"""Core module for database handler."""

from .connection import DatabaseHandler
from .base_model import BaseModel
from .exceptions import (
    DatabaseError,
    DatabaseConnectionError,
    ValidationError,
    NotFoundError,
    DuplicateError
)

__all__ = [
    "DatabaseHandler",
    "BaseModel", 
    "DatabaseError",
    "DatabaseConnectionError",
    "ValidationError",
    "NotFoundError",
    "DuplicateError"
]
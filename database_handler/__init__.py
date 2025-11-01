"""
Database Handler Package

A comprehensive PostgreSQL database handler for managing projects with text sources,
translations, summaries, videos, and links in a hierarchical structure.
"""

from .core.connection import DatabaseHandler
from .config.database import DatabaseConfig

__version__ = "1.0.0"
__all__ = ["DatabaseHandler", "DatabaseConfig"]
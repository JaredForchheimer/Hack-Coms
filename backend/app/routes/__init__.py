"""Routes package initialization."""

from .api import api_bp
from .health import health_bp

__all__ = ['api_bp', 'health_bp']
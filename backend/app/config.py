"""Flask application configuration."""

import os
from decouple import config
from typing import List


class Config:
    """Base configuration class."""
    
    # Flask Settings
    SECRET_KEY = config('SECRET_KEY', default='dev-secret-key-change-in-production')
    FLASK_ENV = config('FLASK_ENV', default='development')
    DEBUG = config('FLASK_DEBUG', default=True, cast=bool)
    
    # Server Settings
    HOST = config('FLASK_HOST', default='0.0.0.0')
    PORT = config('FLASK_PORT', default=5000, cast=int)
    
    # CORS Settings
    CORS_ORIGINS = config('CORS_ORIGINS', default='http://localhost:5173').split(',')
    
    # Upload Settings
    MAX_CONTENT_LENGTH = config('MAX_CONTENT_LENGTH', default=16 * 1024 * 1024, cast=int)  # 16MB
    UPLOAD_FOLDER = config('UPLOAD_FOLDER', default='uploads')
    
    # Database Configuration
    DB_HOST = config('DB_HOST', default='localhost')
    DB_PORT = config('DB_PORT', default=5432, cast=int)
    DB_NAME = config('DB_NAME', default='asl_summarizer')
    DB_USER = config('DB_USER', default='postgres')
    DB_PASSWORD = config('DB_PASSWORD')
    DB_POOL_SIZE = config('DB_POOL_SIZE', default=10, cast=int)
    DB_MAX_OVERFLOW = config('DB_MAX_OVERFLOW', default=20, cast=int)
    
    # External API Keys
    ANTHROPIC_API_KEY = config('ANTHROPIC_API_KEY')
    
    # Content Processing Settings
    MAX_CONTENT_SIZE = 1000000  # 1MB max text content
    SCRAPING_TIMEOUT = 30  # seconds
    LLM_REQUEST_TIMEOUT = 60  # seconds
    
    @classmethod
    def get_database_config(cls):
        """Get database configuration dictionary."""
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'username': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'pool_size': cls.DB_POOL_SIZE,
            'max_overflow': cls.DB_MAX_OVERFLOW
        }


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    FLASK_ENV = 'production'


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    DB_NAME = 'asl_summarizer_test'


def get_config():
    """Get configuration based on environment."""
    env = config('FLASK_ENV', default='development')
    
    if env == 'production':
        return ProductionConfig()
    elif env == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()
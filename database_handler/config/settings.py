"""Settings and configuration loading utilities."""

import os
import yaml
from typing import Dict, Any
from decouple import config
from .database import DatabaseConfig


def load_config_from_env() -> DatabaseConfig:
    """Load database configuration from environment variables."""
    return DatabaseConfig(
        host=config("DB_HOST", default="localhost"),
        port=config("DB_PORT", default=5432, cast=int),
        database=config("DB_NAME", default="project_db"),
        username=config("DB_USER", default="postgres"),
        password=config("DB_PASSWORD", default=""),
        pool_size=config("DB_POOL_SIZE", default=10, cast=int),
        max_overflow=config("DB_MAX_OVERFLOW", default=20, cast=int),
        pool_timeout=config("DB_POOL_TIMEOUT", default=30, cast=int),
        pool_recycle=config("DB_POOL_RECYCLE", default=3600, cast=int),
        ssl_mode=config("DB_SSL_MODE", default="prefer"),
        connect_timeout=config("DB_CONNECT_TIMEOUT", default=10, cast=int),
    )


def load_config_from_file(file_path: str) -> DatabaseConfig:
    """Load database configuration from YAML file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")
    
    with open(file_path, 'r') as file:
        config_data = yaml.safe_load(file)
    
    db_config = config_data.get('database', {})
    
    return DatabaseConfig(
        host=db_config.get('host', 'localhost'),
        port=db_config.get('port', 5432),
        database=db_config.get('database', 'project_db'),
        username=db_config.get('username', 'postgres'),
        password=db_config.get('password', ''),
        pool_size=db_config.get('pool_size', 10),
        max_overflow=db_config.get('max_overflow', 20),
        pool_timeout=db_config.get('pool_timeout', 30),
        pool_recycle=db_config.get('pool_recycle', 3600),
        ssl_mode=db_config.get('ssl_mode', 'prefer'),
        connect_timeout=db_config.get('connect_timeout', 10),
    )


def create_sample_config_file(file_path: str) -> None:
    """Create a sample configuration file."""
    sample_config = {
        'database': {
            'host': 'localhost',
            'port': 5432,
            'database': 'project_db',
            'username': 'postgres',
            'password': 'your_password',
            'pool_size': 10,
            'max_overflow': 20,
            'pool_timeout': 30,
            'pool_recycle': 3600,
            'ssl_mode': 'prefer',
            'connect_timeout': 10
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        }
    }
    
    with open(file_path, 'w') as file:
        yaml.dump(sample_config, file, default_flow_style=False, indent=2)
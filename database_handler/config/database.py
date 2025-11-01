"""Database configuration classes and utilities."""

from typing import Optional
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Database configuration class."""
    
    host: str
    port: int
    database: str
    username: str
    password: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    ssl_mode: str = "prefer"
    connect_timeout: int = 10
    
    def get_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return (
            f"postgresql://{self.username}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
            f"?sslmode={self.ssl_mode}&connect_timeout={self.connect_timeout}"
        )
    
    def get_connection_params(self) -> dict:
        """Get connection parameters as dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.password,
            "sslmode": self.ssl_mode,
            "connect_timeout": self.connect_timeout,
        }
    
    def validate(self) -> None:
        """Validate configuration parameters."""
        if not self.host:
            raise ValueError("Database host is required")
        if not self.database:
            raise ValueError("Database name is required")
        if not self.username:
            raise ValueError("Database username is required")
        if not self.password:
            raise ValueError("Database password is required")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Database port must be between 1 and 65535")
        if self.pool_size <= 0:
            raise ValueError("Pool size must be greater than 0")
        if self.max_overflow < 0:
            raise ValueError("Max overflow must be non-negative")
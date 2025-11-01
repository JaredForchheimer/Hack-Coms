"""Database connection management with connection pooling."""

import logging
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Dict, Any, List, Generator
from ..config.database import DatabaseConfig
from .exceptions import DatabaseConnectionError, TransactionError


logger = logging.getLogger(__name__)


class DatabaseHandler:
    """Main database handler with connection pooling."""
    
    def __init__(self, config: DatabaseConfig, enable_logging: bool = True):
        """Initialize database handler with configuration."""
        self.config = config
        self.config.validate()
        self._pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None
        self._initialized = False
        
        if enable_logging:
            logging.basicConfig(level=logging.INFO)
        
        # Initialize repositories
        self._projects = None
        self._text_sources = None
        self._summaries = None
        self._translations = None
        self._videos = None
        self._links = None
    
    def initialize(self) -> None:
        """Initialize database connection pool and repositories."""
        try:
            self._create_connection_pool()
            self._test_connection()
            self._initialize_repositories()
            self._initialized = True
            logger.info("Database handler initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database handler: {e}")
            raise DatabaseConnectionError(f"Database initialization failed: {e}", e)
    
    def _create_connection_pool(self) -> None:
        """Create PostgreSQL connection pool."""
        try:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=self.config.pool_size + self.config.max_overflow,
                **self.config.get_connection_params()
            )
            logger.info(f"Created connection pool with {self.config.pool_size} connections")
        except psycopg2.Error as e:
            raise DatabaseConnectionError(f"Failed to create connection pool: {e}", e)
    
    def _test_connection(self) -> None:
        """Test database connection."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] != 1:
                    raise DatabaseConnectionError("Database connection test failed")
    
    def _initialize_repositories(self) -> None:
        """Initialize repository instances."""
        from ..models.project import ProjectRepository
        from ..models.text_source import TextSourceRepository
        from ..models.summary import SummaryRepository
        from ..models.translation import TranslationRepository
        from ..models.video import VideoRepository
        from ..models.link import LinkRepository
        
        self._projects = ProjectRepository(self)
        self._text_sources = TextSourceRepository(self)
        self._summaries = SummaryRepository(self)
        self._translations = TranslationRepository(self)
        self._videos = VideoRepository(self)
        self._links = LinkRepository(self)
    
    @property
    def projects(self):
        """Get projects repository."""
        if not self._initialized:
            raise RuntimeError("Database handler not initialized. Call initialize() first.")
        return self._projects
    
    @property
    def text_sources(self):
        """Get text sources repository."""
        if not self._initialized:
            raise RuntimeError("Database handler not initialized. Call initialize() first.")
        return self._text_sources
    
    @property
    def summaries(self):
        """Get summaries repository."""
        if not self._initialized:
            raise RuntimeError("Database handler not initialized. Call initialize() first.")
        return self._summaries
    
    @property
    def translations(self):
        """Get translations repository."""
        if not self._initialized:
            raise RuntimeError("Database handler not initialized. Call initialize() first.")
        return self._translations
    
    @property
    def videos(self):
        """Get videos repository."""
        if not self._initialized:
            raise RuntimeError("Database handler not initialized. Call initialize() first.")
        return self._videos
    
    @property
    def links(self):
        """Get links repository."""
        if not self._initialized:
            raise RuntimeError("Database handler not initialized. Call initialize() first.")
        return self._links
    
    @contextmanager
    def get_connection(self) -> Generator[psycopg2.extensions.connection, None, None]:
        """Get database connection from pool."""
        if self._pool is None:
            raise DatabaseConnectionError("Connection pool not initialized")
        
        connection = None
        try:
            connection = self._pool.getconn()
            if connection is None:
                raise DatabaseConnectionError("Failed to get connection from pool")
            
            # Set autocommit to False for transaction control
            connection.autocommit = False
            yield connection
            
        except psycopg2.Error as e:
            if connection:
                connection.rollback()
            logger.error(f"Database connection error: {e}")
            raise DatabaseConnectionError(f"Database operation failed: {e}", e)
        finally:
            if connection:
                self._pool.putconn(connection)
    
    @contextmanager
    def transaction(self) -> Generator['TransactionContext', None, None]:
        """Create a transaction context."""
        with self.get_connection() as conn:
            transaction_context = TransactionContext(conn, self)
            try:
                yield transaction_context
                conn.commit()
                logger.debug("Transaction committed successfully")
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction rolled back due to error: {e}")
                raise TransactionError(f"Transaction failed: {e}", e)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results."""
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
    
    def execute_command(self, command: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE command and return affected rows."""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(command, params)
                conn.commit()
                return cursor.rowcount
    
    def close(self) -> None:
        """Close all connections in the pool."""
        if self._pool:
            self._pool.closeall()
            self._pool = None
            self._initialized = False
            logger.info("Database connection pool closed")
    
    def __enter__(self):
        """Context manager entry."""
        if not self._initialized:
            self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


class TransactionContext:
    """Transaction context for database operations."""
    
    def __init__(self, connection: psycopg2.extensions.connection, db_handler: DatabaseHandler):
        self.connection = connection
        self.db_handler = db_handler
        
        # Create transaction-specific repositories
        from ..models.project import ProjectRepository
        from ..models.text_source import TextSourceRepository
        from ..models.summary import SummaryRepository
        from ..models.translation import TranslationRepository
        from ..models.video import VideoRepository
        from ..models.link import LinkRepository
        
        self.projects = ProjectRepository(db_handler, connection)
        self.text_sources = TextSourceRepository(db_handler, connection)
        self.summaries = SummaryRepository(db_handler, connection)
        self.translations = TranslationRepository(db_handler, connection)
        self.videos = VideoRepository(db_handler, connection)
        self.links = LinkRepository(db_handler, connection)
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query within the transaction."""
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def execute_command(self, command: str, params: tuple = None) -> int:
        """Execute an INSERT/UPDATE/DELETE command within the transaction."""
        with self.connection.cursor() as cursor:
            cursor.execute(command, params)
            return cursor.rowcount
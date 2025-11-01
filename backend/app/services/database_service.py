"""Database service for connecting Flask API to database handler."""

import logging
import sys
import os
from typing import Dict, Any, List, Optional

# Add the parent directory to path to import database_handler
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../'))

from database_handler import DatabaseHandler, DatabaseConfig
from database_handler.core.exceptions import NotFoundError, ValidationError as DBValidationError
from ..utils.exceptions import DatabaseError, ValidationError

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for database operations."""

    def __init__(self, config: dict):
        self.config = config
        self.db_handler = None
        self._init_database()

    def _init_database(self):
        """Initialize database connection."""
        try:
            db_config = DatabaseConfig(
                host=self.config['DB_HOST'],
                port=self.config['DB_PORT'],
                database=self.config['DB_NAME'],
                username=self.config['DB_USER'],
                password=self.config['DB_PASSWORD'],
                pool_size=self.config.get('DB_POOL_SIZE', 10),
                max_overflow=self.config.get('DB_MAX_OVERFLOW', 20)
            )
            
            self.db_handler = DatabaseHandler(db_config)
            self.db_handler.initialize()
            
            logger.info("Database service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise DatabaseError(f"Database initialization failed: {str(e)}")

    def get_or_create_default_project(self) -> int:
        """Get or create a default project for the application."""
        try:
            # Try to find existing default project
            projects = self.db_handler.projects.search("ASL Summarizer Default")
            if projects:
                return projects[0].id
            
            # Create default project
            project = self.db_handler.projects.create({
                'name': 'ASL Summarizer Default',
                'description': 'Default project for ASL Summarizer application',
                'metadata': {
                    'created_by': 'system',
                    'is_default': True
                }
            })
            
            logger.info(f"Created default project with ID: {project.id}")
            return project.id
            
        except Exception as e:
            logger.error(f"Error getting/creating default project: {str(e)}")
            raise DatabaseError(f"Failed to get default project: {str(e)}")

    def store_text_source(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a text source in the database."""
        try:
            # Ensure we have a project_id
            if 'project_id' not in source_data:
                source_data['project_id'] = self.get_or_create_default_project()
            
            # Create the text source
            text_source = self.db_handler.text_sources.create(source_data)
            
            result = {
                'id': text_source.id,
                'project_id': text_source.project_id,
                'title': text_source.title,
                'content': text_source.content,
                'source_type': text_source.source_type,
                'source_url': text_source.source_url,
                'created_at': text_source.created_at.isoformat() if text_source.created_at else None,
                'metadata': text_source.metadata
            }
            
            logger.info(f"Stored text source with ID: {text_source.id}")
            return result
            
        except DBValidationError as e:
            raise ValidationError(f"Invalid text source data: {str(e)}")
        except Exception as e:
            logger.error(f"Error storing text source: {str(e)}")
            raise DatabaseError(f"Failed to store text source: {str(e)}")

    def store_summary(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store a summary in the database."""
        try:
            # Create the summary
            summary = self.db_handler.summaries.create(summary_data)
            
            result = {
                'id': summary.id,
                'text_source_id': summary.text_source_id,
                'title': summary.title,
                'content': summary.content,
                'summary_type': summary.summary_type,
                'created_at': summary.created_at.isoformat() if summary.created_at else None,
                'metadata': summary.metadata
            }
            
            logger.info(f"Stored summary with ID: {summary.id}")
            return result
            
        except DBValidationError as e:
            raise ValidationError(f"Invalid summary data: {str(e)}")
        except Exception as e:
            logger.error(f"Error storing summary: {str(e)}")
            raise DatabaseError(f"Failed to store summary: {str(e)}")

    def get_sources(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get text sources from database."""
        try:
            sources = self.db_handler.text_sources.list(limit=limit, offset=offset)
            
            result = []
            for source in sources:
                result.append({
                    'id': source.id,
                    'project_id': source.project_id,
                    'title': source.title,
                    'content': source.content[:500] + ('...' if len(source.content) > 500 else ''),  # Preview
                    'source_type': source.source_type,
                    'source_url': source.source_url,
                    'created_at': source.created_at.isoformat() if source.created_at else None,
                    'metadata': source.metadata
                })
            
            logger.info(f"Retrieved {len(result)} sources from database")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving sources: {str(e)}")
            raise DatabaseError(f"Failed to retrieve sources: {str(e)}")

    def get_summaries(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get summaries from database."""
        try:
            summaries = self.db_handler.summaries.list(limit=limit, offset=offset)
            
            result = []
            for summary in summaries:
                # Get the associated text source for additional info
                try:
                    source = self.db_handler.text_sources.get_by_id(summary.text_source_id)
                    source_title = source.title
                    source_url = source.source_url
                except:
                    source_title = "Unknown Source"
                    source_url = None
                
                result.append({
                    'id': summary.id,
                    'text_source_id': summary.text_source_id,
                    'title': summary.title,
                    'content': summary.content,
                    'summary_type': summary.summary_type,
                    'created_at': summary.created_at.isoformat() if summary.created_at else None,
                    'metadata': summary.metadata,
                    'source_title': source_title,
                    'source_url': source_url
                })
            
            logger.info(f"Retrieved {len(result)} summaries from database")
            return result
            
        except Exception as e:
            logger.error(f"Error retrieving summaries: {str(e)}")
            raise DatabaseError(f"Failed to retrieve summaries: {str(e)}")

    def get_source_by_id(self, source_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific text source by ID."""
        try:
            source = self.db_handler.text_sources.get_by_id(source_id)
            
            return {
                'id': source.id,
                'project_id': source.project_id,
                'title': source.title,
                'content': source.content,
                'source_type': source.source_type,
                'source_url': source.source_url,
                'created_at': source.created_at.isoformat() if source.created_at else None,
                'metadata': source.metadata
            }
            
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error retrieving source {source_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve source: {str(e)}")

    def get_summary_by_id(self, summary_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific summary by ID."""
        try:
            summary = self.db_handler.summaries.get_by_id(summary_id)
            
            return {
                'id': summary.id,
                'text_source_id': summary.text_source_id,
                'title': summary.title,
                'content': summary.content,
                'summary_type': summary.summary_type,
                'created_at': summary.created_at.isoformat() if summary.created_at else None,
                'metadata': summary.metadata
            }
            
        except NotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error retrieving summary {summary_id}: {str(e)}")
            raise DatabaseError(f"Failed to retrieve summary: {str(e)}")

    def search_sources(self, search_term: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Search text sources."""
        try:
            sources = self.db_handler.text_sources.search_content(search_term, limit=limit)
            
            result = []
            for source in sources:
                result.append({
                    'id': source.id,
                    'project_id': source.project_id,
                    'title': source.title,
                    'content': source.content[:500] + ('...' if len(source.content) > 500 else ''),
                    'source_type': source.source_type,
                    'source_url': source.source_url,
                    'created_at': source.created_at.isoformat() if source.created_at else None,
                    'metadata': source.metadata
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching sources: {str(e)}")
            raise DatabaseError(f"Failed to search sources: {str(e)}")

    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            sources = self.db_handler.text_sources.list(limit=1)
            summaries = self.db_handler.summaries.list(limit=1)
            
            # Get counts (simplified approach)
            all_sources = self.db_handler.text_sources.list(limit=10000)
            all_summaries = self.db_handler.summaries.list(limit=10000)
            
            return {
                'sources_count': len(all_sources),
                'summaries_count': len(all_summaries),
                'database_connected': True
            }
            
        except Exception as e:
            logger.error(f"Error getting database stats: {str(e)}")
            return {
                'sources_count': 0,
                'summaries_count': 0,
                'database_connected': False,
                'error': str(e)
            }

    def health_check(self) -> bool:
        """Check database health."""
        try:
            # Simple query to test connection
            self.db_handler.text_sources.list(limit=1)
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {str(e)}")
            return False

    def close(self):
        """Close database connections."""
        if self.db_handler:
            try:
                self.db_handler.close()
                logger.info("Database connections closed")
            except Exception as e:
                logger.error(f"Error closing database connections: {str(e)}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
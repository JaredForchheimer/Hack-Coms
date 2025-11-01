"""TextSource model and repository."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from psycopg2.extras import RealDictCursor
from ..core.base_model import BaseModel
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError


logger = logging.getLogger(__name__)


@dataclass
class TextSource(BaseModel):
    """TextSource model representing a text source entity."""
    
    project_id: int = 0
    title: str = ""
    content: str = ""
    source_type: str = "text"
    source_url: Optional[str] = None
    
    def get_table_name(self) -> str:
        """Get the database table name."""
        return "text_sources"
    
    def get_insert_fields(self) -> List[str]:
        """Get fields for INSERT operations."""
        return ["project_id", "title", "content", "source_type", "source_url", "metadata"]
    
    def get_update_fields(self) -> List[str]:
        """Get fields for UPDATE operations."""
        return ["title", "content", "source_type", "source_url", "metadata"]
    
    def validate(self) -> None:
        """Validate text source data."""
        if not self.project_id or self.project_id <= 0:
            raise ValidationError("Project ID is required and must be positive", "project_id", self.project_id)
        
        if not self.title or not self.title.strip():
            raise ValidationError("Text source title is required", "title", self.title)
        
        if len(self.title) > 255:
            raise ValidationError("Text source title must be 255 characters or less", "title", self.title)
        
        if not self.content or not self.content.strip():
            raise ValidationError("Text source content is required", "content", self.content)
        
        if self.source_type and len(self.source_type) > 50:
            raise ValidationError("Source type must be 50 characters or less", "source_type", self.source_type)
        
        if self.source_url and len(self.source_url) > 500:
            raise ValidationError("Source URL must be 500 characters or less", "source_url", self.source_url)


class TextSourceRepository:
    """Repository for TextSource operations."""
    
    def __init__(self, db_handler, connection=None):
        """Initialize repository with database handler."""
        self.db_handler = db_handler
        self.connection = connection
    
    def _execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute query using connection or db_handler."""
        if self.connection:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
        else:
            return self.db_handler.execute_query(query, params)
    
    def _execute_command(self, command: str, params: tuple = None) -> int:
        """Execute command using connection or db_handler."""
        if self.connection:
            with self.connection.cursor() as cursor:
                cursor.execute(command, params)
                return cursor.rowcount
        else:
            return self.db_handler.execute_command(command, params)
    
    def create(self, text_source_data: Dict[str, Any]) -> TextSource:
        """Create a new text source."""
        text_source = TextSource(**text_source_data)
        text_source.validate()
        
        # Verify project exists
        project_query = "SELECT id FROM projects WHERE id = %s"
        project_results = self._execute_query(project_query, (text_source.project_id,))
        if not project_results:
            raise NotFoundError("Project", text_source.project_id)
        
        query = """
            INSERT INTO text_sources (project_id, title, content, source_type, source_url, metadata)
            VALUES (%(project_id)s, %(title)s, %(content)s, %(source_type)s, %(source_url)s, %(metadata)s)
            RETURNING id, created_at, updated_at
        """
        
        try:
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, text_source.get_insert_values())
                    result = cursor.fetchone()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, text_source.get_insert_values())
                        result = cursor.fetchone()
                        conn.commit()
            
            text_source.id = result['id']
            text_source.created_at = result['created_at']
            text_source.updated_at = result['updated_at']
            
            logger.info(f"Created text source with ID: {text_source.id}")
            return text_source
            
        except Exception as e:
            logger.error(f"Failed to create text source: {e}")
            raise DatabaseError(f"Failed to create text source: {e}", e)
    
    def get_by_id(self, text_source_id: int) -> TextSource:
        """Get text source by ID."""
        query = "SELECT * FROM text_sources WHERE id = %s"
        results = self._execute_query(query, (text_source_id,))
        
        if not results:
            raise NotFoundError("TextSource", text_source_id)
        
        return TextSource.from_dict(results[0])
    
    def get_by_project_id(self, project_id: int, limit: int = 100, offset: int = 0) -> List[TextSource]:
        """Get all text sources for a project."""
        query = """
            SELECT * FROM text_sources 
            WHERE project_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (project_id, limit, offset))
        return [TextSource.from_dict(row) for row in results]
    
    def get_by_type(self, project_id: int, source_type: str) -> List[TextSource]:
        """Get text sources by type for a project."""
        query = """
            SELECT * FROM text_sources 
            WHERE project_id = %s AND source_type = %s 
            ORDER BY created_at DESC
        """
        results = self._execute_query(query, (project_id, source_type))
        return [TextSource.from_dict(row) for row in results]
    
    def search_content(self, search_term: str, project_id: Optional[int] = None, limit: int = 100) -> List[TextSource]:
        """Search text sources by content or title."""
        search_pattern = f"%{search_term}%"
        
        if project_id:
            query = """
                SELECT * FROM text_sources 
                WHERE project_id = %s AND (title ILIKE %s OR content ILIKE %s)
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params = (project_id, search_pattern, search_pattern, limit)
        else:
            query = """
                SELECT * FROM text_sources 
                WHERE title ILIKE %s OR content ILIKE %s
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params = (search_pattern, search_pattern, limit)
        
        results = self._execute_query(query, params)
        return [TextSource.from_dict(row) for row in results]
    
    def list(self, limit: int = 100, offset: int = 0) -> List[TextSource]:
        """List all text sources with pagination."""
        query = """
            SELECT * FROM text_sources 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (limit, offset))
        return [TextSource.from_dict(row) for row in results]
    
    def update(self, text_source_id: int, update_data: Dict[str, Any]) -> TextSource:
        """Update text source by ID."""
        # Get existing text source
        existing_source = self.get_by_id(text_source_id)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(existing_source, key) and key != 'project_id':  # Don't allow project_id changes
                setattr(existing_source, key, value)
        
        existing_source.validate()
        
        query = """
            UPDATE text_sources 
            SET title = %(title)s, content = %(content)s, source_type = %(source_type)s,
                source_url = %(source_url)s, metadata = %(metadata)s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING updated_at
        """
        
        try:
            update_values = existing_source.get_update_values()
            update_values['id'] = text_source_id
            
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, update_values)
                    result = cursor.fetchone()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, update_values)
                        result = cursor.fetchone()
                        conn.commit()
            
            existing_source.updated_at = result['updated_at']
            
            logger.info(f"Updated text source with ID: {text_source_id}")
            return existing_source
            
        except Exception as e:
            logger.error(f"Failed to update text source {text_source_id}: {e}")
            raise DatabaseError(f"Failed to update text source: {e}", e)
    
    def delete(self, text_source_id: int) -> bool:
        """Delete text source by ID (cascades to related data)."""
        # Check if text source exists
        self.get_by_id(text_source_id)
        
        query = "DELETE FROM text_sources WHERE id = %s"
        
        try:
            affected_rows = self._execute_command(query, (text_source_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted text source with ID: {text_source_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete text source {text_source_id}: {e}")
            raise DatabaseError(f"Failed to delete text source: {e}", e)
    
    def get_statistics(self, text_source_id: int) -> Dict[str, Any]:
        """Get text source statistics."""
        query = """
            SELECT 
                ts.id,
                ts.title,
                ts.project_id,
                LENGTH(ts.content) as content_length,
                COUNT(DISTINCT s.id) as summary_count,
                COUNT(DISTINCT t.id) as translation_count,
                COUNT(DISTINCT v.id) as video_count,
                COUNT(DISTINCT l.id) as link_count,
                ARRAY_AGG(DISTINCT t.language_code) FILTER (WHERE t.language_code IS NOT NULL) as languages
            FROM text_sources ts
            LEFT JOIN summaries s ON ts.id = s.text_source_id
            LEFT JOIN translations t ON ts.id = t.text_source_id
            LEFT JOIN videos v ON ts.id = v.text_source_id
            LEFT JOIN links l ON ts.id = l.text_source_id
            WHERE ts.id = %s
            GROUP BY ts.id, ts.title, ts.project_id, ts.content
        """
        
        results = self._execute_query(query, (text_source_id,))
        
        if not results:
            raise NotFoundError("TextSource", text_source_id)
        
        stats = results[0]
        return {
            'text_source_id': stats['id'],
            'title': stats['title'],
            'project_id': stats['project_id'],
            'content_length': stats['content_length'] or 0,
            'summary_count': stats['summary_count'] or 0,
            'translation_count': stats['translation_count'] or 0,
            'video_count': stats['video_count'] or 0,
            'link_count': stats['link_count'] or 0,
            'languages': [lang for lang in (stats['languages'] or []) if lang]
        }
    
    def bulk_create(self, text_sources_data: List[Dict[str, Any]]) -> List[TextSource]:
        """Create multiple text sources in a single operation."""
        if not text_sources_data:
            return []
        
        text_sources = []
        for source_data in text_sources_data:
            text_source = TextSource(**source_data)
            text_source.validate()
            text_sources.append(text_source)
        
        # Verify all projects exist
        project_ids = list(set(ts.project_id for ts in text_sources))
        project_query = f"SELECT id FROM projects WHERE id IN ({','.join(['%s'] * len(project_ids))})"
        project_results = self._execute_query(project_query, tuple(project_ids))
        existing_project_ids = {row['id'] for row in project_results}
        
        for ts in text_sources:
            if ts.project_id not in existing_project_ids:
                raise NotFoundError("Project", ts.project_id)
        
        # Build bulk insert query
        query = """
            INSERT INTO text_sources (project_id, title, content, source_type, source_url, metadata)
            VALUES %s
            RETURNING id, title, created_at, updated_at
        """
        
        try:
            values = []
            for text_source in text_sources:
                insert_values = text_source.get_insert_values()
                values.append((
                    insert_values['project_id'],
                    insert_values['title'],
                    insert_values['content'],
                    insert_values['source_type'],
                    insert_values['source_url'],
                    insert_values['metadata']
                ))
            
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    from psycopg2.extras import execute_values
                    execute_values(cursor, query, values, template=None, page_size=100)
                    results = cursor.fetchall()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        from psycopg2.extras import execute_values
                        execute_values(cursor, query, values, template=None, page_size=100)
                        results = cursor.fetchall()
                        conn.commit()
            
            # Update text source objects with returned data
            for i, result in enumerate(results):
                text_sources[i].id = result['id']
                text_sources[i].created_at = result['created_at']
                text_sources[i].updated_at = result['updated_at']
            
            logger.info(f"Created {len(text_sources)} text sources in bulk operation")
            return text_sources
            
        except Exception as e:
            logger.error(f"Failed to bulk create text sources: {e}")
            raise DatabaseError(f"Failed to bulk create text sources: {e}", e)
    
    def bulk_update_by_project(self, project_id: int, update_data: Dict[str, Any]) -> int:
        """Update all text sources for a project."""
        # Build dynamic update query
        set_clauses = []
        params = []
        
        for key, value in update_data.items():
            if key in ['title', 'content', 'source_type', 'source_url', 'metadata']:
                set_clauses.append(f"{key} = %s")
                params.append(value)
        
        if not set_clauses:
            return 0
        
        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        params.append(project_id)
        
        query = f"""
            UPDATE text_sources 
            SET {', '.join(set_clauses)}
            WHERE project_id = %s
        """
        
        try:
            affected_rows = self._execute_command(query, tuple(params))
            logger.info(f"Updated {affected_rows} text sources for project {project_id}")
            return affected_rows
            
        except Exception as e:
            logger.error(f"Failed to bulk update text sources for project {project_id}: {e}")
            raise DatabaseError(f"Failed to bulk update text sources: {e}", e)
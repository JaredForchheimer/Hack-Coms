"""Summary model and repository."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from psycopg2.extras import RealDictCursor
from ..core.base_model import BaseModel
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError


logger = logging.getLogger(__name__)


@dataclass
class Summary(BaseModel):
    """Summary model representing a summary entity."""
    
    text_source_id: int = 0
    title: Optional[str] = None
    content: str = ""
    summary_type: str = "general"
    
    def get_table_name(self) -> str:
        """Get the database table name."""
        return "summaries"
    
    def get_insert_fields(self) -> List[str]:
        """Get fields for INSERT operations."""
        return ["text_source_id", "title", "content", "summary_type", "metadata"]
    
    def get_update_fields(self) -> List[str]:
        """Get fields for UPDATE operations."""
        return ["title", "content", "summary_type", "metadata"]
    
    def validate(self) -> None:
        """Validate summary data."""
        if not self.text_source_id or self.text_source_id <= 0:
            raise ValidationError("Text source ID is required and must be positive", "text_source_id", self.text_source_id)
        
        if not self.content or not self.content.strip():
            raise ValidationError("Summary content is required", "content", self.content)
        
        if self.title and len(self.title) > 255:
            raise ValidationError("Summary title must be 255 characters or less", "title", self.title)
        
        if self.summary_type and len(self.summary_type) > 50:
            raise ValidationError("Summary type must be 50 characters or less", "summary_type", self.summary_type)


class SummaryRepository:
    """Repository for Summary operations."""
    
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
    
    def create(self, summary_data: Dict[str, Any]) -> Summary:
        """Create a new summary."""
        summary = Summary(**summary_data)
        summary.validate()
        
        # Verify text source exists
        source_query = "SELECT id FROM text_sources WHERE id = %s"
        source_results = self._execute_query(source_query, (summary.text_source_id,))
        if not source_results:
            raise NotFoundError("TextSource", summary.text_source_id)
        
        query = """
            INSERT INTO summaries (text_source_id, title, content, summary_type, metadata)
            VALUES (%(text_source_id)s, %(title)s, %(content)s, %(summary_type)s, %(metadata)s)
            RETURNING id, created_at, updated_at
        """
        
        try:
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, summary.get_insert_values())
                    result = cursor.fetchone()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, summary.get_insert_values())
                        result = cursor.fetchone()
                        conn.commit()
            
            summary.id = result['id']
            summary.created_at = result['created_at']
            summary.updated_at = result['updated_at']
            
            logger.info(f"Created summary with ID: {summary.id}")
            return summary
            
        except Exception as e:
            logger.error(f"Failed to create summary: {e}")
            raise DatabaseError(f"Failed to create summary: {e}", e)
    
    def get_by_id(self, summary_id: int) -> Summary:
        """Get summary by ID."""
        query = "SELECT * FROM summaries WHERE id = %s"
        results = self._execute_query(query, (summary_id,))
        
        if not results:
            raise NotFoundError("Summary", summary_id)
        
        return Summary.from_dict(results[0])
    
    def get_by_source_id(self, text_source_id: int, limit: int = 100, offset: int = 0) -> List[Summary]:
        """Get all summaries for a text source."""
        query = """
            SELECT * FROM summaries 
            WHERE text_source_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (text_source_id, limit, offset))
        return [Summary.from_dict(row) for row in results]
    
    def get_by_type(self, text_source_id: int, summary_type: str) -> List[Summary]:
        """Get summaries by type for a text source."""
        query = """
            SELECT * FROM summaries 
            WHERE text_source_id = %s AND summary_type = %s 
            ORDER BY created_at DESC
        """
        results = self._execute_query(query, (text_source_id, summary_type))
        return [Summary.from_dict(row) for row in results]
    
    def get_by_project_type(self, project_id: int, summary_type: str) -> List[Summary]:
        """Get all summaries of a specific type for a project."""
        query = """
            SELECT s.* FROM summaries s
            JOIN text_sources ts ON s.text_source_id = ts.id
            WHERE ts.project_id = %s AND s.summary_type = %s
            ORDER BY s.created_at DESC
        """
        results = self._execute_query(query, (project_id, summary_type))
        return [Summary.from_dict(row) for row in results]
    
    def search_content(self, search_term: str, summary_type: Optional[str] = None, limit: int = 100) -> List[Summary]:
        """Search summaries by content or title."""
        search_pattern = f"%{search_term}%"
        
        if summary_type:
            query = """
                SELECT * FROM summaries 
                WHERE summary_type = %s AND (title ILIKE %s OR content ILIKE %s)
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params = (summary_type, search_pattern, search_pattern, limit)
        else:
            query = """
                SELECT * FROM summaries 
                WHERE title ILIKE %s OR content ILIKE %s
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params = (search_pattern, search_pattern, limit)
        
        results = self._execute_query(query, params)
        return [Summary.from_dict(row) for row in results]
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Summary]:
        """List all summaries with pagination."""
        query = """
            SELECT * FROM summaries 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (limit, offset))
        return [Summary.from_dict(row) for row in results]
    
    def update(self, summary_id: int, update_data: Dict[str, Any]) -> Summary:
        """Update summary by ID."""
        # Get existing summary
        existing_summary = self.get_by_id(summary_id)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(existing_summary, key) and key != 'text_source_id':  # Don't allow text_source_id changes
                setattr(existing_summary, key, value)
        
        existing_summary.validate()
        
        query = """
            UPDATE summaries 
            SET title = %(title)s, content = %(content)s, summary_type = %(summary_type)s,
                metadata = %(metadata)s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING updated_at
        """
        
        try:
            update_values = existing_summary.get_update_values()
            update_values['id'] = summary_id
            
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
            
            existing_summary.updated_at = result['updated_at']
            
            logger.info(f"Updated summary with ID: {summary_id}")
            return existing_summary
            
        except Exception as e:
            logger.error(f"Failed to update summary {summary_id}: {e}")
            raise DatabaseError(f"Failed to update summary: {e}", e)
    
    def delete(self, summary_id: int) -> bool:
        """Delete summary by ID."""
        # Check if summary exists
        self.get_by_id(summary_id)
        
        query = "DELETE FROM summaries WHERE id = %s"
        
        try:
            affected_rows = self._execute_command(query, (summary_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted summary with ID: {summary_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete summary {summary_id}: {e}")
            raise DatabaseError(f"Failed to delete summary: {e}", e)
    
    def get_available_types(self, text_source_id: Optional[int] = None) -> List[str]:
        """Get list of available summary types."""
        if text_source_id:
            query = """
                SELECT DISTINCT summary_type FROM summaries 
                WHERE text_source_id = %s 
                ORDER BY summary_type
            """
            params = (text_source_id,)
        else:
            query = "SELECT DISTINCT summary_type FROM summaries ORDER BY summary_type"
            params = None
        
        results = self._execute_query(query, params)
        return [row['summary_type'] for row in results]
    
    def bulk_create(self, summaries_data: List[Dict[str, Any]]) -> List[Summary]:
        """Create multiple summaries in a single operation."""
        if not summaries_data:
            return []
        
        summaries = []
        for summary_data in summaries_data:
            summary = Summary(**summary_data)
            summary.validate()
            summaries.append(summary)
        
        # Verify all text sources exist
        source_ids = list(set(s.text_source_id for s in summaries))
        source_query = f"SELECT id FROM text_sources WHERE id IN ({','.join(['%s'] * len(source_ids))})"
        source_results = self._execute_query(source_query, tuple(source_ids))
        existing_source_ids = {row['id'] for row in source_results}
        
        for s in summaries:
            if s.text_source_id not in existing_source_ids:
                raise NotFoundError("TextSource", s.text_source_id)
        
        # Build bulk insert query
        query = """
            INSERT INTO summaries (text_source_id, title, content, summary_type, metadata)
            VALUES %s
            RETURNING id, title, created_at, updated_at
        """
        
        try:
            values = []
            for summary in summaries:
                insert_values = summary.get_insert_values()
                values.append((
                    insert_values['text_source_id'],
                    insert_values['title'],
                    insert_values['content'],
                    insert_values['summary_type'],
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
            
            # Update summary objects with returned data
            for i, result in enumerate(results):
                summaries[i].id = result['id']
                summaries[i].created_at = result['created_at']
                summaries[i].updated_at = result['updated_at']
            
            logger.info(f"Created {len(summaries)} summaries in bulk operation")
            return summaries
            
        except Exception as e:
            logger.error(f"Failed to bulk create summaries: {e}")
            raise DatabaseError(f"Failed to bulk create summaries: {e}", e)
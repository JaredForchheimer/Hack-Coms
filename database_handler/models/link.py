"""Link model and repository."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from psycopg2.extras import RealDictCursor
from ..core.base_model import BaseModel
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError


logger = logging.getLogger(__name__)


@dataclass
class Link(BaseModel):
    """Link model representing a link entity."""
    
    text_source_id: int = 0
    url: str = ""
    title: Optional[str] = None
    description: Optional[str] = None
    link_type: str = "reference"
    is_active: bool = True
    
    def get_table_name(self) -> str:
        """Get the database table name."""
        return "links"
    
    def get_insert_fields(self) -> List[str]:
        """Get fields for INSERT operations."""
        return ["text_source_id", "url", "title", "description", "link_type", "is_active", "metadata"]
    
    def get_update_fields(self) -> List[str]:
        """Get fields for UPDATE operations."""
        return ["url", "title", "description", "link_type", "is_active", "metadata"]
    
    def validate(self) -> None:
        """Validate link data."""
        if not self.text_source_id or self.text_source_id <= 0:
            raise ValidationError("Text source ID is required and must be positive", "text_source_id", self.text_source_id)
        
        if not self.url or not self.url.strip():
            raise ValidationError("Link URL is required", "url", self.url)
        
        if len(self.url) > 500:
            raise ValidationError("Link URL must be 500 characters or less", "url", self.url)
        
        # Basic URL validation
        try:
            parsed = urlparse(self.url)
            if not parsed.scheme or not parsed.netloc:
                raise ValidationError("Invalid URL format", "url", self.url)
        except Exception:
            raise ValidationError("Invalid URL format", "url", self.url)
        
        if self.title and len(self.title) > 255:
            raise ValidationError("Link title must be 255 characters or less", "title", self.title)
        
        if self.description and len(self.description) > 1000:
            raise ValidationError("Link description must be 1000 characters or less", "description", self.description)
        
        if self.link_type and len(self.link_type) > 50:
            raise ValidationError("Link type must be 50 characters or less", "link_type", self.link_type)
    
    def get_domain(self) -> Optional[str]:
        """Get the domain from the URL."""
        try:
            parsed = urlparse(self.url)
            return parsed.netloc
        except Exception:
            return None
    
    def get_scheme(self) -> Optional[str]:
        """Get the scheme (protocol) from the URL."""
        try:
            parsed = urlparse(self.url)
            return parsed.scheme
        except Exception:
            return None
    
    def is_secure(self) -> bool:
        """Check if the URL uses HTTPS."""
        return self.get_scheme() == 'https'


class LinkRepository:
    """Repository for Link operations."""
    
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
    
    def create(self, link_data: Dict[str, Any]) -> Link:
        """Create a new link."""
        link = Link(**link_data)
        link.validate()
        
        # Verify text source exists
        source_query = "SELECT id FROM text_sources WHERE id = %s"
        source_results = self._execute_query(source_query, (link.text_source_id,))
        if not source_results:
            raise NotFoundError("TextSource", link.text_source_id)
        
        query = """
            INSERT INTO links (text_source_id, url, title, description, link_type, is_active, metadata)
            VALUES (%(text_source_id)s, %(url)s, %(title)s, %(description)s, %(link_type)s, %(is_active)s, %(metadata)s)
            RETURNING id, created_at, updated_at
        """
        
        try:
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, link.get_insert_values())
                    result = cursor.fetchone()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, link.get_insert_values())
                        result = cursor.fetchone()
                        conn.commit()
            
            link.id = result['id']
            link.created_at = result['created_at']
            link.updated_at = result['updated_at']
            
            logger.info(f"Created link with ID: {link.id}")
            return link
            
        except Exception as e:
            logger.error(f"Failed to create link: {e}")
            raise DatabaseError(f"Failed to create link: {e}", e)
    
    def get_by_id(self, link_id: int) -> Link:
        """Get link by ID."""
        query = "SELECT * FROM links WHERE id = %s"
        results = self._execute_query(query, (link_id,))
        
        if not results:
            raise NotFoundError("Link", link_id)
        
        return Link.from_dict(results[0])
    
    def get_by_source_id(self, text_source_id: int, limit: int = 100, offset: int = 0) -> List[Link]:
        """Get all links for a text source."""
        query = """
            SELECT * FROM links 
            WHERE text_source_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (text_source_id, limit, offset))
        return [Link.from_dict(row) for row in results]
    
    def get_active_by_source_id(self, text_source_id: int, limit: int = 100, offset: int = 0) -> List[Link]:
        """Get all active links for a text source."""
        query = """
            SELECT * FROM links 
            WHERE text_source_id = %s AND is_active = true
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (text_source_id, limit, offset))
        return [Link.from_dict(row) for row in results]
    
    def get_by_type(self, text_source_id: int, link_type: str) -> List[Link]:
        """Get links by type for a text source."""
        query = """
            SELECT * FROM links 
            WHERE text_source_id = %s AND link_type = %s 
            ORDER BY created_at DESC
        """
        results = self._execute_query(query, (text_source_id, link_type))
        return [Link.from_dict(row) for row in results]
    
    def get_by_project_type(self, project_id: int, link_type: str) -> List[Link]:
        """Get all links of a specific type for a project."""
        query = """
            SELECT l.* FROM links l
            JOIN text_sources ts ON l.text_source_id = ts.id
            WHERE ts.project_id = %s AND l.link_type = %s AND l.is_active = true
            ORDER BY l.created_at DESC
        """
        results = self._execute_query(query, (project_id, link_type))
        return [Link.from_dict(row) for row in results]
    
    def get_by_domain(self, domain: str, limit: int = 100) -> List[Link]:
        """Get links by domain."""
        query = """
            SELECT * FROM links 
            WHERE url LIKE %s AND is_active = true
            ORDER BY created_at DESC 
            LIMIT %s
        """
        domain_pattern = f"%{domain}%"
        results = self._execute_query(query, (domain_pattern, limit))
        return [Link.from_dict(row) for row in results]
    
    def search_by_title_or_description(self, search_term: str, limit: int = 100) -> List[Link]:
        """Search links by title or description."""
        search_pattern = f"%{search_term}%"
        query = """
            SELECT * FROM links 
            WHERE (title ILIKE %s OR description ILIKE %s) AND is_active = true
            ORDER BY created_at DESC 
            LIMIT %s
        """
        results = self._execute_query(query, (search_pattern, search_pattern, limit))
        return [Link.from_dict(row) for row in results]
    
    def list(self, active_only: bool = True, limit: int = 100, offset: int = 0) -> List[Link]:
        """List all links with pagination."""
        if active_only:
            query = """
                SELECT * FROM links 
                WHERE is_active = true
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """
        else:
            query = """
                SELECT * FROM links 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """
        
        results = self._execute_query(query, (limit, offset))
        return [Link.from_dict(row) for row in results]
    
    def update(self, link_id: int, update_data: Dict[str, Any]) -> Link:
        """Update link by ID."""
        # Get existing link
        existing_link = self.get_by_id(link_id)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(existing_link, key) and key != 'text_source_id':  # Don't allow text_source_id changes
                setattr(existing_link, key, value)
        
        existing_link.validate()
        
        query = """
            UPDATE links 
            SET url = %(url)s, title = %(title)s, description = %(description)s,
                link_type = %(link_type)s, is_active = %(is_active)s, metadata = %(metadata)s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING updated_at
        """
        
        try:
            update_values = existing_link.get_update_values()
            update_values['id'] = link_id
            
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
            
            existing_link.updated_at = result['updated_at']
            
            logger.info(f"Updated link with ID: {link_id}")
            return existing_link
            
        except Exception as e:
            logger.error(f"Failed to update link {link_id}: {e}")
            raise DatabaseError(f"Failed to update link: {e}", e)
    
    def delete(self, link_id: int) -> bool:
        """Delete link by ID."""
        # Check if link exists
        self.get_by_id(link_id)
        
        query = "DELETE FROM links WHERE id = %s"
        
        try:
            affected_rows = self._execute_command(query, (link_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted link with ID: {link_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete link {link_id}: {e}")
            raise DatabaseError(f"Failed to delete link: {e}", e)
    
    def deactivate(self, link_id: int) -> bool:
        """Deactivate a link instead of deleting it."""
        return self.update(link_id, {"is_active": False}) is not None
    
    def activate(self, link_id: int) -> bool:
        """Activate a previously deactivated link."""
        return self.update(link_id, {"is_active": True}) is not None
    
    def get_available_types(self, text_source_id: Optional[int] = None) -> List[str]:
        """Get list of available link types."""
        if text_source_id:
            query = """
                SELECT DISTINCT link_type FROM links 
                WHERE text_source_id = %s 
                ORDER BY link_type
            """
            params = (text_source_id,)
        else:
            query = "SELECT DISTINCT link_type FROM links ORDER BY link_type"
            params = None
        
        results = self._execute_query(query, params)
        return [row['link_type'] for row in results]
    
    def get_statistics(self, text_source_id: Optional[int] = None) -> Dict[str, Any]:
        """Get link statistics."""
        if text_source_id:
            query = """
                SELECT 
                    COUNT(*) as total_links,
                    COUNT(*) FILTER (WHERE is_active = true) as active_links,
                    COUNT(*) FILTER (WHERE is_active = false) as inactive_links,
                    COUNT(DISTINCT link_type) as type_count,
                    COUNT(*) FILTER (WHERE url LIKE 'https://%') as secure_links
                FROM links 
                WHERE text_source_id = %s
            """
            params = (text_source_id,)
        else:
            query = """
                SELECT 
                    COUNT(*) as total_links,
                    COUNT(*) FILTER (WHERE is_active = true) as active_links,
                    COUNT(*) FILTER (WHERE is_active = false) as inactive_links,
                    COUNT(DISTINCT link_type) as type_count,
                    COUNT(*) FILTER (WHERE url LIKE 'https://%') as secure_links
                FROM links
            """
            params = None
        
        results = self._execute_query(query, params)
        
        if not results:
            return {
                'total_links': 0,
                'active_links': 0,
                'inactive_links': 0,
                'type_count': 0,
                'secure_links': 0
            }
        
        stats = results[0]
        return {
            'total_links': stats['total_links'] or 0,
            'active_links': stats['active_links'] or 0,
            'inactive_links': stats['inactive_links'] or 0,
            'type_count': stats['type_count'] or 0,
            'secure_links': stats['secure_links'] or 0
        }
    
    def bulk_create(self, links_data: List[Dict[str, Any]]) -> List[Link]:
        """Create multiple links in a single operation."""
        if not links_data:
            return []
        
        links = []
        for link_data in links_data:
            link = Link(**link_data)
            link.validate()
            links.append(link)
        
        # Verify all text sources exist
        source_ids = list(set(l.text_source_id for l in links))
        source_query = f"SELECT id FROM text_sources WHERE id IN ({','.join(['%s'] * len(source_ids))})"
        source_results = self._execute_query(source_query, tuple(source_ids))
        existing_source_ids = {row['id'] for row in source_results}
        
        for l in links:
            if l.text_source_id not in existing_source_ids:
                raise NotFoundError("TextSource", l.text_source_id)
        
        # Build bulk insert query
        query = """
            INSERT INTO links (text_source_id, url, title, description, link_type, is_active, metadata)
            VALUES %s
            RETURNING id, title, created_at, updated_at
        """
        
        try:
            values = []
            for link in links:
                insert_values = link.get_insert_values()
                values.append((
                    insert_values['text_source_id'],
                    insert_values['url'],
                    insert_values['title'],
                    insert_values['description'],
                    insert_values['link_type'],
                    insert_values['is_active'],
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
            
            # Update link objects with returned data
            for i, result in enumerate(results):
                links[i].id = result['id']
                links[i].created_at = result['created_at']
                links[i].updated_at = result['updated_at']
            
            logger.info(f"Created {len(links)} links in bulk operation")
            return links
            
        except Exception as e:
            logger.error(f"Failed to bulk create links: {e}")
            raise DatabaseError(f"Failed to bulk create links: {e}", e)
    
    def bulk_deactivate_by_domain(self, domain: str) -> int:
        """Deactivate all links from a specific domain."""
        query = """
            UPDATE links 
            SET is_active = false, updated_at = CURRENT_TIMESTAMP
            WHERE url LIKE %s AND is_active = true
        """
        domain_pattern = f"%{domain}%"
        
        try:
            affected_rows = self._execute_command(query, (domain_pattern,))
            logger.info(f"Deactivated {affected_rows} links from domain: {domain}")
            return affected_rows
            
        except Exception as e:
            logger.error(f"Failed to bulk deactivate links from domain {domain}: {e}")
            raise DatabaseError(f"Failed to bulk deactivate links: {e}", e)
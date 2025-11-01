"""Project model and repository."""

import logging
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from psycopg2.extras import RealDictCursor
from ..core.base_model import BaseModel
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError


logger = logging.getLogger(__name__)


@dataclass
class Project(BaseModel):
    """Project model representing a project entity."""
    
    name: str = ""
    description: str = ""
    
    def get_table_name(self) -> str:
        """Get the database table name."""
        return "projects"
    
    def get_insert_fields(self) -> List[str]:
        """Get fields for INSERT operations."""
        return ["name", "description", "metadata"]
    
    def get_update_fields(self) -> List[str]:
        """Get fields for UPDATE operations."""
        return ["name", "description", "metadata"]
    
    def validate(self) -> None:
        """Validate project data."""
        if not self.name or not self.name.strip():
            raise ValidationError("Project name is required", "name", self.name)
        
        if len(self.name) > 255:
            raise ValidationError("Project name must be 255 characters or less", "name", self.name)
        
        if self.description and len(self.description) > 10000:
            raise ValidationError("Project description must be 10000 characters or less", "description", self.description)


class ProjectRepository:
    """Repository for Project operations."""
    
    def __init__(self, db_handler, connection=None):
        """Initialize repository with database handler."""
        self.db_handler = db_handler
        self.connection = connection  # For transaction support
    
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
    
    def create(self, project_data: Dict[str, Any]) -> Project:
        """Create a new project."""
        project = Project(**project_data)
        project.validate()
        
        query = """
            INSERT INTO projects (name, description, metadata)
            VALUES (%(name)s, %(description)s, %(metadata)s)
            RETURNING id, created_at, updated_at
        """
        
        try:
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, project.get_insert_values())
                    result = cursor.fetchone()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, project.get_insert_values())
                        result = cursor.fetchone()
                        conn.commit()
            
            project.id = result['id']
            project.created_at = result['created_at']
            project.updated_at = result['updated_at']
            
            logger.info(f"Created project with ID: {project.id}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to create project: {e}")
            raise DatabaseError(f"Failed to create project: {e}", e)
    
    def get_by_id(self, project_id: int) -> Project:
        """Get project by ID."""
        query = "SELECT * FROM projects WHERE id = %s"
        results = self._execute_query(query, (project_id,))
        
        if not results:
            raise NotFoundError("Project", project_id)
        
        return Project.from_dict(results[0])
    
    def get_by_name(self, name: str) -> Optional[Project]:
        """Get project by name."""
        query = "SELECT * FROM projects WHERE name = %s"
        results = self._execute_query(query, (name,))
        
        if not results:
            return None
        
        return Project.from_dict(results[0])
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Project]:
        """List all projects with pagination."""
        query = """
            SELECT * FROM projects 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (limit, offset))
        return [Project.from_dict(row) for row in results]
    
    def search(self, search_term: str, limit: int = 100) -> List[Project]:
        """Search projects by name or description."""
        query = """
            SELECT * FROM projects 
            WHERE name ILIKE %s OR description ILIKE %s
            ORDER BY created_at DESC 
            LIMIT %s
        """
        search_pattern = f"%{search_term}%"
        results = self._execute_query(query, (search_pattern, search_pattern, limit))
        return [Project.from_dict(row) for row in results]
    
    def update(self, project_id: int, update_data: Dict[str, Any]) -> Project:
        """Update project by ID."""
        # Get existing project
        existing_project = self.get_by_id(project_id)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(existing_project, key):
                setattr(existing_project, key, value)
        
        existing_project.validate()
        
        query = """
            UPDATE projects 
            SET name = %(name)s, description = %(description)s, 
                metadata = %(metadata)s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING updated_at
        """
        
        try:
            update_values = existing_project.get_update_values()
            update_values['id'] = project_id
            
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
            
            existing_project.updated_at = result['updated_at']
            
            logger.info(f"Updated project with ID: {project_id}")
            return existing_project
            
        except Exception as e:
            logger.error(f"Failed to update project {project_id}: {e}")
            raise DatabaseError(f"Failed to update project: {e}", e)
    
    def delete(self, project_id: int) -> bool:
        """Delete project by ID (cascades to related data)."""
        # Check if project exists
        self.get_by_id(project_id)
        
        query = "DELETE FROM projects WHERE id = %s"
        
        try:
            affected_rows = self._execute_command(query, (project_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted project with ID: {project_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete project {project_id}: {e}")
            raise DatabaseError(f"Failed to delete project: {e}", e)
    
    def get_statistics(self, project_id: int) -> Dict[str, Any]:
        """Get project statistics."""
        query = """
            SELECT 
                p.id,
                p.name,
                COUNT(DISTINCT ts.id) as source_count,
                COUNT(DISTINCT s.id) as summary_count,
                COUNT(DISTINCT t.id) as translation_count,
                COUNT(DISTINCT v.id) as video_count,
                COUNT(DISTINCT l.id) as link_count,
                ARRAY_AGG(DISTINCT t.language_code) FILTER (WHERE t.language_code IS NOT NULL) as languages
            FROM projects p
            LEFT JOIN text_sources ts ON p.id = ts.project_id
            LEFT JOIN summaries s ON ts.id = s.text_source_id
            LEFT JOIN translations t ON ts.id = t.text_source_id
            LEFT JOIN videos v ON ts.id = v.text_source_id
            LEFT JOIN links l ON ts.id = l.text_source_id
            WHERE p.id = %s
            GROUP BY p.id, p.name
        """
        
        results = self._execute_query(query, (project_id,))
        
        if not results:
            raise NotFoundError("Project", project_id)
        
        stats = results[0]
        return {
            'project_id': stats['id'],
            'project_name': stats['name'],
            'source_count': stats['source_count'] or 0,
            'summary_count': stats['summary_count'] or 0,
            'translation_count': stats['translation_count'] or 0,
            'video_count': stats['video_count'] or 0,
            'link_count': stats['link_count'] or 0,
            'languages': [lang for lang in (stats['languages'] or []) if lang]
        }
    
    def bulk_create(self, projects_data: List[Dict[str, Any]]) -> List[Project]:
        """Create multiple projects in a single operation."""
        if not projects_data:
            return []
        
        projects = []
        for project_data in projects_data:
            project = Project(**project_data)
            project.validate()
            projects.append(project)
        
        # Build bulk insert query
        query = """
            INSERT INTO projects (name, description, metadata)
            VALUES %s
            RETURNING id, name, created_at, updated_at
        """
        
        try:
            values = []
            for project in projects:
                insert_values = project.get_insert_values()
                values.append((
                    insert_values['name'],
                    insert_values['description'],
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
            
            # Update project objects with returned data
            for i, result in enumerate(results):
                projects[i].id = result['id']
                projects[i].created_at = result['created_at']
                projects[i].updated_at = result['updated_at']
            
            logger.info(f"Created {len(projects)} projects in bulk operation")
            return projects
            
        except Exception as e:
            logger.error(f"Failed to bulk create projects: {e}")
            raise DatabaseError(f"Failed to bulk create projects: {e}", e)
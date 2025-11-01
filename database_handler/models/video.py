"""Video model and repository for video file references."""

import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from psycopg2.extras import RealDictCursor
from ..core.base_model import BaseModel
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError


logger = logging.getLogger(__name__)


@dataclass
class Video(BaseModel):
    """Video model representing a video file reference entity."""
    
    text_source_id: int = 0
    title: Optional[str] = None
    file_path: str = ""
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    duration: Optional[int] = None  # Duration in seconds
    format: Optional[str] = None
    thumbnail_path: Optional[str] = None
    
    def get_table_name(self) -> str:
        """Get the database table name."""
        return "videos"
    
    def get_insert_fields(self) -> List[str]:
        """Get fields for INSERT operations."""
        return ["text_source_id", "title", "file_path", "file_url", "file_size", 
                "duration", "format", "thumbnail_path", "metadata"]
    
    def get_update_fields(self) -> List[str]:
        """Get fields for UPDATE operations."""
        return ["title", "file_path", "file_url", "file_size", 
                "duration", "format", "thumbnail_path", "metadata"]
    
    def validate(self) -> None:
        """Validate video data."""
        if not self.text_source_id or self.text_source_id <= 0:
            raise ValidationError("Text source ID is required and must be positive", "text_source_id", self.text_source_id)
        
        if not self.file_path or not self.file_path.strip():
            raise ValidationError("Video file path is required", "file_path", self.file_path)
        
        if len(self.file_path) > 500:
            raise ValidationError("Video file path must be 500 characters or less", "file_path", self.file_path)
        
        if self.title and len(self.title) > 255:
            raise ValidationError("Video title must be 255 characters or less", "title", self.title)
        
        if self.file_url and len(self.file_url) > 500:
            raise ValidationError("Video file URL must be 500 characters or less", "file_url", self.file_url)
        
        if self.file_size is not None and self.file_size < 0:
            raise ValidationError("Video file size must be non-negative", "file_size", self.file_size)
        
        if self.duration is not None and self.duration < 0:
            raise ValidationError("Video duration must be non-negative", "duration", self.duration)
        
        if self.format and len(self.format) > 20:
            raise ValidationError("Video format must be 20 characters or less", "format", self.format)
        
        if self.thumbnail_path and len(self.thumbnail_path) > 500:
            raise ValidationError("Thumbnail path must be 500 characters or less", "thumbnail_path", self.thumbnail_path)
    
    def file_exists(self) -> bool:
        """Check if the video file exists on disk."""
        return os.path.exists(self.file_path) if self.file_path else False
    
    def thumbnail_exists(self) -> bool:
        """Check if the thumbnail file exists on disk."""
        return os.path.exists(self.thumbnail_path) if self.thumbnail_path else False
    
    def get_file_size_mb(self) -> Optional[float]:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024) if self.file_size else None
    
    def get_duration_formatted(self) -> Optional[str]:
        """Get duration in HH:MM:SS format."""
        if self.duration is None:
            return None
        
        hours = self.duration // 3600
        minutes = (self.duration % 3600) // 60
        seconds = self.duration % 60
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class VideoRepository:
    """Repository for Video operations."""
    
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
    
    def create(self, video_data: Dict[str, Any]) -> Video:
        """Create a new video reference."""
        video = Video(**video_data)
        video.validate()
        
        # Verify text source exists
        source_query = "SELECT id FROM text_sources WHERE id = %s"
        source_results = self._execute_query(source_query, (video.text_source_id,))
        if not source_results:
            raise NotFoundError("TextSource", video.text_source_id)
        
        query = """
            INSERT INTO videos (text_source_id, title, file_path, file_url, file_size, 
                              duration, format, thumbnail_path, metadata)
            VALUES (%(text_source_id)s, %(title)s, %(file_path)s, %(file_url)s, %(file_size)s,
                    %(duration)s, %(format)s, %(thumbnail_path)s, %(metadata)s)
            RETURNING id, created_at, updated_at
        """
        
        try:
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, video.get_insert_values())
                    result = cursor.fetchone()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, video.get_insert_values())
                        result = cursor.fetchone()
                        conn.commit()
            
            video.id = result['id']
            video.created_at = result['created_at']
            video.updated_at = result['updated_at']
            
            logger.info(f"Created video with ID: {video.id}")
            return video
            
        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            raise DatabaseError(f"Failed to create video: {e}", e)
    
    def get_by_id(self, video_id: int) -> Video:
        """Get video by ID."""
        query = "SELECT * FROM videos WHERE id = %s"
        results = self._execute_query(query, (video_id,))
        
        if not results:
            raise NotFoundError("Video", video_id)
        
        return Video.from_dict(results[0])
    
    def get_by_source_id(self, text_source_id: int, limit: int = 100, offset: int = 0) -> List[Video]:
        """Get all videos for a text source."""
        query = """
            SELECT * FROM videos 
            WHERE text_source_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (text_source_id, limit, offset))
        return [Video.from_dict(row) for row in results]
    
    def get_by_format(self, format: str, limit: int = 100) -> List[Video]:
        """Get videos by format."""
        query = """
            SELECT * FROM videos 
            WHERE format = %s 
            ORDER BY created_at DESC 
            LIMIT %s
        """
        results = self._execute_query(query, (format, limit))
        return [Video.from_dict(row) for row in results]
    
    def get_by_project_id(self, project_id: int, limit: int = 100, offset: int = 0) -> List[Video]:
        """Get all videos for a project."""
        query = """
            SELECT v.* FROM videos v
            JOIN text_sources ts ON v.text_source_id = ts.id
            WHERE ts.project_id = %s
            ORDER BY v.created_at DESC
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (project_id, limit, offset))
        return [Video.from_dict(row) for row in results]
    
    def search_by_title(self, search_term: str, limit: int = 100) -> List[Video]:
        """Search videos by title."""
        search_pattern = f"%{search_term}%"
        query = """
            SELECT * FROM videos 
            WHERE title ILIKE %s
            ORDER BY created_at DESC 
            LIMIT %s
        """
        results = self._execute_query(query, (search_pattern, limit))
        return [Video.from_dict(row) for row in results]
    
    def get_by_duration_range(self, min_duration: int, max_duration: int, limit: int = 100) -> List[Video]:
        """Get videos within a duration range (in seconds)."""
        query = """
            SELECT * FROM videos 
            WHERE duration BETWEEN %s AND %s
            ORDER BY duration ASC
            LIMIT %s
        """
        results = self._execute_query(query, (min_duration, max_duration, limit))
        return [Video.from_dict(row) for row in results]
    
    def get_by_file_size_range(self, min_size: int, max_size: int, limit: int = 100) -> List[Video]:
        """Get videos within a file size range (in bytes)."""
        query = """
            SELECT * FROM videos 
            WHERE file_size BETWEEN %s AND %s
            ORDER BY file_size ASC
            LIMIT %s
        """
        results = self._execute_query(query, (min_size, max_size, limit))
        return [Video.from_dict(row) for row in results]
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Video]:
        """List all videos with pagination."""
        query = """
            SELECT * FROM videos 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (limit, offset))
        return [Video.from_dict(row) for row in results]
    
    def update(self, video_id: int, update_data: Dict[str, Any]) -> Video:
        """Update video by ID."""
        # Get existing video
        existing_video = self.get_by_id(video_id)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(existing_video, key) and key != 'text_source_id':  # Don't allow text_source_id changes
                setattr(existing_video, key, value)
        
        existing_video.validate()
        
        query = """
            UPDATE videos 
            SET title = %(title)s, file_path = %(file_path)s, file_url = %(file_url)s,
                file_size = %(file_size)s, duration = %(duration)s, format = %(format)s,
                thumbnail_path = %(thumbnail_path)s, metadata = %(metadata)s, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING updated_at
        """
        
        try:
            update_values = existing_video.get_update_values()
            update_values['id'] = video_id
            
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
            
            existing_video.updated_at = result['updated_at']
            
            logger.info(f"Updated video with ID: {video_id}")
            return existing_video
            
        except Exception as e:
            logger.error(f"Failed to update video {video_id}: {e}")
            raise DatabaseError(f"Failed to update video: {e}", e)
    
    def delete(self, video_id: int) -> bool:
        """Delete video by ID."""
        # Check if video exists
        self.get_by_id(video_id)
        
        query = "DELETE FROM videos WHERE id = %s"
        
        try:
            affected_rows = self._execute_command(query, (video_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted video with ID: {video_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete video {video_id}: {e}")
            raise DatabaseError(f"Failed to delete video: {e}", e)
    
    def get_available_formats(self, text_source_id: Optional[int] = None) -> List[str]:
        """Get list of available video formats."""
        if text_source_id:
            query = """
                SELECT DISTINCT format FROM videos 
                WHERE text_source_id = %s AND format IS NOT NULL
                ORDER BY format
            """
            params = (text_source_id,)
        else:
            query = "SELECT DISTINCT format FROM videos WHERE format IS NOT NULL ORDER BY format"
            params = None
        
        results = self._execute_query(query, params)
        return [row['format'] for row in results]
    
    def get_statistics(self, text_source_id: Optional[int] = None) -> Dict[str, Any]:
        """Get video statistics."""
        if text_source_id:
            query = """
                SELECT 
                    COUNT(*) as video_count,
                    AVG(duration) as avg_duration,
                    SUM(file_size) as total_size,
                    MIN(duration) as min_duration,
                    MAX(duration) as max_duration,
                    COUNT(DISTINCT format) as format_count
                FROM videos 
                WHERE text_source_id = %s
            """
            params = (text_source_id,)
        else:
            query = """
                SELECT 
                    COUNT(*) as video_count,
                    AVG(duration) as avg_duration,
                    SUM(file_size) as total_size,
                    MIN(duration) as min_duration,
                    MAX(duration) as max_duration,
                    COUNT(DISTINCT format) as format_count
                FROM videos
            """
            params = None
        
        results = self._execute_query(query, params)
        
        if not results:
            return {
                'video_count': 0,
                'avg_duration': 0,
                'total_size': 0,
                'min_duration': 0,
                'max_duration': 0,
                'format_count': 0
            }
        
        stats = results[0]
        return {
            'video_count': stats['video_count'] or 0,
            'avg_duration': float(stats['avg_duration']) if stats['avg_duration'] else 0,
            'total_size': stats['total_size'] or 0,
            'min_duration': stats['min_duration'] or 0,
            'max_duration': stats['max_duration'] or 0,
            'format_count': stats['format_count'] or 0
        }
    
    def bulk_create(self, videos_data: List[Dict[str, Any]]) -> List[Video]:
        """Create multiple videos in a single operation."""
        if not videos_data:
            return []
        
        videos = []
        for video_data in videos_data:
            video = Video(**video_data)
            video.validate()
            videos.append(video)
        
        # Verify all text sources exist
        source_ids = list(set(v.text_source_id for v in videos))
        source_query = f"SELECT id FROM text_sources WHERE id IN ({','.join(['%s'] * len(source_ids))})"
        source_results = self._execute_query(source_query, tuple(source_ids))
        existing_source_ids = {row['id'] for row in source_results}
        
        for v in videos:
            if v.text_source_id not in existing_source_ids:
                raise NotFoundError("TextSource", v.text_source_id)
        
        # Build bulk insert query
        query = """
            INSERT INTO videos (text_source_id, title, file_path, file_url, file_size, 
                              duration, format, thumbnail_path, metadata)
            VALUES %s
            RETURNING id, title, created_at, updated_at
        """
        
        try:
            values = []
            for video in videos:
                insert_values = video.get_insert_values()
                values.append((
                    insert_values['text_source_id'],
                    insert_values['title'],
                    insert_values['file_path'],
                    insert_values['file_url'],
                    insert_values['file_size'],
                    insert_values['duration'],
                    insert_values['format'],
                    insert_values['thumbnail_path'],
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
            
            # Update video objects with returned data
            for i, result in enumerate(results):
                videos[i].id = result['id']
                videos[i].created_at = result['created_at']
                videos[i].updated_at = result['updated_at']
            
            logger.info(f"Created {len(videos)} videos in bulk operation")
            return videos
            
        except Exception as e:
            logger.error(f"Failed to bulk create videos: {e}")
            raise DatabaseError(f"Failed to bulk create videos: {e}", e)
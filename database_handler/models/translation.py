"""Translation model and repository for tokenized translation data."""

import logging
import json
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from psycopg2.extras import RealDictCursor
from ..core.base_model import BaseModel
from ..core.exceptions import NotFoundError, ValidationError, DatabaseError


logger = logging.getLogger(__name__)


@dataclass
class Translation(BaseModel):
    """Translation model representing a tokenized translation entity."""
    
    text_source_id: int = 0
    language_code: str = ""
    title: Optional[str] = None
    tokens: List[Dict[str, Any]] = None
    original_text: Optional[str] = None
    
    def __post_init__(self):
        """Initialize tokens as empty list if None."""
        if self.tokens is None:
            self.tokens = []
    
    def get_table_name(self) -> str:
        """Get the database table name."""
        return "translations"
    
    def get_insert_fields(self) -> List[str]:
        """Get fields for INSERT operations."""
        return ["text_source_id", "language_code", "title", "tokens", "original_text", "metadata"]
    
    def get_update_fields(self) -> List[str]:
        """Get fields for UPDATE operations."""
        return ["title", "tokens", "original_text", "metadata"]
    
    def validate(self) -> None:
        """Validate translation data."""
        if not self.text_source_id or self.text_source_id <= 0:
            raise ValidationError("Text source ID is required and must be positive", "text_source_id", self.text_source_id)
        
        if not self.language_code or not self.language_code.strip():
            raise ValidationError("Language code is required", "language_code", self.language_code)
        
        if len(self.language_code) > 10:
            raise ValidationError("Language code must be 10 characters or less", "language_code", self.language_code)
        
        if self.title and len(self.title) > 255:
            raise ValidationError("Translation title must be 255 characters or less", "title", self.title)
        
        # Validate tokens structure
        if not self.tokens:
            raise ValidationError("Tokens are required for translation", "tokens", self.tokens)
        
        if not isinstance(self.tokens, list):
            raise ValidationError("Tokens must be a list", "tokens", self.tokens)
        
        for i, token in enumerate(self.tokens):
            if not isinstance(token, dict):
                raise ValidationError(f"Token at index {i} must be a dictionary", "tokens", token)
            
            if 'token' not in token:
                raise ValidationError(f"Token at index {i} must have 'token' field", "tokens", token)
            
            if 'pos' not in token:
                raise ValidationError(f"Token at index {i} must have 'pos' field", "tokens", token)
            
            if not isinstance(token['pos'], int) or token['pos'] < 0:
                raise ValidationError(f"Token position at index {i} must be a non-negative integer", "tokens", token['pos'])
    
    def get_token_text(self) -> str:
        """Get the full text from tokens."""
        if not self.tokens:
            return ""
        
        # Sort tokens by position and join
        sorted_tokens = sorted(self.tokens, key=lambda x: x['pos'])
        return " ".join(token['token'] for token in sorted_tokens)
    
    def add_token(self, token: str, position: int) -> None:
        """Add a token at the specified position."""
        if self.tokens is None:
            self.tokens = []
        
        self.tokens.append({"token": token, "pos": position})
    
    def get_tokens_by_range(self, start_pos: int, end_pos: int) -> List[Dict[str, Any]]:
        """Get tokens within a position range."""
        if not self.tokens:
            return []
        
        return [token for token in self.tokens if start_pos <= token['pos'] <= end_pos]


class TranslationRepository:
    """Repository for Translation operations."""
    
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
    
    def create(self, translation_data: Dict[str, Any]) -> Translation:
        """Create a new translation."""
        translation = Translation(**translation_data)
        translation.validate()
        
        # Verify text source exists
        source_query = "SELECT id FROM text_sources WHERE id = %s"
        source_results = self._execute_query(source_query, (translation.text_source_id,))
        if not source_results:
            raise NotFoundError("TextSource", translation.text_source_id)
        
        query = """
            INSERT INTO translations (text_source_id, language_code, title, tokens, original_text, metadata)
            VALUES (%(text_source_id)s, %(language_code)s, %(title)s, %(tokens)s, %(original_text)s, %(metadata)s)
            RETURNING id, created_at, updated_at
        """
        
        try:
            insert_values = translation.get_insert_values()
            # Convert tokens list to JSON string for PostgreSQL
            insert_values['tokens'] = json.dumps(translation.tokens)
            
            if self.connection:
                with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    cursor.execute(query, insert_values)
                    result = cursor.fetchone()
            else:
                with self.db_handler.get_connection() as conn:
                    with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                        cursor.execute(query, insert_values)
                        result = cursor.fetchone()
                        conn.commit()
            
            translation.id = result['id']
            translation.created_at = result['created_at']
            translation.updated_at = result['updated_at']
            
            logger.info(f"Created translation with ID: {translation.id}")
            return translation
            
        except Exception as e:
            logger.error(f"Failed to create translation: {e}")
            raise DatabaseError(f"Failed to create translation: {e}", e)
    
    def get_by_id(self, translation_id: int) -> Translation:
        """Get translation by ID."""
        query = "SELECT * FROM translations WHERE id = %s"
        results = self._execute_query(query, (translation_id,))
        
        if not results:
            raise NotFoundError("Translation", translation_id)
        
        # Convert JSON tokens back to list
        result = results[0]
        if result['tokens']:
            result['tokens'] = json.loads(result['tokens']) if isinstance(result['tokens'], str) else result['tokens']
        
        return Translation.from_dict(result)
    
    def get_by_source_id(self, text_source_id: int, limit: int = 100, offset: int = 0) -> List[Translation]:
        """Get all translations for a text source."""
        query = """
            SELECT * FROM translations 
            WHERE text_source_id = %s 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (text_source_id, limit, offset))
        
        # Convert JSON tokens back to list for each result
        for result in results:
            if result['tokens']:
                result['tokens'] = json.loads(result['tokens']) if isinstance(result['tokens'], str) else result['tokens']
        
        return [Translation.from_dict(row) for row in results]
    
    def get_by_language(self, text_source_id: int, language_code: str) -> Optional[Translation]:
        """Get translation by text source and language code."""
        query = """
            SELECT * FROM translations 
            WHERE text_source_id = %s AND language_code = %s
            ORDER BY created_at DESC
            LIMIT 1
        """
        results = self._execute_query(query, (text_source_id, language_code))
        
        if not results:
            return None
        
        # Convert JSON tokens back to list
        result = results[0]
        if result['tokens']:
            result['tokens'] = json.loads(result['tokens']) if isinstance(result['tokens'], str) else result['tokens']
        
        return Translation.from_dict(result)
    
    def get_by_project_language(self, project_id: int, language_code: str) -> List[Translation]:
        """Get all translations for a project in a specific language."""
        query = """
            SELECT t.* FROM translations t
            JOIN text_sources ts ON t.text_source_id = ts.id
            WHERE ts.project_id = %s AND t.language_code = %s
            ORDER BY t.created_at DESC
        """
        results = self._execute_query(query, (project_id, language_code))
        
        # Convert JSON tokens back to list for each result
        for result in results:
            if result['tokens']:
                result['tokens'] = json.loads(result['tokens']) if isinstance(result['tokens'], str) else result['tokens']
        
        return [Translation.from_dict(row) for row in results]
    
    def search_tokens(self, search_term: str, language_code: Optional[str] = None, limit: int = 100) -> List[Translation]:
        """Search translations by token content."""
        search_pattern = f"%{search_term}%"
        
        if language_code:
            query = """
                SELECT * FROM translations 
                WHERE language_code = %s AND tokens::text ILIKE %s
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params = (language_code, search_pattern, limit)
        else:
            query = """
                SELECT * FROM translations 
                WHERE tokens::text ILIKE %s
                ORDER BY created_at DESC 
                LIMIT %s
            """
            params = (search_pattern, limit)
        
        results = self._execute_query(query, params)
        
        # Convert JSON tokens back to list for each result
        for result in results:
            if result['tokens']:
                result['tokens'] = json.loads(result['tokens']) if isinstance(result['tokens'], str) else result['tokens']
        
        return [Translation.from_dict(row) for row in results]
    
    def list(self, limit: int = 100, offset: int = 0) -> List[Translation]:
        """List all translations with pagination."""
        query = """
            SELECT * FROM translations 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """
        results = self._execute_query(query, (limit, offset))
        
        # Convert JSON tokens back to list for each result
        for result in results:
            if result['tokens']:
                result['tokens'] = json.loads(result['tokens']) if isinstance(result['tokens'], str) else result['tokens']
        
        return [Translation.from_dict(row) for row in results]
    
    def update(self, translation_id: int, update_data: Dict[str, Any]) -> Translation:
        """Update translation by ID."""
        # Get existing translation
        existing_translation = self.get_by_id(translation_id)
        
        # Update fields
        for key, value in update_data.items():
            if hasattr(existing_translation, key) and key != 'text_source_id':  # Don't allow text_source_id changes
                setattr(existing_translation, key, value)
        
        existing_translation.validate()
        
        query = """
            UPDATE translations 
            SET title = %(title)s, tokens = %(tokens)s, original_text = %(original_text)s,
                metadata = %(metadata)s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %(id)s
            RETURNING updated_at
        """
        
        try:
            update_values = existing_translation.get_update_values()
            update_values['id'] = translation_id
            # Convert tokens list to JSON string for PostgreSQL
            update_values['tokens'] = json.dumps(existing_translation.tokens)
            
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
            
            existing_translation.updated_at = result['updated_at']
            
            logger.info(f"Updated translation with ID: {translation_id}")
            return existing_translation
            
        except Exception as e:
            logger.error(f"Failed to update translation {translation_id}: {e}")
            raise DatabaseError(f"Failed to update translation: {e}", e)
    
    def delete(self, translation_id: int) -> bool:
        """Delete translation by ID."""
        # Check if translation exists
        self.get_by_id(translation_id)
        
        query = "DELETE FROM translations WHERE id = %s"
        
        try:
            affected_rows = self._execute_command(query, (translation_id,))
            
            if affected_rows > 0:
                logger.info(f"Deleted translation with ID: {translation_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete translation {translation_id}: {e}")
            raise DatabaseError(f"Failed to delete translation: {e}", e)
    
    def get_available_languages(self, text_source_id: Optional[int] = None) -> List[str]:
        """Get list of available language codes."""
        if text_source_id:
            query = """
                SELECT DISTINCT language_code FROM translations 
                WHERE text_source_id = %s 
                ORDER BY language_code
            """
            params = (text_source_id,)
        else:
            query = "SELECT DISTINCT language_code FROM translations ORDER BY language_code"
            params = None
        
        results = self._execute_query(query, params)
        return [row['language_code'] for row in results]
    
    def get_token_statistics(self, translation_id: int) -> Dict[str, Any]:
        """Get token statistics for a translation."""
        translation = self.get_by_id(translation_id)
        
        if not translation.tokens:
            return {
                'translation_id': translation_id,
                'token_count': 0,
                'unique_tokens': 0,
                'average_token_length': 0,
                'max_position': 0
            }
        
        tokens = translation.tokens
        token_texts = [token['token'] for token in tokens]
        unique_tokens = set(token_texts)
        
        return {
            'translation_id': translation_id,
            'token_count': len(tokens),
            'unique_tokens': len(unique_tokens),
            'average_token_length': sum(len(token) for token in token_texts) / len(token_texts) if token_texts else 0,
            'max_position': max(token['pos'] for token in tokens) if tokens else 0
        }
    
    def bulk_create(self, translations_data: List[Dict[str, Any]]) -> List[Translation]:
        """Create multiple translations in a single operation."""
        if not translations_data:
            return []
        
        translations = []
        for translation_data in translations_data:
            translation = Translation(**translation_data)
            translation.validate()
            translations.append(translation)
        
        # Verify all text sources exist
        source_ids = list(set(t.text_source_id for t in translations))
        source_query = f"SELECT id FROM text_sources WHERE id IN ({','.join(['%s'] * len(source_ids))})"
        source_results = self._execute_query(source_query, tuple(source_ids))
        existing_source_ids = {row['id'] for row in source_results}
        
        for t in translations:
            if t.text_source_id not in existing_source_ids:
                raise NotFoundError("TextSource", t.text_source_id)
        
        # Build bulk insert query
        query = """
            INSERT INTO translations (text_source_id, language_code, title, tokens, original_text, metadata)
            VALUES %s
            RETURNING id, language_code, created_at, updated_at
        """
        
        try:
            values = []
            for translation in translations:
                insert_values = translation.get_insert_values()
                values.append((
                    insert_values['text_source_id'],
                    insert_values['language_code'],
                    insert_values['title'],
                    json.dumps(translation.tokens),  # Convert to JSON
                    insert_values['original_text'],
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
            
            # Update translation objects with returned data
            for i, result in enumerate(results):
                translations[i].id = result['id']
                translations[i].created_at = result['created_at']
                translations[i].updated_at = result['updated_at']
            
            logger.info(f"Created {len(translations)} translations in bulk operation")
            return translations
            
        except Exception as e:
            logger.error(f"Failed to bulk create translations: {e}")
            raise DatabaseError(f"Failed to bulk create translations: {e}", e)
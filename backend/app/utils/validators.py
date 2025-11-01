"""Input validation utilities."""

import validators
import mimetypes
from typing import Optional
from werkzeug.datastructures import FileStorage


def validate_url(url: str) -> bool:
    """Validate if a string is a valid URL."""
    if not url or not isinstance(url, str):
        return False
    
    url = url.strip()
    if not url:
        return False
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    return validators.url(url)


def validate_file(file: FileStorage) -> Optional[str]:
    """Validate uploaded file. Returns error message if invalid, None if valid."""
    if not file:
        return "No file provided"
    
    if not file.filename:
        return "No filename provided"
    
    filename = file.filename.lower()
    
    # Check file extension
    allowed_extensions = ['.pdf', '.txt', '.md', '.mp4', '.avi', '.mov', '.wmv', '.mp3', '.wav', '.m4a']
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
    
    # Check file size (16MB limit)
    if file.content_length and file.content_length > 16 * 1024 * 1024:
        return "File size exceeds 16MB limit"
    
    return None


def validate_content_length(content: str, max_length: int = 1000000) -> bool:
    """Validate content length."""
    if not isinstance(content, str):
        return False
    
    return len(content) <= max_length


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    import re
    from werkzeug.utils import secure_filename
    
    # Use Werkzeug's secure_filename as base
    safe_name = secure_filename(filename)
    
    # Additional sanitization
    safe_name = re.sub(r'[^\w\-_\.]', '', safe_name)
    safe_name = re.sub(r'\.+', '.', safe_name)  # Remove multiple dots
    
    return safe_name


def validate_api_key(api_key: str) -> bool:
    """Basic validation for API keys."""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Check minimum length and format
    api_key = api_key.strip()
    if len(api_key) < 10:  # Minimum reasonable length
        return False
    
    # Basic format checks (alphanumeric, hyphens, underscores)
    import re
    if not re.match(r'^[a-zA-Z0-9\-_]+$', api_key):
        return False
    
    return True


def validate_database_config(config: dict) -> tuple[bool, str]:
    """Validate database configuration."""
    required_fields = ['host', 'port', 'database', 'username', 'password']
    
    for field in required_fields:
        if field not in config or not config[field]:
            return False, f"Missing required database config: {field}"
    
    # Validate port is integer
    try:
        port = int(config['port'])
        if port < 1 or port > 65535:
            return False, "Database port must be between 1 and 65535"
    except (ValueError, TypeError):
        return False, "Database port must be a valid integer"
    
    return True, "Valid"


def validate_json_data(data: dict, required_fields: list) -> tuple[bool, str]:
    """Validate JSON request data has required fields."""
    if not isinstance(data, dict):
        return False, "Request data must be JSON object"
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
        
        if not data[field] or (isinstance(data[field], str) and not data[field].strip()):
            return False, f"Field '{field}' cannot be empty"
    
    return True, "Valid"


def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube video."""
    if not validate_url(url):
        return False
    
    youtube_domains = [
        'youtube.com', 'www.youtube.com', 'm.youtube.com', 
        'youtu.be', 'gaming.youtube.com'
    ]
    
    from urllib.parse import urlparse
    parsed = urlparse(url.lower())
    return parsed.netloc in youtube_domains


def validate_text_content(content: str, min_length: int = 10) -> tuple[bool, str]:
    """Validate text content for processing."""
    if not content or not isinstance(content, str):
        return False, "Content must be a non-empty string"
    
    content = content.strip()
    if len(content) < min_length:
        return False, f"Content must be at least {min_length} characters long"
    
    # Check for common file headers that might indicate binary content
    binary_indicators = [b'\x00', b'\xFF\xD8', b'\x89PNG', b'%PDF']
    content_bytes = content.encode('utf-8', errors='ignore')
    
    for indicator in binary_indicators:
        if indicator in content_bytes[:100]:  # Check first 100 bytes
            return False, "Content appears to be binary data"
    
    return True, "Valid"
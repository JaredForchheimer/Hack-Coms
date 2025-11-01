# Database Handler for Project Management System

A comprehensive PostgreSQL database handler for managing projects with text sources, translations, summaries, videos, and links in a hierarchical structure.

## Features

- **Hierarchical Data Structure**: Projects → Text Sources → (Summaries, Translations, Videos, Links)
- **Tokenized Translation Support**: Store and manage tokenized translation data with position indices
- **Connection Pooling**: Efficient PostgreSQL connection management with psycopg2
- **Transaction Support**: Full ACID transaction support with context managers
- **Bulk Operations**: Efficient bulk insert and update operations
- **Comprehensive Validation**: Input validation with custom exceptions
- **Search & Filtering**: Advanced search capabilities across all data types
- **Flexible Configuration**: Environment-based and file-based configuration
- **Production Ready**: Logging, error handling, and performance optimization

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your PostgreSQL database and configure environment variables:
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=project_db
export DB_USER=your_username
export DB_PASSWORD=your_password
```

3. Initialize the database:
```bash
python database_handler/scripts/init_db.py
```

4. (Optional) Seed with sample data:
```bash
python database_handler/scripts/seed_data.py
```

## Quick Start

```python
from database_handler import DatabaseHandler, DatabaseConfig
from database_handler.config import load_config_from_env

# Load configuration from environment
config = load_config_from_env()

# Create and initialize database handler
with DatabaseHandler(config) as db:
    db.initialize()
    
    # Create a project
    project = db.projects.create({
        "name": "My Project",
        "description": "A sample project",
        "metadata": {"department": "Research"}
    })
    
    # Create a text source
    text_source = db.text_sources.create({
        "project_id": project.id,
        "title": "Research Document",
        "content": "This is the main content...",
        "source_type": "document"
    })
    
    # Create a tokenized translation
    translation = db.translations.create({
        "text_source_id": text_source.id,
        "language_code": "es",
        "title": "Documento de Investigación",
        "tokens": [
            {"token": "Este", "pos": 0},
            {"token": "es", "pos": 1},
            {"token": "el", "pos": 2},
            {"token": "contenido", "pos": 3}
        ],
        "original_text": "Este es el contenido"
    })
```

## Database Schema

The system uses a hierarchical PostgreSQL schema:

```
Projects (1) → Text Sources (N)
                    ↓
    ┌─────────────────────────────────────┐
    │                                     │
    ▼               ▼               ▼     ▼
Summaries    Translations    Videos   Links
```

### Core Tables

- **projects**: Main project entities
- **text_sources**: Text content associated with projects
- **summaries**: Summaries of text sources
- **translations**: Tokenized translations with position data
- **videos**: Video file references and metadata
- **links**: External links and references

## API Reference

### Projects

```python
# Create project
project = db.projects.create(project_data)

# Get project by ID
project = db.projects.get_by_id(project_id)

# Search projects
projects = db.projects.search("search term")

# Get project statistics
stats = db.projects.get_statistics(project_id)

# Update project
project = db.projects.update(project_id, update_data)

# Delete project (cascades to all related data)
db.projects.delete(project_id)
```

### Text Sources

```python
# Create text source
text_source = db.text_sources.create(source_data)

# Get sources by project
sources = db.text_sources.get_by_project_id(project_id)

# Search content
sources = db.text_sources.search_content("search term")

# Get by type
sources = db.text_sources.get_by_type(project_id, "document")
```

### Translations

```python
# Create tokenized translation
translation = db.translations.create({
    "text_source_id": source_id,
    "language_code": "es",
    "tokens": [
        {"token": "palabra", "pos": 0},
        {"token": "siguiente", "pos": 1}
    ]
})

# Get by language
translation = db.translations.get_by_language(source_id, "es")

# Search tokens
translations = db.translations.search_tokens("search term")

# Get available languages
languages = db.translations.get_available_languages()
```

### Videos

```python
# Create video reference
video = db.videos.create({
    "text_source_id": source_id,
    "title": "Project Video",
    "file_path": "/path/to/video.mp4",
    "duration": 1800,  # seconds
    "format": "mp4"
})

# Get by format
videos = db.videos.get_by_format("mp4")

# Get statistics
stats = db.videos.get_statistics()
```

### Links

```python
# Create link
link = db.links.create({
    "text_source_id": source_id,
    "url": "https://example.com",
    "title": "Reference Link",
    "link_type": "reference"
})

# Get active links
links = db.links.get_active_by_source_id(source_id)

# Deactivate link
db.links.deactivate(link_id)
```

## Advanced Features

### Transactions

```python
with db.transaction() as tx:
    project = tx.projects.create(project_data)
    source = tx.text_sources.create(source_data)
    # All operations commit together or rollback on error
```

### Bulk Operations

```python
# Bulk create multiple items
projects = db.projects.bulk_create(projects_data_list)
sources = db.text_sources.bulk_create(sources_data_list)
```

### Error Handling

```python
from database_handler.core.exceptions import NotFoundError, ValidationError

try:
    project = db.projects.get_by_id(999)
except NotFoundError:
    print("Project not found")

try:
    project = db.projects.create({"name": ""})  # Invalid
except ValidationError as e:
    print(f"Validation error: {e}")
```

## Configuration

### Environment Variables

```bash
# Database Connection
DB_HOST=localhost
DB_PORT=5432
DB_NAME=project_db
DB_USER=username
DB_PASSWORD=password

# Connection Pool
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_TIMEOUT=30

# SSL and Security
DB_SSL_MODE=prefer
DB_CONNECT_TIMEOUT=10
```

### Configuration File

Create a YAML configuration file:

```yaml
database:
  host: localhost
  port: 5432
  database: project_db
  username: postgres
  password: your_password
  pool_size: 10
  max_overflow: 20
```

Load with:

```python
from database_handler.config import load_config_from_file
config = load_config_from_file("config.yaml")
```

## Scripts

### Database Initialization

```bash
# Initialize database with tables and indexes
python database_handler/scripts/init_db.py

# Check database status
python database_handler/scripts/init_db.py --check

# Drop and recreate tables
python database_handler/scripts/init_db.py --drop
```

### Sample Data

```bash
# Seed with sample data
python database_handler/scripts/seed_data.py

# Clear existing data and reseed
python database_handler/scripts/seed_data.py --clear
```

## Examples

See [`example_usage.py`](example_usage.py) for comprehensive usage examples including:

- Basic CRUD operations
- Advanced queries and statistics
- Transaction usage
- Bulk operations
- Error handling
- Search and filtering

## Architecture

The database handler follows these design patterns:

- **Repository Pattern**: Each model has a dedicated repository class
- **Unit of Work**: Transaction support with automatic rollback
- **Factory Pattern**: Model creation and validation
- **Connection Pooling**: Efficient database connection management

## Performance Considerations

- **Indexes**: Strategic indexes on commonly queried fields
- **Connection Pooling**: Reuse database connections efficiently
- **Bulk Operations**: Use bulk inserts for large datasets
- **Pagination**: Built-in pagination support for large result sets
- **JSONB**: Efficient storage and querying of metadata

## Security

- **SQL Injection Prevention**: Parameterized queries throughout
- **Input Validation**: Comprehensive validation before database operations
- **Connection Security**: SSL/TLS support for database connections
- **Error Handling**: Secure error messages without exposing internals

## Testing

Run the example script to test functionality:

```bash
python example_usage.py
```

## Contributing

1. Follow the existing code structure and patterns
2. Add comprehensive validation to new models
3. Include proper error handling and logging
4. Update documentation for new features
5. Test with the provided example scripts

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:

1. Check the example usage scripts
2. Review the architecture documentation
3. Examine the database schema design
4. Test with the provided sample data

---

**Note**: This database handler is designed for PostgreSQL and requires proper database setup and configuration before use.
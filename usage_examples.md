# Database Handler Usage Examples

## Basic Setup and Configuration

```python
from database_handler import DatabaseHandler
from database_handler.config import DatabaseConfig

# Initialize database configuration
config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="project_db",
    username="your_username",
    password="your_password",
    pool_size=10
)

# Create database handler instance
db_handler = DatabaseHandler(config)

# Initialize database (creates tables if they don't exist)
db_handler.initialize()
```

## Working with Projects

```python
from database_handler.models import Project

# Create a new project
project_data = {
    "name": "Research Project Alpha",
    "description": "A comprehensive research project on AI applications",
    "metadata": {"department": "AI Research", "priority": "high"}
}

project = db_handler.projects.create(project_data)
print(f"Created project with ID: {project.id}")

# Get project by ID
project = db_handler.projects.get_by_id(1)
print(f"Project: {project.name}")

# Update project
updated_data = {"description": "Updated description"}
project = db_handler.projects.update(1, updated_data)

# List all projects
projects = db_handler.projects.list()
for project in projects:
    print(f"- {project.name}")

# Delete project (cascades to all related data)
db_handler.projects.delete(1)
```

## Working with Text Sources

```python
# Create a text source for a project
source_data = {
    "project_id": 1,
    "title": "Primary Research Document",
    "content": "This is the main content of the research document...",
    "source_type": "document",
    "source_url": "https://example.com/research.pdf",
    "metadata": {"author": "Dr. Smith", "publication_date": "2024-01-15"}
}

text_source = db_handler.text_sources.create(source_data)

# Get all text sources for a project
sources = db_handler.text_sources.get_by_project_id(1)
for source in sources:
    print(f"- {source.title}")

# Search text sources by content
matching_sources = db_handler.text_sources.search_content("research")
```

## Working with Translations

```python
# Store a tokenized translation
translation_data = {
    "text_source_id": 1,
    "language_code": "es",
    "title": "Documento de Investigación Principal",
    "tokens": [
        {"token": "Este", "pos": 0},
        {"token": "es", "pos": 1},
        {"token": "el", "pos": 2},
        {"token": "contenido", "pos": 3},
        {"token": "principal", "pos": 4}
    ],
    "original_text": "Este es el contenido principal...",
    "metadata": {"translator": "AI System", "confidence": 0.95}
}

translation = db_handler.translations.create(translation_data)

# Get all translations for a text source
translations = db_handler.translations.get_by_source_id(1)
for trans in translations:
    print(f"- {trans.language_code}: {trans.title}")

# Get translation by language
spanish_translation = db_handler.translations.get_by_language(1, "es")

# Extract tokens from translation
tokens = spanish_translation.tokens
for token_data in tokens:
    print(f"Position {token_data['pos']}: {token_data['token']}")
```

## Working with Videos

```python
# Store video file reference
video_data = {
    "text_source_id": 1,
    "title": "Research Presentation Video",
    "file_path": "/media/videos/research_presentation.mp4",
    "file_url": "https://cdn.example.com/videos/research_presentation.mp4",
    "file_size": 157286400,  # bytes
    "duration": 1800,  # seconds (30 minutes)
    "format": "mp4",
    "thumbnail_path": "/media/thumbnails/research_presentation.jpg",
    "metadata": {"resolution": "1920x1080", "bitrate": "2000kbps"}
}

video = db_handler.videos.create(video_data)

# Get all videos for a text source
videos = db_handler.videos.get_by_source_id(1)
for video in videos:
    print(f"- {video.title} ({video.format}, {video.duration}s)")

# Get videos by format
mp4_videos = db_handler.videos.get_by_format("mp4")
```

## Working with Summaries

```python
# Create a summary for a text source
summary_data = {
    "text_source_id": 1,
    "title": "Executive Summary",
    "content": "This research demonstrates significant advances in AI...",
    "summary_type": "executive",
    "metadata": {"generated_by": "AI Assistant", "word_count": 250}
}

summary = db_handler.summaries.create(summary_data)

# Get summaries by type
executive_summaries = db_handler.summaries.get_by_type(1, "executive")
```

## Working with Links

```python
# Add reference links to a text source
link_data = {
    "text_source_id": 1,
    "url": "https://arxiv.org/abs/2024.12345",
    "title": "Related Research Paper",
    "description": "Supporting research that validates our findings",
    "link_type": "reference",
    "metadata": {"doi": "10.1000/xyz123", "citation_count": 45}
}

link = db_handler.links.create(link_data)

# Get all active links for a text source
links = db_handler.links.get_active_by_source_id(1)
for link in links:
    print(f"- {link.title}: {link.url}")

# Deactivate a link
db_handler.links.deactivate(link.id)
```

## Complex Queries and Relationships

```python
# Get complete project with all related data
project_with_data = db_handler.projects.get_complete(1)
print(f"Project: {project_with_data.name}")
print(f"Text Sources: {len(project_with_data.text_sources)}")

for source in project_with_data.text_sources:
    print(f"  Source: {source.title}")
    print(f"    Summaries: {len(source.summaries)}")
    print(f"    Translations: {len(source.translations)}")
    print(f"    Videos: {len(source.videos)}")
    print(f"    Links: {len(source.links)}")

# Search across all content
search_results = db_handler.search_all("artificial intelligence")
for result in search_results:
    print(f"Found in {result.type}: {result.title}")

# Get project statistics
stats = db_handler.projects.get_statistics(1)
print(f"Total sources: {stats['source_count']}")
print(f"Total translations: {stats['translation_count']}")
print(f"Languages available: {stats['languages']}")
```

## Transaction Management

```python
# Use transactions for complex operations
with db_handler.transaction() as tx:
    try:
        # Create project
        project = tx.projects.create(project_data)
        
        # Create multiple text sources
        for source_data in source_list:
            source_data["project_id"] = project.id
            source = tx.text_sources.create(source_data)
            
            # Add translations for each source
            for translation_data in translation_list:
                translation_data["text_source_id"] = source.id
                tx.translations.create(translation_data)
        
        # If everything succeeds, transaction commits automatically
        print("All data created successfully")
        
    except Exception as e:
        # Transaction rolls back automatically on exception
        print(f"Error occurred, rolling back: {e}")
        raise
```

## Error Handling

```python
from database_handler.exceptions import (
    DatabaseConnectionError,
    ValidationError,
    NotFoundError
)

try:
    # Attempt database operation
    project = db_handler.projects.get_by_id(999)
    
except NotFoundError:
    print("Project not found")
    
except ValidationError as e:
    print(f"Invalid data: {e.message}")
    
except DatabaseConnectionError:
    print("Database connection failed")
    # Implement retry logic or fallback
```

## Batch Operations

```python
# Bulk create text sources
source_list = [
    {"project_id": 1, "title": "Source 1", "content": "Content 1"},
    {"project_id": 1, "title": "Source 2", "content": "Content 2"},
    {"project_id": 1, "title": "Source 3", "content": "Content 3"}
]

created_sources = db_handler.text_sources.bulk_create(source_list)
print(f"Created {len(created_sources)} sources")

# Bulk update
update_data = {"metadata": {"batch_updated": True}}
updated_count = db_handler.text_sources.bulk_update_by_project(1, update_data)
print(f"Updated {updated_count} sources")
```

## Configuration and Environment Management

```python
import os
from database_handler.config import load_config_from_env

# Load configuration from environment variables
config = load_config_from_env()

# Or load from configuration file
config = load_config_from_file("config/production.yaml")

# Initialize with custom settings
db_handler = DatabaseHandler(
    config,
    enable_logging=True,
    log_level="DEBUG",
    enable_metrics=True
)
```

This database handler provides a comprehensive, production-ready solution for managing your project data with proper error handling, transaction support, and efficient querying capabilities.
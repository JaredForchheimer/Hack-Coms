"""
Example usage of the Database Handler for Project Management System.

This script demonstrates how to use the database handler to manage projects,
text sources, translations, summaries, videos, and links.
"""

import logging
import json
from database_handler import DatabaseHandler, DatabaseConfig
from database_handler.config import load_config_from_env
from database_handler.core.exceptions import NotFoundError, ValidationError


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_basic_usage():
    """Demonstrate basic usage of the database handler."""
    print("=== Basic Usage Example ===")
    
    # Load configuration from environment variables
    config = load_config_from_env()
    
    # Create database handler and initialize
    with DatabaseHandler(config) as db:
        db.initialize()
        
        # Create a new project
        project_data = {
            "name": "Example Project",
            "description": "A demonstration project for the database handler",
            "metadata": {
                "department": "Engineering",
                "priority": "high",
                "tags": ["demo", "example"]
            }
        }
        
        project = db.projects.create(project_data)
        print(f"Created project: {project.name} (ID: {project.id})")
        
        # Create a text source for the project
        text_source_data = {
            "project_id": project.id,
            "title": "Sample Research Document",
            "content": "This is a sample research document containing important information about our project. It includes methodology, findings, and conclusions.",
            "source_type": "document",
            "source_url": "https://example.com/research.pdf",
            "metadata": {
                "author": "Dr. Example",
                "word_count": 150
            }
        }
        
        text_source = db.text_sources.create(text_source_data)
        print(f"Created text source: {text_source.title} (ID: {text_source.id})")
        
        # Create a summary
        summary_data = {
            "text_source_id": text_source.id,
            "title": "Executive Summary",
            "content": "This document presents key findings from our research project, highlighting the main conclusions and recommendations.",
            "summary_type": "executive"
        }
        
        summary = db.summaries.create(summary_data)
        print(f"Created summary: {summary.title} (ID: {summary.id})")
        
        # Create a translation with tokenized data
        translation_data = {
            "text_source_id": text_source.id,
            "language_code": "es",
            "title": "Documento de Investigación de Muestra",
            "tokens": [
                {"token": "Este", "pos": 0},
                {"token": "es", "pos": 1},
                {"token": "un", "pos": 2},
                {"token": "documento", "pos": 3},
                {"token": "de", "pos": 4},
                {"token": "investigación", "pos": 5},
                {"token": "de", "pos": 6},
                {"token": "muestra", "pos": 7}
            ],
            "original_text": "Este es un documento de investigación de muestra",
            "metadata": {
                "translator": "AI System",
                "confidence": 0.95
            }
        }
        
        translation = db.translations.create(translation_data)
        print(f"Created translation: {translation.language_code} (ID: {translation.id})")
        
        # Create a video reference
        video_data = {
            "text_source_id": text_source.id,
            "title": "Project Presentation Video",
            "file_path": "/media/videos/project_presentation.mp4",
            "file_url": "https://cdn.example.com/videos/project_presentation.mp4",
            "file_size": 104857600,  # 100MB
            "duration": 1200,  # 20 minutes
            "format": "mp4",
            "metadata": {
                "resolution": "1920x1080",
                "presenter": "Dr. Example"
            }
        }
        
        video = db.videos.create(video_data)
        print(f"Created video: {video.title} (ID: {video.id})")
        
        # Create some links
        link_data = {
            "text_source_id": text_source.id,
            "url": "https://example.com/related-research",
            "title": "Related Research Paper",
            "description": "A related research paper that supports our findings",
            "link_type": "reference"
        }
        
        link = db.links.create(link_data)
        print(f"Created link: {link.title} (ID: {link.id})")


def example_advanced_queries():
    """Demonstrate advanced querying capabilities."""
    print("\n=== Advanced Queries Example ===")
    
    config = load_config_from_env()
    
    with DatabaseHandler(config) as db:
        db.initialize()
        
        # Search for projects
        projects = db.projects.search("Example")
        print(f"Found {len(projects)} projects matching 'Example'")
        
        if projects:
            project = projects[0]
            
            # Get project statistics
            stats = db.projects.get_statistics(project.id)
            print(f"Project statistics: {json.dumps(stats, indent=2)}")
            
            # Get all text sources for the project
            text_sources = db.text_sources.get_by_project_id(project.id)
            print(f"Found {len(text_sources)} text sources for project")
            
            if text_sources:
                text_source = text_sources[0]
                
                # Get all translations for the text source
                translations = db.translations.get_by_source_id(text_source.id)
                print(f"Found {len(translations)} translations")
                
                # Get translation by language
                spanish_translation = db.translations.get_by_language(text_source.id, "es")
                if spanish_translation:
                    print(f"Spanish translation: {spanish_translation.get_token_text()}")
                
                # Get all videos for the text source
                videos = db.videos.get_by_source_id(text_source.id)
                print(f"Found {len(videos)} videos")
                
                # Get video statistics
                video_stats = db.videos.get_statistics(text_source.id)
                print(f"Video statistics: {json.dumps(video_stats, indent=2)}")
                
                # Get active links
                links = db.links.get_active_by_source_id(text_source.id)
                print(f"Found {len(links)} active links")


def example_transaction_usage():
    """Demonstrate transaction usage for complex operations."""
    print("\n=== Transaction Usage Example ===")
    
    config = load_config_from_env()
    
    with DatabaseHandler(config) as db:
        db.initialize()
        
        # Use transaction for complex operation
        try:
            with db.transaction() as tx:
                # Create project within transaction
                project_data = {
                    "name": "Transaction Test Project",
                    "description": "Testing transaction functionality"
                }
                project = tx.projects.create(project_data)
                print(f"Created project in transaction: {project.id}")
                
                # Create multiple text sources
                for i in range(3):
                    source_data = {
                        "project_id": project.id,
                        "title": f"Source Document {i+1}",
                        "content": f"Content for document {i+1}",
                        "source_type": "document"
                    }
                    source = tx.text_sources.create(source_data)
                    print(f"Created text source in transaction: {source.id}")
                
                # If we reach here, transaction will commit automatically
                print("Transaction completed successfully")
                
        except Exception as e:
            print(f"Transaction failed and was rolled back: {e}")


def example_bulk_operations():
    """Demonstrate bulk operations for efficiency."""
    print("\n=== Bulk Operations Example ===")
    
    config = load_config_from_env()
    
    with DatabaseHandler(config) as db:
        db.initialize()
        
        # Find an existing project or create one
        projects = db.projects.search("Example")
        if not projects:
            project = db.projects.create({
                "name": "Bulk Operations Test",
                "description": "Testing bulk operations"
            })
        else:
            project = projects[0]
        
        # Bulk create text sources
        sources_data = []
        for i in range(5):
            sources_data.append({
                "project_id": project.id,
                "title": f"Bulk Source {i+1}",
                "content": f"Content for bulk source {i+1}",
                "source_type": "document"
            })
        
        sources = db.text_sources.bulk_create(sources_data)
        print(f"Bulk created {len(sources)} text sources")
        
        # Bulk create summaries
        summaries_data = []
        for source in sources[:3]:  # Create summaries for first 3 sources
            summaries_data.append({
                "text_source_id": source.id,
                "title": f"Summary for {source.title}",
                "content": f"This is a summary for {source.title}",
                "summary_type": "general"
            })
        
        summaries = db.summaries.bulk_create(summaries_data)
        print(f"Bulk created {len(summaries)} summaries")


def example_error_handling():
    """Demonstrate error handling."""
    print("\n=== Error Handling Example ===")
    
    config = load_config_from_env()
    
    with DatabaseHandler(config) as db:
        db.initialize()
        
        # Try to get a non-existent project
        try:
            project = db.projects.get_by_id(99999)
        except NotFoundError as e:
            print(f"Caught NotFoundError: {e}")
        
        # Try to create a project with invalid data
        try:
            invalid_project = db.projects.create({
                "name": "",  # Empty name should cause validation error
                "description": "This should fail"
            })
        except ValidationError as e:
            print(f"Caught ValidationError: {e}")
        
        # Try to create a text source with invalid project_id
        try:
            invalid_source = db.text_sources.create({
                "project_id": 99999,  # Non-existent project
                "title": "This should fail",
                "content": "Content"
            })
        except NotFoundError as e:
            print(f"Caught NotFoundError for invalid project_id: {e}")


def example_search_and_filtering():
    """Demonstrate search and filtering capabilities."""
    print("\n=== Search and Filtering Example ===")
    
    config = load_config_from_env()
    
    with DatabaseHandler(config) as db:
        db.initialize()
        
        # Search projects by name
        projects = db.projects.search("Example")
        print(f"Projects matching 'Example': {len(projects)}")
        
        # Search text sources by content
        text_sources = db.text_sources.search_content("research")
        print(f"Text sources containing 'research': {len(text_sources)}")
        
        # Search summaries by type
        if text_sources:
            summaries = db.summaries.get_by_type(text_sources[0].id, "executive")
            print(f"Executive summaries: {len(summaries)}")
        
        # Get available languages
        languages = db.translations.get_available_languages()
        print(f"Available languages: {languages}")
        
        # Get videos by format
        mp4_videos = db.videos.get_by_format("mp4")
        print(f"MP4 videos: {len(mp4_videos)}")
        
        # Get links by type
        if text_sources:
            reference_links = db.links.get_by_type(text_sources[0].id, "reference")
            print(f"Reference links: {len(reference_links)}")


def main():
    """Run all examples."""
    print("Database Handler Usage Examples")
    print("=" * 50)
    
    try:
        example_basic_usage()
        example_advanced_queries()
        example_transaction_usage()
        example_bulk_operations()
        example_error_handling()
        example_search_and_filtering()
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
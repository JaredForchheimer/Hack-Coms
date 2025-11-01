"""Sample data seeding script for testing and demonstration."""

import logging
import sys
import os
from typing import List, Dict, Any

# Add the parent directory to the path so we can import the database_handler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database_handler import DatabaseHandler, DatabaseConfig
from database_handler.config import load_config_from_env


logger = logging.getLogger(__name__)


def create_sample_projects() -> List[Dict[str, Any]]:
    """Create sample project data."""
    return [
        {
            "name": "AI Research Project",
            "description": "Comprehensive research on artificial intelligence applications in healthcare",
            "metadata": {
                "department": "AI Research",
                "priority": "high",
                "budget": 100000,
                "start_date": "2024-01-01"
            }
        },
        {
            "name": "Climate Change Analysis",
            "description": "Analysis of climate change impacts on coastal regions",
            "metadata": {
                "department": "Environmental Science",
                "priority": "medium",
                "budget": 75000,
                "start_date": "2024-02-15"
            }
        },
        {
            "name": "Educational Technology Study",
            "description": "Study on the effectiveness of digital learning platforms",
            "metadata": {
                "department": "Education",
                "priority": "medium",
                "budget": 50000,
                "start_date": "2024-03-01"
            }
        }
    ]


def create_sample_text_sources(project_ids: List[int]) -> List[Dict[str, Any]]:
    """Create sample text source data."""
    return [
        # AI Research Project sources
        {
            "project_id": project_ids[0],
            "title": "Machine Learning in Healthcare: A Comprehensive Review",
            "content": "This comprehensive review examines the current state of machine learning applications in healthcare. We analyze various algorithms including deep learning, neural networks, and ensemble methods. The study covers applications in medical imaging, drug discovery, and patient diagnosis. Key findings indicate that ML models can achieve accuracy rates of 95% or higher in specific diagnostic tasks. However, challenges remain in data privacy, model interpretability, and regulatory compliance.",
            "source_type": "research_paper",
            "source_url": "https://example.com/ml-healthcare-review.pdf",
            "metadata": {
                "authors": ["Dr. Smith", "Dr. Johnson"],
                "publication_date": "2024-01-15",
                "journal": "Journal of Medical AI",
                "doi": "10.1000/xyz123"
            }
        },
        {
            "project_id": project_ids[0],
            "title": "AI Ethics Guidelines for Healthcare Applications",
            "content": "This document outlines ethical guidelines for implementing AI systems in healthcare settings. Key principles include transparency, fairness, accountability, and patient privacy. The guidelines emphasize the importance of human oversight and the need for explainable AI models. Special attention is given to bias prevention and ensuring equitable access to AI-powered healthcare solutions.",
            "source_type": "guidelines",
            "source_url": "https://example.com/ai-ethics-healthcare.pdf",
            "metadata": {
                "organization": "Healthcare AI Ethics Board",
                "version": "2.1",
                "last_updated": "2024-01-20"
            }
        },
        # Climate Change Analysis sources
        {
            "project_id": project_ids[1],
            "title": "Sea Level Rise Projections for 2050",
            "content": "Based on current climate models and historical data, we project sea level rise of 15-30 cm by 2050 in coastal regions. This analysis incorporates data from satellite measurements, tide gauges, and ice sheet monitoring. The projections vary by geographic region, with some areas experiencing higher rates due to local factors such as land subsidence and ocean currents.",
            "source_type": "report",
            "source_url": "https://example.com/sea-level-projections.pdf",
            "metadata": {
                "data_sources": ["NOAA", "NASA", "IPCC"],
                "model_version": "CMIP6",
                "confidence_level": "high"
            }
        },
        # Educational Technology Study sources
        {
            "project_id": project_ids[2],
            "title": "Digital Learning Platform Effectiveness Survey",
            "content": "Survey results from 1,000 students across 50 schools show that digital learning platforms improve engagement by 40% and learning outcomes by 25%. Students reported higher satisfaction with interactive content and personalized learning paths. However, challenges include digital divide issues and the need for teacher training on new technologies.",
            "source_type": "survey",
            "metadata": {
                "sample_size": 1000,
                "schools": 50,
                "survey_period": "2024-02-01 to 2024-02-28",
                "response_rate": "78%"
            }
        }
    ]


def create_sample_summaries(text_source_ids: List[int]) -> List[Dict[str, Any]]:
    """Create sample summary data."""
    return [
        {
            "text_source_id": text_source_ids[0],
            "title": "Executive Summary: ML in Healthcare",
            "content": "Machine learning shows significant promise in healthcare with 95%+ accuracy in diagnostic tasks. Key applications include medical imaging, drug discovery, and patient diagnosis. Main challenges are data privacy, model interpretability, and regulatory compliance.",
            "summary_type": "executive",
            "metadata": {
                "word_count": 35,
                "generated_by": "AI Assistant",
                "confidence": 0.92
            }
        },
        {
            "text_source_id": text_source_ids[1],
            "title": "Key Points: AI Ethics Guidelines",
            "content": "Core principles: transparency, fairness, accountability, patient privacy. Emphasizes human oversight and explainable AI. Focus on bias prevention and equitable access to AI healthcare solutions.",
            "summary_type": "key_points",
            "metadata": {
                "word_count": 28,
                "generated_by": "Human Reviewer"
            }
        },
        {
            "text_source_id": text_source_ids[2],
            "title": "Technical Summary: Sea Level Projections",
            "content": "Projected 15-30 cm sea level rise by 2050 based on CMIP6 models. Regional variations due to local factors. High confidence level using NOAA, NASA, and IPCC data sources.",
            "summary_type": "technical",
            "metadata": {
                "word_count": 30,
                "technical_level": "advanced"
            }
        }
    ]


def create_sample_translations(text_source_ids: List[int]) -> List[Dict[str, Any]]:
    """Create sample translation data."""
    return [
        {
            "text_source_id": text_source_ids[0],
            "language_code": "es",
            "title": "Aprendizaje Automático en Atención Médica: Una Revisión Integral",
            "tokens": [
                {"token": "Esta", "pos": 0},
                {"token": "revisión", "pos": 1},
                {"token": "integral", "pos": 2},
                {"token": "examina", "pos": 3},
                {"token": "el", "pos": 4},
                {"token": "estado", "pos": 5},
                {"token": "actual", "pos": 6},
                {"token": "de", "pos": 7},
                {"token": "las", "pos": 8},
                {"token": "aplicaciones", "pos": 9},
                {"token": "de", "pos": 10},
                {"token": "aprendizaje", "pos": 11},
                {"token": "automático", "pos": 12},
                {"token": "en", "pos": 13},
                {"token": "atención", "pos": 14},
                {"token": "médica", "pos": 15}
            ],
            "original_text": "Esta revisión integral examina el estado actual de las aplicaciones de aprendizaje automático en atención médica.",
            "metadata": {
                "translator": "Professional Translator",
                "translation_date": "2024-01-16",
                "quality_score": 0.95
            }
        },
        {
            "text_source_id": text_source_ids[1],
            "language_code": "fr",
            "title": "Directives Éthiques de l'IA pour les Applications de Santé",
            "tokens": [
                {"token": "Ce", "pos": 0},
                {"token": "document", "pos": 1},
                {"token": "décrit", "pos": 2},
                {"token": "les", "pos": 3},
                {"token": "directives", "pos": 4},
                {"token": "éthiques", "pos": 5},
                {"token": "pour", "pos": 6},
                {"token": "l'implémentation", "pos": 7},
                {"token": "des", "pos": 8},
                {"token": "systèmes", "pos": 9},
                {"token": "d'IA", "pos": 10},
                {"token": "dans", "pos": 11},
                {"token": "les", "pos": 12},
                {"token": "environnements", "pos": 13},
                {"token": "de", "pos": 14},
                {"token": "santé", "pos": 15}
            ],
            "original_text": "Ce document décrit les directives éthiques pour l'implémentation des systèmes d'IA dans les environnements de santé.",
            "metadata": {
                "translator": "AI Translation Service",
                "translation_date": "2024-01-21",
                "quality_score": 0.88
            }
        }
    ]


def create_sample_videos(text_source_ids: List[int]) -> List[Dict[str, Any]]:
    """Create sample video data."""
    return [
        {
            "text_source_id": text_source_ids[0],
            "title": "ML in Healthcare: Expert Panel Discussion",
            "file_path": "/media/videos/ml_healthcare_panel.mp4",
            "file_url": "https://cdn.example.com/videos/ml_healthcare_panel.mp4",
            "file_size": 1073741824,  # 1GB
            "duration": 3600,  # 1 hour
            "format": "mp4",
            "thumbnail_path": "/media/thumbnails/ml_healthcare_panel.jpg",
            "metadata": {
                "resolution": "1920x1080",
                "bitrate": "2000kbps",
                "speakers": ["Dr. Smith", "Dr. Johnson", "Dr. Williams"],
                "recording_date": "2024-01-10"
            }
        },
        {
            "text_source_id": text_source_ids[2],
            "title": "Climate Data Visualization Demo",
            "file_path": "/media/videos/climate_data_viz.mp4",
            "file_url": "https://cdn.example.com/videos/climate_data_viz.mp4",
            "file_size": 536870912,  # 512MB
            "duration": 1800,  # 30 minutes
            "format": "mp4",
            "thumbnail_path": "/media/thumbnails/climate_data_viz.jpg",
            "metadata": {
                "resolution": "1280x720",
                "bitrate": "1500kbps",
                "presenter": "Dr. Climate",
                "recording_date": "2024-02-20"
            }
        }
    ]


def create_sample_links(text_source_ids: List[int]) -> List[Dict[str, Any]]:
    """Create sample link data."""
    return [
        {
            "text_source_id": text_source_ids[0],
            "url": "https://www.nature.com/articles/s41591-021-01614-0",
            "title": "AI for healthcare: The promise, the hype, the promise",
            "description": "Nature Medicine article discussing AI applications in healthcare",
            "link_type": "reference",
            "metadata": {
                "publication": "Nature Medicine",
                "access_date": "2024-01-15",
                "relevance_score": 0.95
            }
        },
        {
            "text_source_id": text_source_ids[0],
            "url": "https://github.com/healthcare-ai/ml-models",
            "title": "Healthcare ML Models Repository",
            "description": "Open source repository of machine learning models for healthcare applications",
            "link_type": "resource",
            "metadata": {
                "platform": "GitHub",
                "stars": 1250,
                "last_updated": "2024-01-12"
            }
        },
        {
            "text_source_id": text_source_ids[1],
            "url": "https://www.who.int/publications/i/item/ethics-and-governance-of-ai-for-health",
            "title": "WHO Ethics and Governance of AI for Health",
            "description": "World Health Organization guidelines on AI ethics in healthcare",
            "link_type": "guidelines",
            "metadata": {
                "organization": "WHO",
                "publication_date": "2021-06-28",
                "document_type": "official_guidelines"
            }
        },
        {
            "text_source_id": text_source_ids[2],
            "url": "https://climate.nasa.gov/evidence/",
            "title": "NASA Climate Change Evidence",
            "description": "NASA's comprehensive evidence for climate change",
            "link_type": "data_source",
            "metadata": {
                "organization": "NASA",
                "data_types": ["satellite", "temperature", "ice"],
                "last_updated": "2024-02-15"
            }
        }
    ]


def seed_database(config: DatabaseConfig = None, clear_existing: bool = False) -> bool:
    """
    Seed the database with sample data.
    
    Args:
        config: Database configuration. If None, loads from environment.
        clear_existing: Whether to clear existing data first.
    
    Returns:
        True if successful, False otherwise.
    """
    if config is None:
        config = load_config_from_env()
    
    try:
        with DatabaseHandler(config) as db:
            db.initialize()
            
            if clear_existing:
                logger.info("Clearing existing data...")
                # Clear in reverse order due to foreign key constraints
                db.execute_command("DELETE FROM links")
                db.execute_command("DELETE FROM videos")
                db.execute_command("DELETE FROM translations")
                db.execute_command("DELETE FROM summaries")
                db.execute_command("DELETE FROM text_sources")
                db.execute_command("DELETE FROM projects")
            
            logger.info("Creating sample projects...")
            projects_data = create_sample_projects()
            projects = db.projects.bulk_create(projects_data)
            project_ids = [p.id for p in projects]
            logger.info(f"Created {len(projects)} projects")
            
            logger.info("Creating sample text sources...")
            text_sources_data = create_sample_text_sources(project_ids)
            text_sources = db.text_sources.bulk_create(text_sources_data)
            text_source_ids = [ts.id for ts in text_sources]
            logger.info(f"Created {len(text_sources)} text sources")
            
            logger.info("Creating sample summaries...")
            summaries_data = create_sample_summaries(text_source_ids)
            summaries = db.summaries.bulk_create(summaries_data)
            logger.info(f"Created {len(summaries)} summaries")
            
            logger.info("Creating sample translations...")
            translations_data = create_sample_translations(text_source_ids)
            translations = db.translations.bulk_create(translations_data)
            logger.info(f"Created {len(translations)} translations")
            
            logger.info("Creating sample videos...")
            videos_data = create_sample_videos(text_source_ids)
            videos = db.videos.bulk_create(videos_data)
            logger.info(f"Created {len(videos)} videos")
            
            logger.info("Creating sample links...")
            links_data = create_sample_links(text_source_ids)
            links = db.links.bulk_create(links_data)
            logger.info(f"Created {len(links)} links")
            
            logger.info("Sample data seeding completed successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        return False


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Seed database with sample data')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        config = load_config_from_env()
        
        print("Seeding database with sample data...")
        success = seed_database(config, clear_existing=args.clear)
        
        if success:
            print("Database seeding completed successfully!")
            sys.exit(0)
        else:
            print("Database seeding failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
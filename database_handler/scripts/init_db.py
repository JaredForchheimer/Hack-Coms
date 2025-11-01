"""Database initialization script."""

import logging
import sys
import os
from typing import Optional

# Add the parent directory to the path so we can import the database_handler
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from database_handler.config import DatabaseConfig, load_config_from_env
from database_handler.core.exceptions import DatabaseError, DatabaseConnectionError


logger = logging.getLogger(__name__)


# SQL statements for creating tables
CREATE_TABLES_SQL = """
-- Create projects table
CREATE TABLE IF NOT EXISTS projects (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create text_sources table
CREATE TABLE IF NOT EXISTS text_sources (
    id SERIAL PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    source_type VARCHAR(50) DEFAULT 'text',
    source_url VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create summaries table
CREATE TABLE IF NOT EXISTS summaries (
    id SERIAL PRIMARY KEY,
    text_source_id INTEGER NOT NULL REFERENCES text_sources(id) ON DELETE CASCADE,
    title VARCHAR(255),
    content TEXT NOT NULL,
    summary_type VARCHAR(50) DEFAULT 'general',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create translations table
CREATE TABLE IF NOT EXISTS translations (
    id SERIAL PRIMARY KEY,
    text_source_id INTEGER NOT NULL REFERENCES text_sources(id) ON DELETE CASCADE,
    language_code VARCHAR(10) NOT NULL,
    title VARCHAR(255),
    tokens JSONB NOT NULL,
    original_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create videos table
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    text_source_id INTEGER NOT NULL REFERENCES text_sources(id) ON DELETE CASCADE,
    title VARCHAR(255),
    file_path VARCHAR(500) NOT NULL,
    file_url VARCHAR(500),
    file_size BIGINT,
    duration INTEGER,
    format VARCHAR(20),
    thumbnail_path VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);

-- Create links table
CREATE TABLE IF NOT EXISTS links (
    id SERIAL PRIMARY KEY,
    text_source_id INTEGER NOT NULL REFERENCES text_sources(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    title VARCHAR(255),
    description TEXT,
    link_type VARCHAR(50) DEFAULT 'reference',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'
);
"""

# SQL statements for creating indexes
CREATE_INDEXES_SQL = """
-- Project indexes
CREATE INDEX IF NOT EXISTS idx_projects_name ON projects(name);
CREATE INDEX IF NOT EXISTS idx_projects_created_at ON projects(created_at);

-- Text source indexes
CREATE INDEX IF NOT EXISTS idx_text_sources_project_id ON text_sources(project_id);
CREATE INDEX IF NOT EXISTS idx_text_sources_title ON text_sources(title);
CREATE INDEX IF NOT EXISTS idx_text_sources_source_type ON text_sources(source_type);

-- Summary indexes
CREATE INDEX IF NOT EXISTS idx_summaries_text_source_id ON summaries(text_source_id);
CREATE INDEX IF NOT EXISTS idx_summaries_summary_type ON summaries(summary_type);

-- Translation indexes
CREATE INDEX IF NOT EXISTS idx_translations_text_source_id ON translations(text_source_id);
CREATE INDEX IF NOT EXISTS idx_translations_language_code ON translations(language_code);

-- Video indexes
CREATE INDEX IF NOT EXISTS idx_videos_text_source_id ON videos(text_source_id);
CREATE INDEX IF NOT EXISTS idx_videos_format ON videos(format);

-- Link indexes
CREATE INDEX IF NOT EXISTS idx_links_text_source_id ON links(text_source_id);
CREATE INDEX IF NOT EXISTS idx_links_link_type ON links(link_type);
CREATE INDEX IF NOT EXISTS idx_links_is_active ON links(is_active);
"""

# SQL statements for creating triggers to update updated_at timestamps
CREATE_TRIGGERS_SQL = """
-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for each table
DROP TRIGGER IF EXISTS update_projects_updated_at ON projects;
CREATE TRIGGER update_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_text_sources_updated_at ON text_sources;
CREATE TRIGGER update_text_sources_updated_at
    BEFORE UPDATE ON text_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_summaries_updated_at ON summaries;
CREATE TRIGGER update_summaries_updated_at
    BEFORE UPDATE ON summaries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_translations_updated_at ON translations;
CREATE TRIGGER update_translations_updated_at
    BEFORE UPDATE ON translations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_videos_updated_at ON videos;
CREATE TRIGGER update_videos_updated_at
    BEFORE UPDATE ON videos
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_links_updated_at ON links;
CREATE TRIGGER update_links_updated_at
    BEFORE UPDATE ON links
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
"""


def initialize_database(config: Optional[DatabaseConfig] = None, drop_existing: bool = False) -> bool:
    """
    Initialize the database with tables, indexes, and triggers.
    
    Args:
        config: Database configuration. If None, loads from environment.
        drop_existing: Whether to drop existing tables first.
    
    Returns:
        True if successful, False otherwise.
    """
    if config is None:
        config = load_config_from_env()
    
    try:
        config.validate()
    except Exception as e:
        logger.error(f"Invalid database configuration: {e}")
        return False
    
    import psycopg2
    from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
    
    try:
        # Connect to PostgreSQL server (not specific database)
        server_params = config.get_connection_params()
        database_name = server_params.pop('database')
        
        logger.info("Connecting to PostgreSQL server...")
        conn = psycopg2.connect(**server_params)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database_name,))
            db_exists = cursor.fetchone() is not None
            
            if not db_exists:
                logger.info(f"Creating database: {database_name}")
                cursor.execute(f'CREATE DATABASE "{database_name}"')
            else:
                logger.info(f"Database {database_name} already exists")
        
        conn.close()
        
        # Connect to the specific database
        logger.info(f"Connecting to database: {database_name}")
        conn = psycopg2.connect(**config.get_connection_params())
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        
        with conn.cursor() as cursor:
            if drop_existing:
                logger.info("Dropping existing tables...")
                cursor.execute("""
                    DROP TABLE IF EXISTS links CASCADE;
                    DROP TABLE IF EXISTS videos CASCADE;
                    DROP TABLE IF EXISTS translations CASCADE;
                    DROP TABLE IF EXISTS summaries CASCADE;
                    DROP TABLE IF EXISTS text_sources CASCADE;
                    DROP TABLE IF EXISTS projects CASCADE;
                    DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
                """)
            
            logger.info("Creating tables...")
            cursor.execute(CREATE_TABLES_SQL)
            
            logger.info("Creating indexes...")
            cursor.execute(CREATE_INDEXES_SQL)
            
            logger.info("Creating triggers...")
            cursor.execute(CREATE_TRIGGERS_SQL)
        
        conn.close()
        logger.info("Database initialization completed successfully!")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"PostgreSQL error during initialization: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during initialization: {e}")
        return False


def check_database_status(config: Optional[DatabaseConfig] = None) -> dict:
    """
    Check the status of the database and tables.
    
    Args:
        config: Database configuration. If None, loads from environment.
    
    Returns:
        Dictionary with status information.
    """
    if config is None:
        config = load_config_from_env()
    
    import psycopg2
    
    status = {
        'database_exists': False,
        'tables_exist': {},
        'indexes_exist': {},
        'connection_successful': False,
        'error': None
    }
    
    try:
        conn = psycopg2.connect(**config.get_connection_params())
        status['connection_successful'] = True
        
        with conn.cursor() as cursor:
            status['database_exists'] = True
            
            # Check tables
            tables = ['projects', 'text_sources', 'summaries', 'translations', 'videos', 'links']
            for table in tables:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    )
                """, (table,))
                status['tables_exist'][table] = cursor.fetchone()[0]
            
            # Check indexes
            indexes = [
                'idx_projects_name', 'idx_text_sources_project_id', 
                'idx_summaries_text_source_id', 'idx_translations_text_source_id',
                'idx_videos_text_source_id', 'idx_links_text_source_id'
            ]
            for index in indexes:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM pg_indexes 
                        WHERE schemaname = 'public' 
                        AND indexname = %s
                    )
                """, (index,))
                status['indexes_exist'][index] = cursor.fetchone()[0]
        
        conn.close()
        
    except psycopg2.Error as e:
        status['error'] = str(e)
    except Exception as e:
        status['error'] = str(e)
    
    return status


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Initialize database for the project management system')
    parser.add_argument('--drop', action='store_true', help='Drop existing tables before creating new ones')
    parser.add_argument('--check', action='store_true', help='Check database status without making changes')
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
        
        if args.check:
            print("Checking database status...")
            status = check_database_status(config)
            
            print(f"Connection successful: {status['connection_successful']}")
            print(f"Database exists: {status['database_exists']}")
            
            if status['tables_exist']:
                print("\nTable status:")
                for table, exists in status['tables_exist'].items():
                    print(f"  {table}: {'✓' if exists else '✗'}")
            
            if status['indexes_exist']:
                print("\nIndex status:")
                for index, exists in status['indexes_exist'].items():
                    print(f"  {index}: {'✓' if exists else '✗'}")
            
            if status['error']:
                print(f"\nError: {status['error']}")
                sys.exit(1)
        else:
            print("Initializing database...")
            success = initialize_database(config, drop_existing=args.drop)
            
            if success:
                print("Database initialization completed successfully!")
                sys.exit(0)
            else:
                print("Database initialization failed!")
                sys.exit(1)
                
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
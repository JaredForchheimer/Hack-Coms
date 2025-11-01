"""Main media processing service that coordinates scraping, validation, and summarization."""

import logging
import os
from typing import Dict, Any, Optional
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from .scraping_service import ScrapingService
from .claude_service import ClaudeService
from ..utils.validators import validate_url, validate_file

logger = logging.getLogger(__name__)


class MediaService:
    """Service for processing media uploads and URLs."""

    def __init__(self, config=None):
        self.config = config
        self.scraper = ScrapingService()
        self.claude = ClaudeService()
        self.upload_folder = config.get('UPLOAD_FOLDER', 'uploads') if config else 'uploads'
        self.max_content_size = config.get('MAX_CONTENT_SIZE', 1000000) if config else 1000000

    def process_url(self, url: str) -> Dict[str, Any]:
        """Process a URL by extracting content and validating it."""
        try:
            logger.info(f"Processing URL: {url}")
            
            # Validate URL
            if not validate_url(url):
                return {
                    'success': False,
                    'error': 'Invalid URL format'
                }
            
            # Extract content
            extraction_result = self.scraper.extract_content(url)
            if not extraction_result['success']:
                return extraction_result
            
            # Get content for validation
            content = self._get_content_for_validation(extraction_result)
            if not content:
                return {
                    'success': False,
                    'error': 'No content found to validate'
                }
            
            # Check content size
            if len(content) > self.max_content_size:
                content = content[:self.max_content_size]
                logger.warning(f"Content truncated to {self.max_content_size} characters")
            
            # Validate content with Claude
            validation_result = self.claude.validate_content(
                content, 
                extraction_result.get('title')
            )
            
            if not validation_result['success']:
                return {
                    'success': False,
                    'error': validation_result.get('error', 'Validation failed')
                }
            
            # Combine results
            result = {
                'success': True,
                'extraction': extraction_result,
                'validation': validation_result,
                'content_preview': content[:500] + ('...' if len(content) > 500 else '')
            }
            
            logger.info(f"URL processing completed. Validation passed: {validation_result['accepted']}")
            return result
            
        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to process URL: {str(e)}'
            }

    def process_file(self, file: FileStorage) -> Dict[str, Any]:
        """Process an uploaded file."""
        try:
            logger.info(f"Processing uploaded file: {file.filename}")
            
            # Validate file
            validation_error = validate_file(file)
            if validation_error:
                return {
                    'success': False,
                    'error': validation_error
                }
            
            # Save file temporarily
            filename = secure_filename(file.filename)
            file_path = os.path.join(self.upload_folder, filename)
            file.save(file_path)
            
            try:
                # Extract content based on file type
                content = self._extract_file_content(file_path, filename)
                
                if not content:
                    return {
                        'success': False,
                        'error': 'Could not extract content from file'
                    }
                
                # Check content size
                if len(content) > self.max_content_size:
                    content = content[:self.max_content_size]
                    logger.warning(f"File content truncated to {self.max_content_size} characters")
                
                # Validate content with Claude
                validation_result = self.claude.validate_content(content, filename)
                
                if not validation_result['success']:
                    return {
                        'success': False,
                        'error': validation_result.get('error', 'Validation failed')
                    }
                
                # Prepare result
                extraction_result = {
                    'success': True,
                    'type': 'file',
                    'title': filename,
                    'content': content,
                    'size': file.content_length or len(content),
                    'uploadedAt': self._get_current_timestamp()
                }
                
                result = {
                    'success': True,
                    'extraction': extraction_result,
                    'validation': validation_result,
                    'content_preview': content[:500] + ('...' if len(content) > 500 else '')
                }
                
                logger.info(f"File processing completed. Validation passed: {validation_result['accepted']}")
                return result
                
            finally:
                # Clean up temporary file
                if os.path.exists(file_path):
                    os.remove(file_path)
            
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to process file: {str(e)}'
            }

    def generate_summary(self, content: str, title: str = None) -> Dict[str, Any]:
        """Generate a summary for approved content."""
        try:
            logger.info("Generating summary for approved content")
            
            if not content or len(content.strip()) == 0:
                return {
                    'success': False,
                    'error': 'Content is required for summary generation'
                }
            
            # Generate summary with Claude
            summary_result = self.claude.generate_summary(content, title)
            
            logger.info(f"Summary generation completed. Success: {summary_result['success']}")
            return summary_result
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to generate summary: {str(e)}'
            }

    def _get_content_for_validation(self, extraction_result: Dict[str, Any]) -> Optional[str]:
        """Extract content text from extraction result."""
        if extraction_result.get('type') == 'video':
            return extraction_result.get('transcript')
        elif extraction_result.get('type') == 'article':
            return extraction_result.get('content')
        elif extraction_result.get('type') == 'file':
            return extraction_result.get('content')
        return None

    def _extract_file_content(self, file_path: str, filename: str) -> Optional[str]:
        """Extract text content from uploaded file."""
        try:
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
            
            if file_ext == 'pdf':
                return self._extract_pdf_content(file_path)
            elif file_ext in ['txt', 'md']:
                return self._extract_text_content(file_path)
            else:
                logger.warning(f"Unsupported file type: {file_ext}")
                return None
                
        except Exception as e:
            logger.error(f"Error extracting content from {filename}: {str(e)}")
            return None

    def _extract_pdf_content(self, file_path: str) -> Optional[str]:
        """Extract text content from PDF file."""
        try:
            import PyPDF2
            
            content = []
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    content.append(page.extract_text())
            
            return ' '.join(content).strip()
            
        except ImportError:
            logger.error("PyPDF2 not installed, cannot process PDF files")
            return None
        except Exception as e:
            logger.error(f"Error extracting PDF content: {str(e)}")
            return None

    def _extract_text_content(self, file_path: str) -> Optional[str]:
        """Extract content from text files."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read().strip()
            except Exception as e:
                logger.error(f"Error reading text file: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"Error extracting text content: {str(e)}")
            return None

    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'

    def cleanup(self):
        """Clean up resources."""
        if hasattr(self.scraper, 'close'):
            self.scraper.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
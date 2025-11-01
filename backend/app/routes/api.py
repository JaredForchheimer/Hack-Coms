"""Main API routes for media processing and data retrieval."""

import logging
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from ..services.media_service import MediaService
from ..services.database_service import DatabaseService
from ..utils.exceptions import (
    BaseAppError, ValidationError, handle_app_error,
    ScrapingError, LLMServiceError, FileProcessingError
)
from ..utils.validators import validate_json_data, validate_url, validate_text_content

logger = logging.getLogger(__name__)
api_bp = Blueprint('api', __name__)


def get_media_service():
    """Get media service instance."""
    return MediaService(current_app.config)


def get_database_service():
    """Get database service instance."""
    return DatabaseService(current_app.config)


@api_bp.errorhandler(BaseAppError)
def handle_api_error(error):
    """Handle custom application errors."""
    return jsonify(*handle_app_error(error))


@api_bp.route('/media/extract-url', methods=['POST'])
def extract_url():
    """Extract text content from URL (news article or YouTube video)."""
    try:
        # Validate request data
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        
        data = request.get_json()
        valid, msg = validate_json_data(data, ['url'])
        if not valid:
            raise ValidationError(msg)
        
        url = data['url'].strip()
        if not validate_url(url):
            raise ValidationError("Invalid URL format")
        
        logger.info(f"Processing URL extraction request for: {url}")
        
        # Process URL with media service
        with get_media_service() as media_service:
            result = media_service.process_url(url)
        
        if not result['success']:
            logger.warning(f"URL processing failed: {result.get('error')}")
            return jsonify(result), 422
        
        # Transform result to match frontend expectations
        extraction = result['extraction']
        validation = result['validation']
        
        response = {
            'success': True,
            'type': extraction['type'],
            'title': extraction['title'],
            'url': url
        }
        
        # Add content based on type
        if extraction['type'] == 'video':
            response.update({
                'transcript': extraction.get('transcript', ''),
                'duration': extraction.get('duration'),
                'thumbnail': extraction.get('thumbnail')
            })
        else:
            response.update({
                'content': extraction.get('content', ''),
                'author': extraction.get('author'),
                'publishDate': extraction.get('publishDate')
            })
        
        # Add validation results
        response['validation'] = {
            'accepted': validation['accepted'],
            'checks': validation['checks'],
            'reason': validation['reason']
        }
        
        logger.info(f"URL extraction completed successfully. Accepted: {validation['accepted']}")
        return jsonify(response)
        
    except BaseAppError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in extract_url: {str(e)}")
        raise ScrapingError(f"Failed to process URL: {str(e)}")


@api_bp.route('/media/process-file', methods=['POST'])
def process_file():
    """Process uploaded file."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            raise ValidationError("No file provided")
        
        file = request.files['file']
        if file.filename == '':
            raise ValidationError("No file selected")
        
        logger.info(f"Processing file upload: {file.filename}")
        
        # Process file with media service
        with get_media_service() as media_service:
            result = media_service.process_file(file)
        
        if not result['success']:
            logger.warning(f"File processing failed: {result.get('error')}")
            return jsonify(result), 422
        
        # Transform result to match frontend expectations
        extraction = result['extraction']
        validation = result['validation']
        
        response = {
            'success': True,
            'type': 'file',
            'title': extraction['title'],
            'content': extraction['content'],
            'size': extraction['size'],
            'uploadedAt': extraction['uploadedAt'],
            'validation': {
                'accepted': validation['accepted'],
                'checks': validation['checks'],
                'reason': validation['reason']
            }
        }
        
        logger.info(f"File processing completed successfully. Accepted: {validation['accepted']}")
        return jsonify(response)
        
    except BaseAppError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in process_file: {str(e)}")
        raise FileProcessingError(f"Failed to process file: {str(e)}")


@api_bp.route('/media/validate', methods=['POST'])
def validate_content():
    """Validate content using Claude API."""
    try:
        # Validate request data
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        
        data = request.get_json()
        valid, msg = validate_json_data(data, ['content'])
        if not valid:
            raise ValidationError(msg)
        
        content = data['content']
        title = data.get('title')
        
        # Validate content
        content_valid, content_msg = validate_text_content(content)
        if not content_valid:
            raise ValidationError(content_msg)
        
        logger.info("Processing content validation request")
        
        # Validate with Claude
        with get_media_service() as media_service:
            validation_result = media_service.claude.validate_content(content, title)
        
        if not validation_result['success']:
            logger.warning(f"Content validation failed: {validation_result.get('error')}")
            raise LLMServiceError(validation_result.get('error', 'Validation failed'))
        
        response = {
            'success': True,
            'accepted': validation_result['accepted'],
            'checks': validation_result['checks'],
            'reason': validation_result['reason']
        }
        
        logger.info(f"Content validation completed. Accepted: {validation_result['accepted']}")
        return jsonify(response)
        
    except BaseAppError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in validate_content: {str(e)}")
        raise LLMServiceError(f"Content validation failed: {str(e)}")


@api_bp.route('/media/summarize', methods=['POST'])
def generate_summary():
    """Generate summary and store both content and summary in database."""
    try:
        # Validate request data
        if not request.is_json:
            raise ValidationError("Request must be JSON")
        
        data = request.get_json()
        required_fields = ['content', 'title', 'source_data']
        valid, msg = validate_json_data(data, required_fields)
        if not valid:
            raise ValidationError(msg)
        
        content = data['content']
        title = data['title']
        source_data = data['source_data']
        
        # Validate content
        content_valid, content_msg = validate_text_content(content)
        if not content_valid:
            raise ValidationError(content_msg)
        
        logger.info("Generating summary and storing data")
        
        # Generate summary
        with get_media_service() as media_service:
            summary_result = media_service.generate_summary(content, title)
        
        if not summary_result['success']:
            logger.warning(f"Summary generation failed: {summary_result.get('error')}")
            raise LLMServiceError(summary_result.get('error', 'Summary generation failed'))
        
        # Store text source and summary in database
        with get_database_service() as db_service:
            # Prepare source data for database
            source_db_data = {
                'title': title,
                'content': content,
                'source_type': source_data.get('type', 'unknown'),
                'source_url': source_data.get('url'),
                'metadata': source_data.get('metadata', {})
            }
            
            # Store text source
            stored_source = db_service.store_text_source(source_db_data)
            
            # Prepare summary data for database
            summary_db_data = {
                'text_source_id': stored_source['id'],
                'title': f"Summary: {title}",
                'content': summary_result['summary'],
                'summary_type': 'general',
                'metadata': {
                    'word_count': summary_result['wordCount'],
                    'generated_at': summary_result['generatedAt'],
                    'generated_by': 'claude-3-sonnet'
                }
            }
            
            # Store summary
            stored_summary = db_service.store_summary(summary_db_data)
        
        response = {
            'success': True,
            'summary': summary_result['summary'],
            'wordCount': summary_result['wordCount'],
            'generatedAt': summary_result['generatedAt'],
            'source_id': stored_source['id'],
            'summary_id': stored_summary['id']
        }
        
        logger.info(f"Summary generated and stored successfully. Source ID: {stored_source['id']}, Summary ID: {stored_summary['id']}")
        return jsonify(response)
        
    except BaseAppError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_summary: {str(e)}")
        raise LLMServiceError(f"Summary generation failed: {str(e)}")


@api_bp.route('/sources', methods=['GET'])
def get_sources():
    """Get all text sources from database."""
    try:
        # Get pagination parameters
        limit = min(int(request.args.get('limit', 100)), 1000)  # Max 1000
        offset = max(int(request.args.get('offset', 0)), 0)
        search = request.args.get('search', '').strip()
        
        logger.info(f"Retrieving sources (limit: {limit}, offset: {offset}, search: '{search}')")
        
        with get_database_service() as db_service:
            if search:
                sources = db_service.search_sources(search, limit=limit)
            else:
                sources = db_service.get_sources(limit=limit, offset=offset)
        
        response = {
            'success': True,
            'sources': sources,
            'count': len(sources),
            'limit': limit,
            'offset': offset
        }
        
        logger.info(f"Retrieved {len(sources)} sources from database")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving sources: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve sources: {str(e)}',
            'sources': []
        }), 500


@api_bp.route('/summaries', methods=['GET'])
def get_summaries():
    """Get all summaries from database."""
    try:
        # Get pagination parameters
        limit = min(int(request.args.get('limit', 100)), 1000)  # Max 1000
        offset = max(int(request.args.get('offset', 0)), 0)
        
        logger.info(f"Retrieving summaries (limit: {limit}, offset: {offset})")
        
        with get_database_service() as db_service:
            summaries = db_service.get_summaries(limit=limit, offset=offset)
        
        response = {
            'success': True,
            'summaries': summaries,
            'count': len(summaries),
            'limit': limit,
            'offset': offset
        }
        
        logger.info(f"Retrieved {len(summaries)} summaries from database")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving summaries: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve summaries: {str(e)}',
            'summaries': []
        }), 500


@api_bp.route('/sources/<int:source_id>', methods=['GET'])
def get_source_by_id(source_id):
    """Get a specific text source by ID."""
    try:
        logger.info(f"Retrieving source with ID: {source_id}")
        
        with get_database_service() as db_service:
            source = db_service.get_source_by_id(source_id)
        
        if not source:
            return jsonify({
                'success': False,
                'error': 'Source not found'
            }), 404
        
        response = {
            'success': True,
            'source': source
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving source {source_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve source: {str(e)}'
        }), 500


@api_bp.route('/summaries/<int:summary_id>', methods=['GET'])
def get_summary_by_id(summary_id):
    """Get a specific summary by ID."""
    try:
        logger.info(f"Retrieving summary with ID: {summary_id}")
        
        with get_database_service() as db_service:
            summary = db_service.get_summary_by_id(summary_id)
        
        if not summary:
            return jsonify({
                'success': False,
                'error': 'Summary not found'
            }), 404
        
        response = {
            'success': True,
            'summary': summary
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving summary {summary_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve summary: {str(e)}'
        }), 500


@api_bp.route('/statistics', methods=['GET'])
def get_statistics():
    """Get application statistics."""
    try:
        logger.info("Retrieving application statistics")
        
        with get_database_service() as db_service:
            stats = db_service.get_database_stats()
        
        response = {
            'success': True,
            'statistics': stats
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to retrieve statistics: {str(e)}',
            'statistics': {}
        }), 500
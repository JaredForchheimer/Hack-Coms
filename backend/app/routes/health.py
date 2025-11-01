"""Health check routes."""

import logging
from flask import Blueprint, jsonify, current_app

logger = logging.getLogger(__name__)
health_bp = Blueprint('health', __name__)


@health_bp.route('/', methods=['GET'])
@health_bp.route('/status', methods=['GET'])
def health_check():
    """Basic health check endpoint."""
    try:
        # Import here to avoid circular imports
        from ..services.database_service import DatabaseService
        
        # Check database connection
        db_service = DatabaseService(current_app.config)
        db_healthy = db_service.health_check()
        db_service.close()
        
        # Check Claude API (basic validation)
        claude_healthy = bool(current_app.config.get('ANTHROPIC_API_KEY'))
        
        status = {
            'status': 'healthy' if db_healthy and claude_healthy else 'unhealthy',
            'version': '1.0.0',
            'services': {
                'database': 'up' if db_healthy else 'down',
                'claude_api': 'configured' if claude_healthy else 'not_configured',
                'flask': 'up'
            },
            'environment': current_app.config.get('FLASK_ENV', 'unknown')
        }
        
        status_code = 200 if db_healthy and claude_healthy else 503
        return jsonify(status), status_code
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': 'Health check failed',
            'services': {
                'database': 'error',
                'claude_api': 'unknown',
                'flask': 'up'
            }
        }), 503


@health_bp.route('/database', methods=['GET'])
def database_health():
    """Database-specific health check."""
    try:
        from ..services.database_service import DatabaseService
        
        db_service = DatabaseService(current_app.config)
        stats = db_service.get_database_stats()
        db_service.close()
        
        return jsonify({
            'status': 'healthy' if stats.get('database_connected') else 'unhealthy',
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503


@health_bp.route('/claude', methods=['GET'])
def claude_health():
    """Claude API health check."""
    try:
        from ..services.claude_service import ClaudeService
        
        claude_service = ClaudeService()
        connection_test = claude_service.test_connection()
        
        return jsonify({
            'status': 'healthy' if connection_test else 'unhealthy',
            'api_configured': bool(current_app.config.get('ANTHROPIC_API_KEY')),
            'connection_test': connection_test
        })
        
    except Exception as e:
        logger.error(f"Claude health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'api_configured': bool(current_app.config.get('ANTHROPIC_API_KEY'))
        }), 503
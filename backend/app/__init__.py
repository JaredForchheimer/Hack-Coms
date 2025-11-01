"""Flask application factory."""

import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from .config import get_config


def create_app(config=None):
    """Create and configure Flask application."""
    
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'], supports_credentials=True)
    
    # Ensure upload folder exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from .routes.api import api_bp
    from .routes.health import health_bp
    
    app.register_blueprint(health_bp, url_prefix='/health')
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Global error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    @app.errorhandler(413)
    def too_large(error):
        return {'error': 'File too large'}, 413
    
    return app
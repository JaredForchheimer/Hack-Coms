"""Application entry point for the Flask backend."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app import create_app

# Create Flask application
app = create_app()

if __name__ == '__main__':
    try:
        host = app.config.get('HOST', '0.0.0.0')
        port = app.config.get('PORT', 5000)
        debug = app.config.get('DEBUG', False)
        
        print(f"Starting ASL Summarizer Backend Server...")
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"Debug: {debug}")
        print(f"Environment: {app.config.get('FLASK_ENV', 'unknown')}")
        print("=" * 50)
        
        app.run(host=host, port=port, debug=debug)
        
    except KeyboardInterrupt:
        print("\nShutting down server...")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)
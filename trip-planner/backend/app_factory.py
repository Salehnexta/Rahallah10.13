"""
Trip Planning Assistant - Flask Application Factory
Creates Flask application with proper configuration
"""
import os
import logging
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

def create_app(test_config=None):
    """
    Application factory following Flask best practices
    
    Args:
        test_config (dict, optional): Configuration for testing
        
    Returns:
        Flask: Configured Flask application
    """
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Configure app
    app.config.from_mapping(
        SECRET_KEY=os.getenv('SECRET_KEY', 'dev_key_CHANGE_ME_in_production'),
        DEEPSEEK_API_KEY=os.getenv('DEEPSEEK_API_KEY'),
        DEEPSEEK_API_BASE=os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com'),
    )
    
    # Apply test config if provided
    if test_config:
        app.config.update(test_config)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
    
    # Register blueprints
    from routes.api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

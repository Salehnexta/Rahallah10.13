"""
Simple test script to isolate startup issues.
Run this script to check what's causing the initialization error.
"""
import sys
import os
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test importing key modules to identify any issues."""
    try:
        logger.info("Testing Flask import...")
        import flask
        logger.info(f"Flask version: {flask.__version__}")
        
        logger.info("Testing Flask-SocketIO import...")
        import flask_socketio
        logger.info(f"Flask-SocketIO version: {flask_socketio.__version__}")
        
        logger.info("Testing Redis import...")
        import redis
        logger.info(f"Redis version: {redis.__version__}")
        
        logger.info("Testing our persistence module...")
        import utils.persistence
        logger.info("Persistence module imported successfully")

        # Try to create a SessionStore instance
        logger.info("Testing SessionStore initialization...")
        session_store = utils.persistence.SessionStore()
        logger.info("SessionStore initialized successfully")
        
        # Try to create a SessionStateManager instance
        if hasattr(utils.persistence, 'SessionStateManager'):
            logger.info("Testing SessionStateManager initialization...")
            session_manager = utils.persistence.SessionStateManager()
            logger.info("SessionStateManager initialized successfully")
        
        logger.info("All key imports successful!")
        return True
    
    except Exception as e:
        logger.error(f"Import error: {e}", exc_info=True)
        return False

def test_flask_minimal():
    """Test a minimal Flask app to check if Flask itself works."""
    try:
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/test')
        def test_route():
            return "Flask is working!"
        
        logger.info("Created minimal Flask app successfully")
        
        # Just create the app but don't run it
        return True
    
    except Exception as e:
        logger.error(f"Flask minimal app error: {e}", exc_info=True)
        return False

def test_socketio_minimal():
    """Test a minimal Flask+SocketIO app."""
    try:
        from flask import Flask
        from flask_socketio import SocketIO
        
        app = Flask(__name__)
        socketio = SocketIO(app)
        
        @socketio.on('connect')
        def test_connect():
            logger.info("Client connected to test socket")
        
        logger.info("Created minimal Flask+SocketIO app successfully")
        
        return True
    except Exception as e:
        logger.error(f"Flask+SocketIO minimal app error: {e}", exc_info=True)
        return False

def main():
    """Run all tests."""
    logger.info("=== Starting Import Tests ===")
    imports_ok = test_imports()
    
    logger.info("\n=== Starting Minimal Flask App Test ===")
    flask_ok = test_flask_minimal()
    
    logger.info("\n=== Starting Minimal SocketIO Test ===")
    socketio_ok = test_socketio_minimal()
    
    logger.info("\n=== Test Summary ===")
    logger.info(f"Imports: {'OK' if imports_ok else 'FAILED'}")
    logger.info(f"Minimal Flask: {'OK' if flask_ok else 'FAILED'}")
    logger.info(f"Minimal SocketIO: {'OK' if socketio_ok else 'FAILED'}")
    
    if imports_ok and flask_ok and socketio_ok:
        logger.info("\nAll tests passed! The issue might be in app.py itself, not in the imports or basic Flask/SocketIO functionality.")
    else:
        logger.info("\nSome tests failed. Check the logs above for details on what's causing the issue.")

if __name__ == "__main__":
    main()

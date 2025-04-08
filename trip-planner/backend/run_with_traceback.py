#!/usr/bin/env python3
"""
Run Flask app with full error traceback
"""
import sys
import traceback
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    logger.info("Importing app.py...")
    import app
    
    logger.info("Starting Flask app...")
    # Access the Flask app instance
    if hasattr(app, 'app'):
        flask_app = app.app
    else:
        logger.error("No Flask app instance found in app.py")
        sys.exit(1)
        
    # Access SocketIO if it exists
    socketio = getattr(app, 'socketio', None)
    
    if socketio:
        logger.info("Starting SocketIO app...")
        socketio.run(flask_app, debug=True, host='127.0.0.1', port=5000)
    else:
        logger.info("Starting regular Flask app...")
        flask_app.run(debug=True, host='127.0.0.1', port=5000)
        
except Exception as e:
    logger.error(f"Error running app: {e}")
    logger.error("Full traceback:")
    traceback.print_exc()

"""
Trip Planning Assistant - Flask Backend
Main application file that sets up routes and handles API requests
"""
import os
import uuid
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Import agent system
from agents.agent_orchestrator import AgentOrchestrator

# In-memory session storage for conversation history
# Format: {session_id: [{"role": "user/assistant", "content": "message"}]}
sessions = {}

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from the user
    
    Expected JSON payload:
    {
        "session_id": "optional-session-id",
        "message": "User's message",
        "language": "en/ar" (optional, will be auto-detected)
    }
    
    Returns:
    {
        "session_id": "session-id",
        "response": "Assistant's response",
        "language": "en/ar",
        "intent": "detected intent"
    }
    """
    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        # Create new session if it doesn't exist
        if session_id not in sessions:
            sessions[session_id] = []
            logger.info(f"Created new session: {session_id}")
        
        # Add user message to history
        sessions[session_id].append({"role": "user", "content": message})
        
        # Process message with agent orchestrator
        response_data = AgentOrchestrator().process_message(
            user_message=message,
            session_id=session_id,
            conversation_history=sessions[session_id]
        )
        
        # Extract response text and metadata
        response_text = response_data["text"]
        language = response_data["language"]
        intent = response_data["intent"]
        
        # Add assistant response to history
        sessions[session_id].append({"role": "assistant", "content": response_text})
        
        # Log the interaction (excluding sensitive data)
        logger.info(f"Session {session_id}: Processed message with intent {intent}, history length: {len(sessions[session_id])}")
        
        return jsonify({
            "session_id": session_id,
            "response": response_text,
            "language": language,
            "intent": intent
        })
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "An error occurred processing your request",
            "details": str(e)
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_session():
    """Reset a conversation session"""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        
        if session_id and session_id in sessions:
            sessions[session_id] = []
            logger.info(f"Reset session: {session_id}")
            return jsonify({"status": "success", "message": "Session reset successfully"})
        else:
            return jsonify({"status": "error", "message": "Invalid session ID"}), 400
            
    except Exception as e:
        logger.error(f"Error resetting session: {str(e)}")
        return jsonify({
            "error": "An error occurred resetting the session",
            "details": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    # Test LLM connection
    try:
        from agents.llm_utils import test_llm_connection
        llm_status, message = test_llm_connection()
        llm_health = "connected" if llm_status else "error"
    except Exception as e:
        llm_health = "error"
        message = str(e)
    
    return jsonify({
        "status": "healthy", 
        "version": "1.0.0",
        "llm_status": llm_health,
        "llm_message": message if llm_health == "error" else "LLM connection successful"
    })

@app.route('/api/languages', methods=['GET'])
def supported_languages():
    """Return supported languages"""
    return jsonify({
        "supported_languages": ["en", "ar"],
        "default_language": "en"
    })

if __name__ == '__main__':
    # Check if DeepSeek API key is set
    if not os.getenv('DEEPSEEK_API_KEY'):
        logger.warning("DEEPSEEK_API_KEY not found in environment variables")
        print("Warning: DEEPSEEK_API_KEY not set in .env file")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)

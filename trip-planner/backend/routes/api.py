"""
API Routes for Trip Planning Assistant
Defines all REST endpoints for the application
"""
import logging
import json
from flask import Blueprint, request, jsonify
from agents.agent_system import AgentSystem

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
api_bp = Blueprint('api', __name__)

# Initialize Agent System
agent_system = AgentSystem()

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        from agents.llm_utils import test_llm_connection
        
        # Test LLM connection
        llm_status = test_llm_connection()
        
        return jsonify({
            "success": True,
            "error": None,
            "data": {
                "status": "healthy",
                "version": "1.0.4",
                "llm_status": llm_status
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in health endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "data": {
                "status": "unhealthy",
                "version": "1.0.4",
                "llm_status": False
            }
        }), 500

@api_bp.route('/languages', methods=['GET'])
def languages():
    """Get supported languages"""
    try:
        return jsonify({
            "success": True,
            "error": None,
            "data": {
                "supported_languages": ["english", "arabic"],
                "default_language": "english"
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in languages endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "data": None
        }), 500

@api_bp.route('/chat', methods=['POST'])
def chat():
    """
    Chat endpoint for processing user messages
    
    Request body:
        {
            "message": "User message",
            "session_id": "unique_session_id",
            "language": "english|arabic" (optional, defaults to english)
        }
        
    Returns:
        JSON response with assistant message and any relevant data
    """
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing request body",
                "data": None
            }), 400
        
        # Extract required fields
        message = data.get('message')
        session_id = data.get('session_id')
        language = data.get('language', 'english')
        
        # Validate required fields
        if not message:
            return jsonify({
                "success": False,
                "error": "Missing 'message' field",
                "data": None
            }), 400
            
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Missing 'session_id' field",
                "data": None
            }), 400
        
        # Process message using Agent System
        response = agent_system.process_message(
            session_id=session_id,
            message=message,
            language=language
        )
        
        # Format response
        return jsonify({
            "success": True,
            "error": None,
            "data": {
                "text": response.get("text", ""),
                "intent": response.get("intent", "unknown"),
                "mock_data": response.get("mock_data", {}),
                "session_id": session_id,
                "intent": response.get("intent", "unknown"),
                "language": language,
                "response": response.get("text", "")
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "data": None
        }), 500

@api_bp.route('/test-connection', methods=['GET'])
def test_connection():
    """
    Test connection to the DeepSeek API
    
    Returns:
        JSON response with connection status
    """
    try:
        from agents.llm_utils import test_llm_connection
        
        # Test connection
        result = test_llm_connection()
        
        return jsonify({
            "success": result,
            "error": None if result else "Failed to connect to DeepSeek API",
            "data": {
                "connected": result
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in /test-connection endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "data": None
        }), 500

@api_bp.route('/reset', methods=['POST'])
def reset_session():
    """Reset a session"""
    try:
        # Parse request data
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Missing request body",
                "data": None
            }), 400
        
        # Extract required fields
        session_id = data.get('session_id')
        
        # Validate required fields
        if not session_id:
            return jsonify({
                "success": False,
                "error": "Missing 'session_id' field",
                "data": None
            }), 400
        
        # Check if session exists
        if session_id in agent_system.sessions:
            # Reset the session
            agent_system.sessions[session_id] = {
                "conversation_history": [],
                "flight_options": [],
                "hotel_options": [],
                "language": "english",
                "mock_data": {},
                "user_preferences": {}
            }
            
            return jsonify({
                "success": True,
                "error": None,
                "data": {
                    "status": "success",
                    "message": f"Session {session_id} has been reset"
                }
            }), 200
        else:
            # Session doesn't exist, create it
            agent_system.sessions[session_id] = {
                "conversation_history": [],
                "flight_options": [],
                "hotel_options": [],
                "language": "english",
                "mock_data": {},
                "user_preferences": {}
            }
            
            return jsonify({
                "success": True,
                "error": None,
                "data": {
                    "status": "success",
                    "message": f"New session {session_id} has been created"
                }
            }), 200
            
    except Exception as e:
        logger.error(f"Error in reset endpoint: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Internal server error",
            "data": None
        }), 500

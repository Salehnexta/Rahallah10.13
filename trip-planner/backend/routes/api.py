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

"""
Test script for the refactored Trip Planning Assistant
Tests the Flask application and LangGraph integration
"""
import logging
import json
import sys
from app_factory import create_app
from agents.agent_system import AgentSystem
from agents.llm_utils import test_llm_connection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_flask_app():
    """Test the Flask application factory"""
    logger.info("Testing Flask application factory...")
    
    # Create the Flask app with test configuration
    app = create_app({
        "TESTING": True,
        "DEBUG": True
    })
    
    # Test client
    with app.test_client() as client:
        # Test health endpoint
        logger.info("Testing health endpoint...")
        response = client.get('/health')
        assert response.status_code == 200
        assert "healthy" in response.get_json()["status"]
        logger.info("✅ Health endpoint test passed")
        
        # Test chat endpoint with valid data
        logger.info("Testing chat endpoint with valid data...")
        test_data = {
            "message": "I want to fly from Jeddah to Riyadh",
            "session_id": "test_session_123",
            "language": "english"
        }
        
        headers = {"Content-Type": "application/json"}
        response = client.post('/api/chat', data=json.dumps(test_data), headers=headers)
        
        # Verify response
        if response.status_code == 200:
            logger.info("✅ Chat endpoint test passed")
        else:
            logger.error(f"❌ Chat endpoint test failed: {response.get_json()}")
            
    logger.info("Flask application tests completed")

def test_agent_system():
    """Test the Agent System directly"""
    logger.info("Testing Agent System...")
    
    # Initialize Agent System
    agent_system = AgentSystem()
    
    # Test messages
    test_messages = [
        {
            "message": "I want to plan a trip from Jeddah to Riyadh next week",
            "session_id": "test_session_1",
            "language": "english",
            "expected_intent": "trip_planning"
        },
        {
            "message": "I need a flight from Riyadh to Jeddah",
            "session_id": "test_session_2", 
            "language": "english",
            "expected_intent": "flight_booking"
        }
    ]
    
    # Process each test message
    for i, test in enumerate(test_messages):
        logger.info(f"\n===== Testing message {i+1}: {test['message']} =====")
        
        try:
            # Process message
            response = agent_system.process_message(
                session_id=test["session_id"],
                message=test["message"],
                language=test["language"]
            )
            
            # Log response
            logger.info(f"Detected intent: {response.get('intent', 'unknown')}")
            logger.info(f"Response: {response.get('text', '')[:200]}...")  # Show first 200 chars
            
            # Verify intent
            if response.get("intent") == test["expected_intent"]:
                logger.info(f"✅ Test passed: Intent detected correctly")
            else:
                logger.error(f"❌ Test failed: Expected intent {test['expected_intent']}, got {response.get('intent', 'unknown')}")
                
        except Exception as e:
            logger.error(f"Error in test: {str(e)}")
            
    logger.info("Agent System tests completed")

def test_llm_connection_status():
    """Test LLM connection status"""
    logger.info("Testing LLM connection...")
    
    try:
        # Test connection
        result = test_llm_connection()
        
        if result:
            logger.info("✅ LLM connection test passed")
        else:
            logger.error("❌ LLM connection test failed")
            
    except Exception as e:
        logger.error(f"Error testing LLM connection: {str(e)}")
        
    logger.info("LLM connection test completed")

if __name__ == "__main__":
    logger.info("Starting Trip Planning Assistant tests...")
    
    # Test LLM connection
    test_llm_connection_status()
    
    # Test Agent System
    test_agent_system()
    
    # Test Flask app (uncomment when Flask routes are fully implemented)
    # test_flask_app()
    
    logger.info("All tests completed")

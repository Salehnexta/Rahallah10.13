"""
Agent Sequence Test for Trip Planning Assistant
Tests the agents working together in sequence without using LangGraph
"""
import logging
import json
import uuid
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import agents directly
from agents.conversation_lead_agent import ConversationLeadAgent
from agents.flight_booking_agent import FlightBookingAgent
from agents.hotel_booking_agent import HotelBookingAgent
from agents.trip_planning_agent import TripPlanningAgent

def process_conversation(message: str, language: str = "english"):
    """
    Process a conversation through the appropriate sequence of agents
    based on the detected intent
    
    Args:
        message (str): User message
        language (str): Language of the conversation ("english" or "arabic")
        
    Returns:
        dict: Final response with all relevant information
    """
    # Generate a unique session ID
    session_id = f"test_{uuid.uuid4().hex[:8]}"
    
    # Initialize all agents
    conversation_agent = ConversationLeadAgent()
    flight_agent = FlightBookingAgent()
    hotel_agent = HotelBookingAgent()
    trip_agent = TripPlanningAgent()
    
    # Step 1: Let conversation lead agent determine intent
    logger.info(f"Step 1: Processing with ConversationLeadAgent")
    convo_result = conversation_agent.process_request(session_id, message, language)
    
    intent = convo_result.get('intent', 'general')
    logger.info(f"Detected intent: {intent}")
    
    # Step 2: Based on intent, call the appropriate specialized agent
    if intent == 'flight_booking':
        logger.info(f"Step 2: Processing with FlightBookingAgent")
        result = flight_agent.process_request(session_id, message, language)
        
    elif intent == 'hotel_booking':
        logger.info(f"Step 2: Processing with HotelBookingAgent")
        result = hotel_agent.process_request(session_id, message, language)
        
    elif intent == 'trip_planning':
        logger.info(f"Step 2: Processing with TripPlanningAgent")
        result = trip_agent.process_request(session_id, message, language)
        
    else:
        # For general conversation, use the conversation lead agent's response
        logger.info(f"Step 2: No specialized agent needed, using ConversationLeadAgent response")
        result = convo_result
    
    # Include the detected intent in the result
    result['intent'] = intent
    
    return result

def test_agent_sequence():
    """Run tests for agent sequence processing"""
    
    # Test cases
    test_cases = [
        {
            "message": "I want to book a flight from Riyadh to Jeddah next week",
            "expected_intent": "flight_booking",
            "language": "english",
            "description": "Flight booking request in English"
        },
        {
            "message": "أريد حجز فندق في الرياض لمدة 3 أيام",
            "expected_intent": "hotel_booking",
            "language": "arabic",
            "description": "Hotel booking request in Arabic (I want to book a hotel in Riyadh for 3 days)"
        },
        {
            "message": "I need to plan a complete trip from Jeddah to Riyadh next month",
            "expected_intent": "trip_planning", 
            "language": "english",
            "description": "Trip planning request in English"
        }
    ]
    
    # Run the tests
    success_count = 0
    
    for i, test in enumerate(test_cases):
        logger.info(f"\n\n===== Test {i+1}: {test['description']} =====")
        logger.info(f"Message: '{test['message']}'")
        logger.info(f"Expected intent: {test['expected_intent']}")
        
        try:
            # Process the conversation
            result = process_conversation(test['message'], test['language'])
            
            # Log the response
            response_text = result.get('text', '')
            logger.info(f"Response: {response_text[:150]}..." if response_text else "No response generated")
            
            # Check the mock data
            if 'mock_data' in result:
                mock_data = result['mock_data']
                if 'flights' in mock_data:
                    logger.info(f"Generated {len(mock_data['flights'])} flight options")
                if 'hotels' in mock_data:
                    logger.info(f"Generated {len(mock_data['hotels'])} hotel options")
                if 'trip_packages' in mock_data:
                    logger.info(f"Generated {len(mock_data['trip_packages'])} trip packages")
            
            # Check if the detected intent matches the expected intent
            detected_intent = result.get('intent', 'unknown')
            if detected_intent == test['expected_intent']:
                logger.info("✅ Test passed: Intent detected correctly")
                success_count += 1
            else:
                logger.warning(f"❌ Test failed: Expected intent '{test['expected_intent']}' but got '{detected_intent}'")
                
        except Exception as e:
            logger.error(f"❌ Error processing conversation: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Print test summary
    logger.info(f"\n\n===== Test Summary =====")
    logger.info(f"Total tests: {len(test_cases)}")
    logger.info(f"Successful tests: {success_count}")
    logger.info(f"Success rate: {success_count/len(test_cases)*100:.1f}%")
    
    return success_count == len(test_cases)

if __name__ == "__main__":
    logger.info("Starting Agent Sequence Test for Trip Planning Assistant")
    success = test_agent_sequence()
    logger.info(f"\nOverall test {'succeeded' if success else 'failed'}")

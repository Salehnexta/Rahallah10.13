"""
Test Script for Trip Planning Assistant
This script tests each agent individually with mock data
"""
import logging
import json
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import all necessary modules and classes for both LangGraph and direct agent testing
try:
    # Test if LangGraph is available
    import langgraph
    LANGGRAPH_AVAILABLE = True
    logger.info("LangGraph is available, will test with LangGraph workflow.")
except ImportError as e:
    logger.warning(f"LangGraph not available: {e}. Will test agents directly without LangGraph.")
    LANGGRAPH_AVAILABLE = False

# Import node functions for LangGraph testing
from agents.conversation_lead_agent import create_conversation_lead_node
from agents.flight_booking_agent import create_flight_booking_node
from agents.hotel_booking_agent import create_hotel_booking_node
from agents.trip_planning_agent import create_trip_planning_node
from agents.llm_utils import create_agent_workflow

# Import agent classes for direct testing
from agents.conversation_lead_agent import ConversationLeadAgent
from agents.flight_booking_agent import FlightBookingAgent
from agents.hotel_booking_agent import HotelBookingAgent
from agents.trip_planning_agent import TripPlanningAgent

def test_langgraph_workflow():
    """Test the LangGraph-based multi-agent workflow"""
    
    # Create agent nodes
    logger.info("Creating agent nodes...")
    conversation_lead_node = create_conversation_lead_node()
    flight_booking_node = create_flight_booking_node()
    hotel_booking_node = create_hotel_booking_node()
    trip_planning_node = create_trip_planning_node()
    
    # Create the agent workflow
    logger.info("Creating agent workflow...")
    agents = {
        "conversation_lead_agent": conversation_lead_node,
        "flight_booking_agent": flight_booking_node,
        "hotel_booking_agent": hotel_booking_node,
        "trip_planning_agent": trip_planning_node
    }
    
    workflow = create_agent_workflow(agents)
    
    # Test messages
    test_messages = [
        {
            "message": "I want to plan a trip from Jeddah to Riyadh next week",
            "expected_intent": "trip_planning",
            "language": "english"
        },
        {
            "message": "I need a flight from Riyadh to Jeddah",
            "expected_intent": "flight_booking",
            "language": "english"
        },
        {
            "message": "أريد حجز فندق في الرياض",  # "I want to book a hotel in Riyadh"
            "expected_intent": "hotel_booking",
            "language": "arabic"
        }
    ]
    
    # Run the tests
    for i, test in enumerate(test_messages):
        logger.info(f"\n===== Testing message {i+1}: {test['message']} =====")
        
        # Initialize the state
        state = {
            "session_id": f"test_session_{i}",
            "message": test["message"],
            "language": test["language"]
        }
        
        # Run the workflow
        try:
            result = workflow.invoke(state)
            
            # Print the results
            logger.info(f"Final agent: {result.get('current_agent', 'unknown')}")
            logger.info(f"Detected intent: {result.get('intent', 'unknown')}")
            logger.info(f"Response: {result.get('response', '')[:200]}...")  # Show first 200 chars
            
            # Check if mock data was generated
            mock_data = result.get('mock_data', {})
            if mock_data:
                if 'flights' in mock_data:
                    logger.info(f"Generated {len(mock_data['flights'])} flight options")
                if 'hotels' in mock_data:
                    logger.info(f"Generated {len(mock_data['hotels'])} hotel options")
                if 'trip_packages' in mock_data:
                    logger.info(f"Generated {len(mock_data['trip_packages'])} trip packages")
            
            # Validate expected intent
            if result.get('intent') == test['expected_intent']:
                logger.info("✅ Test passed: Intent detected correctly")
            else:
                logger.warning(f"❌ Test failed: Expected intent '{test['expected_intent']}' but got '{result.get('intent')}'")
                
        except Exception as e:
            logger.error(f"Error running workflow: {str(e)}")
            import traceback
            traceback.print_exc()
    
    logger.info("\nAll tests completed")

def test_direct_agents():
    """Test each agent directly without using LangGraph"""
    logger.info("Testing agents directly without LangGraph workflow")
    
    # Initialize agents
    conversation_agent = ConversationLeadAgent()
    flight_agent = FlightBookingAgent()
    hotel_agent = HotelBookingAgent()
    trip_agent = TripPlanningAgent()
    
    # Test messages
    test_messages = [
        {
            "message": "I want to plan a trip from Jeddah to Riyadh next week",
            "expected_intent": "trip_planning",
            "language": "english"
        },
        {
            "message": "I need a flight from Riyadh to Jeddah",
            "expected_intent": "flight_booking",
            "language": "english"
        },
        {
            "message": "أريد حجز فندق في الرياض",  # "I want to book a hotel in Riyadh"
            "expected_intent": "hotel_booking",
            "language": "arabic"
        }
    ]
    
    # Test each agent with each message
    for i, test in enumerate(test_messages):
        logger.info(f"\n===== Testing message {i+1}: {test['message']} =====")
        session_id = f"test_session_{i}"
        message = test["message"]
        language = test["language"]
        
        # Test conversation lead agent
        try:
            logger.info("\nTesting ConversationLeadAgent...")
            convo_result = conversation_agent.process_request(session_id, message, language)
            logger.info(f"Detected intent: {convo_result.get('intent', 'unknown')}")
            logger.info(f"Response: {convo_result.get('text', '')[:200]}...")  # First 200 chars
            
            # Based on intent, test the appropriate specialized agent
            intent = convo_result.get('intent', 'general')
            
            if intent == 'flight_booking':
                logger.info("\nTesting FlightBookingAgent...")
                flight_result = flight_agent.process_request(session_id, message, language)
                logger.info(f"Generated {len(flight_result.get('mock_data', {}).get('flights', []))} flight options")
                logger.info(f"Response: {flight_result.get('text', '')[:200]}...")  # First 200 chars
                
            elif intent == 'hotel_booking':
                logger.info("\nTesting HotelBookingAgent...")
                hotel_result = hotel_agent.process_request(session_id, message, language)
                logger.info(f"Generated {len(hotel_result.get('mock_data', {}).get('hotels', []))} hotel options")
                logger.info(f"Response: {hotel_result.get('text', '')[:200]}...")  # First 200 chars
                
            elif intent == 'trip_planning':
                logger.info("\nTesting TripPlanningAgent...")
                trip_result = trip_agent.process_request(session_id, message, language)
                logger.info(f"Generated {len(trip_result.get('mock_data', {}).get('trip_packages', []))} trip packages")
                logger.info(f"Response: {trip_result.get('text', '')[:200]}...")  # First 200 chars
            
            # Validate expected intent
            if intent == test['expected_intent']:
                logger.info("✅ Test passed: Intent detected correctly")
            else:
                logger.warning(f"❌ Test failed: Expected intent '{test['expected_intent']}' but got '{intent}'")
                
        except Exception as e:
            logger.error(f"Error testing agents: {str(e)}")
            import traceback
            traceback.print_exc()
    
    logger.info("\nAll direct agent tests completed")


if __name__ == "__main__":
    logger.info("Starting Trip Planning Assistant Tests")
    
    if LANGGRAPH_AVAILABLE:
        test_langgraph_workflow()
    else:
        test_direct_agents()

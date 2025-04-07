"""
Basic test for Trip Planning Assistant agents
Tests each agent individually without LangGraph
"""
import logging
import json
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_conversation_lead_agent():
    """Test the ConversationLeadAgent basic functionality"""
    try:
        from agents.conversation_lead_agent import ConversationLeadAgent
        
        logger.info("\n===== Testing ConversationLeadAgent =====")
        agent = ConversationLeadAgent()
        
        # Create a test message
        test_message = "I need a flight from Riyadh to Jeddah next week"
        test_session = "test_session_123"
        language = "english"
        
        # Process the message
        logger.info(f"Processing: '{test_message}'")
        result = agent.process_request(test_session, test_message, language)
        
        # Log the result
        intent = result.get("intent", "unknown")
        logger.info(f"Detected intent: {intent}")
        logger.info(f"Response: {result.get('text', '')[:100]}...")
        
        return True
    except Exception as e:
        logger.error(f"Error testing ConversationLeadAgent: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_flight_booking_agent():
    """Test the FlightBookingAgent basic functionality"""
    try:
        from agents.flight_booking_agent import FlightBookingAgent
        
        logger.info("\n===== Testing FlightBookingAgent =====")
        agent = FlightBookingAgent()
        
        # Create a test message
        test_message = "I need a flight from Riyadh to Jeddah next week"
        test_session = "test_session_123"
        language = "english"
        
        # Process the message
        logger.info(f"Processing: '{test_message}'")
        result = agent.process_request(test_session, test_message, language)
        
        # Log the result
        logger.info(f"Response: {result.get('text', '')[:100]}...")
        
        # Check mock data
        mock_data = result.get("mock_data", {})
        flights = mock_data.get("flights", [])
        logger.info(f"Generated {len(flights)} flight options")
        
        if flights:
            logger.info(f"First flight: {flights[0].get('airline')} {flights[0].get('flight_number')}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing FlightBookingAgent: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_hotel_booking_agent():
    """Test the HotelBookingAgent basic functionality"""
    try:
        from agents.hotel_booking_agent import HotelBookingAgent
        
        logger.info("\n===== Testing HotelBookingAgent =====")
        agent = HotelBookingAgent()
        
        # Create a test message
        test_message = "I need a hotel in Riyadh for next week"
        test_session = "test_session_123"
        language = "english"
        
        # Process the message
        logger.info(f"Processing: '{test_message}'")
        result = agent.process_request(test_session, test_message, language)
        
        # Log the result
        logger.info(f"Response: {result.get('text', '')[:100]}...")
        
        # Check mock data
        mock_data = result.get("mock_data", {})
        hotels = mock_data.get("hotels", [])
        logger.info(f"Generated {len(hotels)} hotel options")
        
        if hotels:
            logger.info(f"First hotel: {hotels[0].get('name')}, {hotels[0].get('star_rating')} stars")
        
        return True
    except Exception as e:
        logger.error(f"Error testing HotelBookingAgent: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_trip_planning_agent():
    """Test the TripPlanningAgent basic functionality"""
    try:
        from agents.trip_planning_agent import TripPlanningAgent
        
        logger.info("\n===== Testing TripPlanningAgent =====")
        agent = TripPlanningAgent()
        
        # Create a test message
        test_message = "I need to plan a trip from Riyadh to Jeddah next week"
        test_session = "test_session_123"
        language = "english"
        
        # Process the message
        logger.info(f"Processing: '{test_message}'")
        result = agent.process_request(test_session, test_message, language)
        
        # Log the result
        logger.info(f"Response: {result.get('text', '')[:100]}...")
        
        # Check mock data
        mock_data = result.get("mock_data", {})
        packages = mock_data.get("trip_packages", [])
        logger.info(f"Generated {len(packages)} trip packages")
        
        if packages:
            logger.info(f"First package: {packages[0].get('name')}, Price: {packages[0].get('total_price')}")
        
        return True
    except Exception as e:
        logger.error(f"Error testing TripPlanningAgent: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    logger.info("Starting Basic Agent Tests")
    
    # Run each test individually
    convo_success = test_conversation_lead_agent()
    flight_success = test_flight_booking_agent()
    hotel_success = test_hotel_booking_agent()
    trip_success = test_trip_planning_agent()
    
    # Log overall results
    logger.info("\n===== Test Results =====")
    logger.info(f"ConversationLeadAgent: {'✅ PASSED' if convo_success else '❌ FAILED'}")
    logger.info(f"FlightBookingAgent: {'✅ PASSED' if flight_success else '❌ FAILED'}")
    logger.info(f"HotelBookingAgent: {'✅ PASSED' if hotel_success else '❌ FAILED'}")
    logger.info(f"TripPlanningAgent: {'✅ PASSED' if trip_success else '❌ FAILED'}")
    
    overall = all([convo_success, flight_success, hotel_success, trip_success])
    logger.info(f"\nOverall: {'✅ ALL TESTS PASSED' if overall else '❌ SOME TESTS FAILED'}")

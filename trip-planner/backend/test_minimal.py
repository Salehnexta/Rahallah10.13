"""
Minimal test script for Trip Planning Assistant
Tests basic functionality of each agent
"""
import logging
import sys
import os

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Run a simple test of basic agent functionality"""
    logger.info("Starting minimal test of Trip Planning Assistant agents")
    
    # Import the agents individually to avoid potential import issues
    try:
        from agents.conversation_lead_agent import ConversationLeadAgent
        from agents.flight_booking_agent import FlightBookingAgent
        from agents.hotel_booking_agent import HotelBookingAgent
        from agents.trip_planning_agent import TripPlanningAgent
        
        logger.info("✅ Imported all agent classes successfully")
    except Exception as e:
        logger.error(f"❌ Error importing agent classes: {str(e)}")
        return
    
    # Test conversation lead agent with a simple request
    try:
        logger.info("\nTesting ConversationLeadAgent...")
        agent = ConversationLeadAgent()
        
        test_message = "I want to book a flight from Riyadh to Jeddah"
        
        logger.info(f"Input message: '{test_message}'")
        result = agent.process_request("test_session", test_message, "english")
        
        logger.info(f"Detected intent: {result.get('intent', 'unknown')}")
        if 'text' in result:
            logger.info(f"Response: {result['text'][:100]}...")
        
        logger.info("✅ ConversationLeadAgent test successful")
    except Exception as e:
        logger.error(f"❌ ConversationLeadAgent test failed: {str(e)}")
    
    # Test flight booking agent
    try:
        logger.info("\nTesting FlightBookingAgent...")
        agent = FlightBookingAgent()
        
        test_message = "I need a flight from Riyadh to Jeddah tomorrow"
        
        logger.info(f"Input message: '{test_message}'")
        result = agent.process_request("test_session", test_message, "english")
        
        if 'text' in result:
            logger.info(f"Response: {result['text'][:100]}...")
        
        # Check mock data
        flights = result.get('mock_data', {}).get('flights', [])
        logger.info(f"Generated {len(flights)} flight options")
        
        logger.info("✅ FlightBookingAgent test successful")
    except Exception as e:
        logger.error(f"❌ FlightBookingAgent test failed: {str(e)}")
    
    # Test hotel booking agent
    try:
        logger.info("\nTesting HotelBookingAgent...")
        agent = HotelBookingAgent()
        
        test_message = "I need a hotel in Riyadh for next week"
        
        logger.info(f"Input message: '{test_message}'")
        result = agent.process_request("test_session", test_message, "english")
        
        if 'text' in result:
            logger.info(f"Response: {result['text'][:100]}...")
        
        # Check mock data
        hotels = result.get('mock_data', {}).get('hotels', [])
        logger.info(f"Generated {len(hotels)} hotel options")
        
        logger.info("✅ HotelBookingAgent test successful")
    except Exception as e:
        logger.error(f"❌ HotelBookingAgent test failed: {str(e)}")
    
    # Test trip planning agent
    try:
        logger.info("\nTesting TripPlanningAgent...")
        agent = TripPlanningAgent()
        
        test_message = "I want to plan a trip from Riyadh to Jeddah next week"
        
        logger.info(f"Input message: '{test_message}'")
        result = agent.process_request("test_session", test_message, "english")
        
        if 'text' in result:
            logger.info(f"Response: {result['text'][:100]}...")
        
        # Check mock data
        packages = result.get('mock_data', {}).get('trip_packages', [])
        logger.info(f"Generated {len(packages)} trip package options")
        
        logger.info("✅ TripPlanningAgent test successful")
    except Exception as e:
        logger.error(f"❌ TripPlanningAgent test failed: {str(e)}")
    
    logger.info("\nMinimal test completed")

if __name__ == "__main__":
    main()

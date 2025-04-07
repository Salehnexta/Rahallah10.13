"""
Simple test script to test each agent individually
"""
import logging
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_conversation_agent():
    """Test the ConversationLeadAgent in isolation"""
    from agents.conversation_lead_agent import ConversationLeadAgent
    
    print("\n===== TESTING CONVERSATION LEAD AGENT =====")
    conversation_agent = ConversationLeadAgent()
    
    # Test English message
    message = "I want to plan a trip from Jeddah to Riyadh"
    response = conversation_agent.process_request("test_session", message, "english")
    
    print(f"User: {message}")
    print(f"Agent response: {response['text']}")
    print(f"Detected intent: {response['intent']}")
    
    # Test Arabic message
    arabic_message = "أريد حجز فندق في الرياض"
    arabic_response = conversation_agent.process_request("test_session", arabic_message, "arabic")
    
    print(f"\nUser: {arabic_message}")
    print(f"Agent response: {arabic_response['text']}")
    print(f"Detected intent: {arabic_response['intent']}")

def test_flight_agent():
    """Test the FlightBookingAgent in isolation"""
    from agents.flight_booking_agent import FlightBookingAgent
    
    print("\n===== TESTING FLIGHT BOOKING AGENT =====")
    flight_agent = FlightBookingAgent()
    
    # Test English message
    message = "I need a flight from Jeddah to Riyadh next week"
    response = flight_agent.process_request("test_session", message, "english")
    
    print(f"User: {message}")
    print(f"Agent response: {response['text'][:200]}...") # Show first 200 chars
    print(f"Mock data contains {len(response.get('mock_data', {}).get('flights', []))} flights")
    
    # Test first flight data
    if response.get('mock_data', {}).get('flights'):
        first_flight = response['mock_data']['flights'][0]
        print(f"Sample flight: {first_flight['airline']} {first_flight['flight_number']} from {first_flight['origin']} to {first_flight['destination']}")

def test_hotel_agent():
    """Test the HotelBookingAgent in isolation"""
    from agents.hotel_booking_agent import HotelBookingAgent
    
    print("\n===== TESTING HOTEL BOOKING AGENT =====")
    hotel_agent = HotelBookingAgent()
    
    # Test English message
    message = "I need a hotel in Riyadh for 3 nights"
    response = hotel_agent.process_request("test_session", message, "english")
    
    print(f"User: {message}")
    print(f"Agent response: {response['text'][:200]}...") # Show first 200 chars
    print(f"Mock data contains {len(response.get('mock_data', {}).get('hotels', []))} hotels")
    
    # Test first hotel data
    if response.get('mock_data', {}).get('hotels'):
        first_hotel = response['mock_data']['hotels'][0]
        print(f"Sample hotel: {first_hotel['name']} ({first_hotel['star_rating']} stars) in {first_hotel['city']}")

def test_trip_agent():
    """Test the TripPlanningAgent in isolation"""
    from agents.trip_planning_agent import TripPlanningAgent
    
    print("\n===== TESTING TRIP PLANNING AGENT =====")
    trip_agent = TripPlanningAgent()
    
    # Test English message
    message = "I want to plan a trip from Jeddah to Riyadh next week"
    response = trip_agent.process_request("test_session", message, "english")
    
    print(f"User: {message}")
    print(f"Agent response: {response['text'][:200]}...") # Show first 200 chars
    print(f"Mock data contains {len(response.get('mock_data', {}).get('trip_packages', []))} trip packages")
    
    # Test first package data
    if response.get('mock_data', {}).get('trip_packages'):
        first_package = response['mock_data']['trip_packages'][0]
        print(f"Sample package: {first_package['name']} - Total: {first_package['total_price']} {first_package['currency']}")

if __name__ == "__main__":
    print("Starting Individual Agent Tests")
    print("Using mock data instead of API calls\n")
    
    # Test each agent individually with separate try-except blocks
    print("Testing agents one by one with detailed error reporting:\n")
    
    try:
        print("1. Testing ConversationLeadAgent...")
        test_conversation_agent()
        print("ConversationLeadAgent test completed successfully!")
    except Exception as e:
        logger.exception(f"ConversationLeadAgent test failed: {str(e)}")
        print(f"ConversationLeadAgent test failed: {str(e)}")
    
    try:
        print("\n2. Testing FlightBookingAgent...")
        test_flight_agent()
        print("FlightBookingAgent test completed successfully!")
    except Exception as e:
        logger.exception(f"FlightBookingAgent test failed: {str(e)}")
        print(f"FlightBookingAgent test failed: {str(e)}")
    
    try:
        print("\n3. Testing HotelBookingAgent...")
        test_hotel_agent()
        print("HotelBookingAgent test completed successfully!")
    except Exception as e:
        logger.exception(f"HotelBookingAgent test failed: {str(e)}")
        print(f"HotelBookingAgent test failed: {str(e)}")
    
    try:
        print("\n4. Testing TripPlanningAgent...")
        test_trip_agent()
        print("TripPlanningAgent test completed successfully!")
    except Exception as e:
        logger.exception(f"TripPlanningAgent test failed: {str(e)}")
        print(f"TripPlanningAgent test failed: {str(e)}")
    
    print("\nAll individual agent tests attempted.")

"""
Integration test for testing the Trip Planning Assistant agent system
with mock data instead of API calls
"""
import os
import logging
import json
from agents.conversation_lead_agent import ConversationLeadAgent
from agents.flight_booking_agent import FlightBookingAgent
from agents.hotel_booking_agent import HotelBookingAgent
from agents.trip_planning_agent import TripPlanningAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_conversation_flow():
    """Test the conversation flow through different agent interactions"""
    # Initialize agents
    conversation_agent = ConversationLeadAgent()
    flight_agent = FlightBookingAgent()
    hotel_agent = HotelBookingAgent()
    trip_agent = TripPlanningAgent()
    
    # Test session ID
    session_id = "test_session_123"
    
    print("\n===== TESTING CONVERSATION FLOW =====")
    
    # Test initial greeting
    print("\n1. Initial greeting:")
    greeting_message = "Hello, I need help planning a trip"
    greeting_response = conversation_agent.process_request(session_id, greeting_message, "english")
    print(f"User: {greeting_message}")
    print(f"System: {greeting_response['text']}")
    
    # Test flight booking intent
    print("\n2. Flight booking intent:")
    flight_message = "I need to book a flight from Jeddah to Riyadh next week"
    flight_intent_response = conversation_agent.process_request(session_id, flight_message, "english")
    print(f"User: {flight_message}")
    print(f"System: {flight_intent_response['text']}")
    print(f"Detected intent: {flight_intent_response['intent']}")
    
    # Process with flight agent directly
    if flight_intent_response['intent'] == "flight_booking":
        flight_response = flight_agent.process_request(session_id, flight_message, "english")
        print("\nFlight Agent Response:")
        print(flight_response['text'])
        print(f"Generated {len(flight_response.get('mock_data', {}).get('flights', []))} flight options")
    
    # Test hotel booking intent
    print("\n3. Hotel booking intent:")
    hotel_message = "I need a hotel in Riyadh for 3 nights"
    hotel_intent_response = conversation_agent.process_request(session_id, hotel_message, "english")
    print(f"User: {hotel_message}")
    print(f"System: {hotel_intent_response['text']}")
    print(f"Detected intent: {hotel_intent_response['intent']}")
    
    # Process with hotel agent directly
    if hotel_intent_response['intent'] == "hotel_booking":
        hotel_response = hotel_agent.process_request(session_id, hotel_message, "english")
        print("\nHotel Agent Response:")
        print(hotel_response['text'])
        print(f"Generated {len(hotel_response.get('mock_data', {}).get('hotels', []))} hotel options")
    
    # Test trip planning intent
    print("\n4. Trip planning intent:")
    trip_message = "I want to plan a complete trip from Jeddah to Riyadh for next week"
    trip_intent_response = conversation_agent.process_request(session_id, trip_message, "english")
    print(f"User: {trip_message}")
    print(f"System: {trip_intent_response['text']}")
    print(f"Detected intent: {trip_intent_response['intent']}")
    
    # Process with trip planning agent directly
    if trip_intent_response['intent'] == "trip_planning":
        trip_response = trip_agent.process_request(session_id, trip_message, "english")
        print("\nTrip Planning Agent Response:")
        print(trip_response['text'])
        print(f"Generated {len(trip_response.get('mock_data', {}).get('trip_packages', []))} trip packages")
    
    # Test language switching (Arabic)
    print("\n5. Arabic language test:")
    arabic_message = "أريد حجز رحلة من جدة إلى الرياض"
    arabic_response = conversation_agent.process_request(session_id, arabic_message, "arabic")
    print(f"User: {arabic_message}")
    print(f"System: {arabic_response['text']}")
    print(f"Detected intent: {arabic_response['intent']}")
    
    if arabic_response['intent'] == "trip_planning":
        arabic_trip_response = trip_agent.process_request(session_id, arabic_message, "arabic")
        print("\nArabic Trip Planning Agent Response:")
        print(arabic_trip_response['text'])

def test_direct_agents():
    """Test each agent directly with mock data"""
    # Test session ID
    session_id = "test_session_456"
    
    print("\n===== TESTING DIRECT AGENT CALLS =====")
    
    # Test FlightBookingAgent directly
    print("\n1. Flight Booking Agent Test:")
    flight_agent = FlightBookingAgent()
    flight_response = flight_agent.process_request(
        session_id, 
        "I need a flight from Riyadh to Jeddah", 
        "english"
    )
    print(flight_response['text'])
    mock_flights = flight_response.get('mock_data', {}).get('flights', [])
    print(f"Generated {len(mock_flights)} flight options")
    if mock_flights:
        print(f"Sample flight: {json.dumps(mock_flights[0], indent=2)}")
    
    # Test HotelBookingAgent directly
    print("\n2. Hotel Booking Agent Test:")
    hotel_agent = HotelBookingAgent()
    hotel_response = hotel_agent.process_request(
        session_id, 
        "I need a hotel in Riyadh", 
        "english"
    )
    print(hotel_response['text'])
    mock_hotels = hotel_response.get('mock_data', {}).get('hotels', [])
    print(f"Generated {len(mock_hotels)} hotel options")
    if mock_hotels:
        print(f"Sample hotel: {json.dumps(mock_hotels[0], indent=2)}")
    
    # Test TripPlanningAgent directly
    print("\n3. Trip Planning Agent Test:")
    trip_agent = TripPlanningAgent()
    trip_response = trip_agent.process_request(
        session_id, 
        "I want to plan a trip from Jeddah to Riyadh", 
        "english"
    )
    print(trip_response['text'])
    mock_packages = trip_response.get('mock_data', {}).get('trip_packages', [])
    print(f"Generated {len(mock_packages)} trip packages")
    if mock_packages:
        print(f"Sample package summary: {json.dumps({'package_id': mock_packages[0]['package_id'], 'name': mock_packages[0]['name'], 'total_price': mock_packages[0]['total_price']}, indent=2)}")

if __name__ == "__main__":
    print("Starting Trip Planning Assistant Integration Tests")
    print("Using mock data instead of API calls\n")
    
    try:
        # Test direct agent calls
        test_direct_agents()
        
        # Test conversation flow
        test_conversation_flow()
        
        print("\nAll tests completed successfully!")
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        print(f"\nTest failed: {str(e)}")

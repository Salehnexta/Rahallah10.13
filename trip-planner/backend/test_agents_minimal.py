"""
Minimal test for Trip Planning Assistant agents
Tests each agent individually with mock implementations
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

# Mock implementations of agents for testing - without LangGraph dependencies
class MockConversationLeadAgent:
    """Simplified Conversation Lead Agent for testing"""
    
    def process_request(self, session_id, message, language):
        """Determine intent from message using simple keywords"""
        logger.info(f"Processing message with ConversationLeadAgent: '{message}'")
        
        # Simple keyword matching for intents
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["flight", "fly", "plane", "airport", "رحلة", "طيران", "مطار"]):
            intent = "flight_booking"
        elif any(word in message_lower for word in ["hotel", "stay", "room", "فندق", "غرفة", "إقامة"]):
            intent = "hotel_booking"
        elif any(word in message_lower for word in ["trip", "plan", "travel", "package", "رحلة", "سفر", "حزمة"]):
            intent = "trip_planning"
        else:
            intent = "general"
        
        # Generate a simple response based on intent
        if language == "english":
            if intent == "flight_booking":
                response = f"I'll help you book a flight. Please provide more details about your travel plans."
            elif intent == "hotel_booking":
                response = f"I'll help you find a hotel. Please provide more details about your stay."
            elif intent == "trip_planning":
                response = f"I'll help you plan your trip. Please provide more details about your travel plans."
            else:
                response = f"How can I assist you with your travel plans today?"
        else:  # arabic
            if intent == "flight_booking":
                response = "سأساعدك في حجز رحلة طيران. يرجى تقديم المزيد من التفاصيل حول خطط سفرك."
            elif intent == "hotel_booking":
                response = "سأساعدك في العثور على فندق. يرجى تقديم المزيد من التفاصيل حول إقامتك."
            elif intent == "trip_planning":
                response = "سأساعدك في تخطيط رحلتك. يرجى تقديم المزيد من التفاصيل حول خطط سفرك."
            else:
                response = "كيف يمكنني مساعدتك في خطط سفرك اليوم؟"
        
        return {
            "text": response,
            "intent": intent,
            "mock_data": {},
            "success": True
        }

class MockFlightBookingAgent:
    """Simplified Flight Booking Agent for testing"""
    
    def process_request(self, session_id, message, language):
        """Generate mock flight options"""
        logger.info(f"Processing message with FlightBookingAgent: '{message}'")
        
        # Extract simple origin and destination
        message_lower = message.lower()
        origin = "Riyadh"  # Default
        destination = "Jeddah"  # Default
        
        # Generate mock flight data
        flights = [
            {
                "airline": "Saudia",
                "flight_number": "SV1020",
                "departure_airport": "RUH",
                "arrival_airport": "JED",
                "departure_time": "08:00",
                "arrival_time": "09:45",
                "duration": "1h 45m",
                "price": "850 SAR",
                "class": "Economy"
            },
            {
                "airline": "flynas",
                "flight_number": "XY2314",
                "departure_airport": "RUH",
                "arrival_airport": "JED",
                "departure_time": "14:30",
                "arrival_time": "16:15",
                "duration": "1h 45m",
                "price": "720 SAR",
                "class": "Economy"
            }
        ]
        
        # Generate response
        if language == "english":
            response = f"I found {len(flights)} flights from {origin} to {destination}:\n\n"
            for i, flight in enumerate(flights, 1):
                response += f"{i}. {flight['airline']} {flight['flight_number']}: {flight['departure_time']} - {flight['arrival_time']}, {flight['duration']}, {flight['price']}\n"
        else:  # arabic
            response = f"وجدت {len(flights)} رحلات من {origin} إلى {destination}:\n\n"
            for i, flight in enumerate(flights, 1):
                response += f"{i}. {flight['airline']} {flight['flight_number']}: {flight['departure_time']} - {flight['arrival_time']}, {flight['duration']}, {flight['price']}\n"
        
        return {
            "text": response,
            "intent": "flight_booking",
            "mock_data": {"flights": flights},
            "success": True
        }

class MockHotelBookingAgent:
    """Simplified Hotel Booking Agent for testing"""
    
    def process_request(self, session_id, message, language):
        """Generate mock hotel options"""
        logger.info(f"Processing message with HotelBookingAgent: '{message}'")
        
        # Extract simple destination
        message_lower = message.lower()
        destination = "Riyadh"  # Default
        
        # Generate mock hotel data
        hotels = [
            {
                "name": "Luxury Riyadh Hotel",
                "star_rating": 5,
                "location": "Downtown Riyadh",
                "price_per_night": "950 SAR",
                "amenities": ["Pool", "Spa", "Restaurant", "Gym"],
                "breakfast_included": True,
                "wifi": True
            },
            {
                "name": "Business Traveler Hotel",
                "star_rating": 4,
                "location": "Business District, Riyadh",
                "price_per_night": "750 SAR",
                "amenities": ["Restaurant", "Business Center", "Gym"],
                "breakfast_included": True,
                "wifi": True
            }
        ]
        
        # Generate response
        if language == "english":
            response = f"I found {len(hotels)} hotels in {destination}:\n\n"
            for i, hotel in enumerate(hotels, 1):
                response += f"{i}. {hotel['name']}: {hotel['star_rating']} stars, {hotel['location']}, {hotel['price_per_night']} per night\n"
        else:  # arabic
            response = f"وجدت {len(hotels)} فنادق في {destination}:\n\n"
            for i, hotel in enumerate(hotels, 1):
                response += f"{i}. {hotel['name']}: {hotel['star_rating']} نجوم, {hotel['location']}, {hotel['price_per_night']} في الليلة\n"
        
        return {
            "text": response,
            "intent": "hotel_booking",
            "mock_data": {"hotels": hotels},
            "success": True
        }

class MockTripPlanningAgent:
    """Simplified Trip Planning Agent for testing"""
    
    def process_request(self, session_id, message, language):
        """Generate mock trip packages"""
        logger.info(f"Processing message with TripPlanningAgent: '{message}'")
        
        # Extract simple origin and destination
        message_lower = message.lower()
        origin = "Riyadh"  # Default
        destination = "Jeddah"  # Default
        
        # Generate mock trip packages
        trip_packages = [
            {
                "name": "Weekend Getaway",
                "origin": origin,
                "destination": destination,
                "duration": "3 days",
                "flight": {
                    "airline": "Saudia",
                    "flight_number": "SV1020",
                    "price": "850 SAR"
                },
                "hotel": {
                    "name": "Luxury Hotel",
                    "star_rating": 5,
                    "price_per_night": "950 SAR"
                },
                "total_price": "3700 SAR",
                "activities": ["Beach visit", "Shopping", "Dining experience"]
            },
            {
                "name": "Business Trip Package",
                "origin": origin,
                "destination": destination,
                "duration": "2 days",
                "flight": {
                    "airline": "flynas",
                    "flight_number": "XY2314",
                    "price": "720 SAR"
                },
                "hotel": {
                    "name": "Business Traveler Hotel",
                    "star_rating": 4,
                    "price_per_night": "750 SAR"
                },
                "total_price": "2220 SAR",
                "activities": ["Business center", "Conference facilities"]
            }
        ]
        
        # Generate response
        if language == "english":
            response = f"I've prepared {len(trip_packages)} trip packages from {origin} to {destination}:\n\n"
            for i, package in enumerate(trip_packages, 1):
                response += f"{i}. {package['name']}: {package['duration']}, Flight: {package['flight']['airline']}, Hotel: {package['hotel']['name']}, Total: {package['total_price']}\n"
        else:  # arabic
            response = f"لقد أعددت {len(trip_packages)} حزم سفر من {origin} إلى {destination}:\n\n"
            for i, package in enumerate(trip_packages, 1):
                response += f"{i}. {package['name']}: {package['duration']}, الرحلة: {package['flight']['airline']}, الفندق: {package['hotel']['name']}, المجموع: {package['total_price']}\n"
        
        return {
            "text": response,
            "intent": "trip_planning",
            "mock_data": {"trip_packages": trip_packages},
            "success": True
        }

def test_sequential_flow():
    """Test the agents working together in sequence"""
    # Create the agents
    convo_agent = MockConversationLeadAgent()
    flight_agent = MockFlightBookingAgent()
    hotel_agent = MockHotelBookingAgent()
    trip_agent = MockTripPlanningAgent()
    
    # Test cases
    test_cases = [
        {
            "message": "I want to book a flight from Riyadh to Jeddah",
            "expected_intent": "flight_booking",
            "language": "english"
        },
        {
            "message": "أريد حجز فندق في الرياض",  # I want to book a hotel in Riyadh
            "expected_intent": "hotel_booking",
            "language": "arabic"
        },
        {
            "message": "I need a travel package from Jeddah to Riyadh",
            "expected_intent": "trip_planning",
            "language": "english"
        }
    ]
    
    # Run the tests
    for i, test in enumerate(test_cases):
        logger.info(f"\n===== Test {i+1}: {test['message']} =====")
        
        # Step 1: Use conversation lead agent to determine intent
        logger.info("Step 1: Processing with Conversation Lead Agent")
        result = convo_agent.process_request("test_session", test["message"], test["language"])
        
        intent = result.get("intent", "unknown")
        logger.info(f"Detected intent: {intent}")
        logger.info(f"Response: {result.get('text', '')}")
        
        # Step 2: Based on intent, use the appropriate specialized agent
        logger.info(f"Step 2: Processing with specialized agent based on intent: {intent}")
        
        if intent == "flight_booking":
            specialized_result = flight_agent.process_request("test_session", test["message"], test["language"])
        elif intent == "hotel_booking":
            specialized_result = hotel_agent.process_request("test_session", test["message"], test["language"])
        elif intent == "trip_planning":
            specialized_result = trip_agent.process_request("test_session", test["message"], test["language"]) 
        else:
            specialized_result = {"text": "I'm not sure how to help with that specific request."}
        
        logger.info(f"Specialized agent response: {specialized_result.get('text', '')[:100]}...")
        
        # Check mock data
        mock_data = specialized_result.get("mock_data", {})
        if "flights" in mock_data:
            logger.info(f"Generated {len(mock_data['flights'])} flight options")
        if "hotels" in mock_data:
            logger.info(f"Generated {len(mock_data['hotels'])} hotel options")
        if "trip_packages" in mock_data:
            logger.info(f"Generated {len(mock_data['trip_packages'])} trip packages")
        
        # Verify intent matching
        if intent == test["expected_intent"]:
            logger.info("✅ Detected correct intent")
        else:
            logger.warning(f"❌ Expected {test['expected_intent']} but got {intent}")

if __name__ == "__main__":
    logger.info("Starting minimal agent test with mock implementations")
    test_sequential_flow()
    logger.info("\nTest completed successfully")

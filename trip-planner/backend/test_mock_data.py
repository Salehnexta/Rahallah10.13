"""
Test script for Trip Planning Assistant mock data generation
"""
import os
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockFlightBookingAgent:
    """Simplified Flight Booking Agent that generates mock flight data"""
    
    def process_request(self, session_id, message, language):
        """Process a flight booking request with mock data"""
        logger.info(f"Processing flight booking request: {message}")
        
        # Extract origin and destination from message (simplified)
        origin = "Jeddah" if "Jeddah" in message else "Riyadh"
        destination = "Riyadh" if "Riyadh" in message and origin != "Riyadh" else "Jeddah"
        
        # Generate mock flight options
        flights = self._generate_mock_flights(origin, destination)
        
        # Generate response
        response_text = self._format_response(flights, language)
        
        return {
            "text": response_text,
            "intent": "flight_booking",
            "mock_data": {"flights": flights},
            "success": True
        }
    
    def _generate_mock_flights(self, origin, destination, num_options=3):
        """Generate mock flight options"""
        airlines = ["Saudia", "flynas", "flyadeal"]
        flight_numbers = ["SV1020", "XY215", "F3321"]
        
        today = datetime.now()
        
        flights = []
        for i in range(num_options):
            departure_date = (today + timedelta(days=i+1)).strftime("%Y-%m-%d")
            departure_time = f"{8 + i}:00"
            arrival_time = f"{10 + i}:30"
            
            flights.append({
                "airline": airlines[i % len(airlines)],
                "flight_number": flight_numbers[i % len(flight_numbers)],
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "departure_time": departure_time,
                "arrival_time": arrival_time,
                "price": 450 + (i * 75),
                "currency": "SAR",
                "booking_link": f"https://example.com/book/{flight_numbers[i % len(flight_numbers)]}"
            })
        
        return flights
    
    def _format_response(self, flights, language):
        """Format the response message based on language"""
        if language.lower() == "arabic":
            return f"وجدت {len(flights)} رحلات من {flights[0]['origin']} إلى {flights[0]['destination']}."
        else:
            return f"I found {len(flights)} flights from {flights[0]['origin']} to {flights[0]['destination']}."

class MockHotelBookingAgent:
    """Simplified Hotel Booking Agent that generates mock hotel data"""
    
    def process_request(self, session_id, message, language):
        """Process a hotel booking request with mock data"""
        logger.info(f"Processing hotel booking request: {message}")
        
        # Extract city from message (simplified)
        city = "Riyadh" if "Riyadh" in message else "Jeddah"
        
        # Generate mock hotel options
        hotels = self._generate_mock_hotels(city)
        
        # Generate response
        response_text = self._format_response(hotels, language)
        
        return {
            "text": response_text,
            "intent": "hotel_booking",
            "mock_data": {"hotels": hotels},
            "success": True
        }
    
    def _generate_mock_hotels(self, city, num_options=3):
        """Generate mock hotel options"""
        hotel_names = {
            "Riyadh": ["Ritz-Carlton Riyadh", "Four Seasons Riyadh", "Hyatt Regency Riyadh"],
            "Jeddah": ["Waldorf Astoria Jeddah", "Rosewood Jeddah", "InterContinental Jeddah"]
        }
        
        amenities = [
            ["Free WiFi", "Pool", "Spa"],
            ["Restaurant", "Gym", "Business Center"],
            ["Free Breakfast", "Airport Shuttle", "Concierge"]
        ]
        
        today = datetime.now()
        
        hotels = []
        for i in range(num_options):
            check_in_date = (today + timedelta(days=i+1)).strftime("%Y-%m-%d")
            check_out_date = (today + timedelta(days=i+4)).strftime("%Y-%m-%d")
            
            hotels.append({
                "name": hotel_names[city][i % len(hotel_names[city])],
                "city": city,
                "star_rating": 4 + (i % 2),
                "price_per_night": 750 + (i * 250),
                "currency": "SAR",
                "available_from": check_in_date,
                "available_to": check_out_date,
                "amenities": amenities[i % len(amenities)],
                "booking_link": f"https://example.com/hotel/{i+1}"
            })
        
        return hotels
    
    def _format_response(self, hotels, language):
        """Format the response message based on language"""
        if language.lower() == "arabic":
            return f"وجدت {len(hotels)} فنادق في {hotels[0]['city']}."
        else:
            return f"I found {len(hotels)} hotels in {hotels[0]['city']}."

class MockTripPlanningAgent:
    """Simplified Trip Planning Agent that combines flight and hotel data"""
    
    def __init__(self):
        """Initialize the Trip Planning Agent"""
        self.flight_agent = MockFlightBookingAgent()
        self.hotel_agent = MockHotelBookingAgent()
    
    def process_request(self, session_id, message, language):
        """Process a trip planning request with mock data"""
        logger.info(f"Processing trip planning request: {message}")
        
        # Extract origin, destination from message (simplified)
        origin = "Jeddah" if "Jeddah" in message else "Riyadh"
        destination = "Riyadh" if "Riyadh" in message and origin != "Riyadh" else "Jeddah"
        
        # Get mock flight and hotel data
        flight_data = self.flight_agent._generate_mock_flights(origin, destination)
        hotel_data = self.hotel_agent._generate_mock_hotels(destination)
        
        # Create trip packages
        trip_packages = self._create_trip_packages(flight_data, hotel_data)
        
        # Generate response
        response_text = self._format_response(trip_packages, language)
        
        return {
            "text": response_text,
            "intent": "trip_planning",
            "mock_data": {"trip_packages": trip_packages},
            "success": True
        }
    
    def _create_trip_packages(self, flights, hotels):
        """Create trip packages combining flights and hotels"""
        packages = []
        
        for i in range(min(len(flights), len(hotels))):
            flight = flights[i]
            hotel = hotels[i]
            
            # Calculate total cost
            flight_price = flight["price"]
            hotel_price = hotel["price_per_night"] * 3  # Assuming 3 nights
            
            packages.append({
                "package_id": f"PKG{i+1}",
                "name": f"{flight['airline']} + {hotel['name']} Package",
                "flight": flight,
                "hotel": hotel,
                "total_price": flight_price + hotel_price,
                "currency": "SAR",
                "booking_link": f"https://example.com/package/{i+1}"
            })
        
        return packages
    
    def _format_response(self, packages, language):
        """Format the response message based on language"""
        if language.lower() == "arabic":
            return f"وجدت {len(packages)} خيارات للرحلة من {packages[0]['flight']['origin']} إلى {packages[0]['flight']['destination']}."
        else:
            return f"I found {len(packages)} trip options from {packages[0]['flight']['origin']} to {packages[0]['flight']['destination']}."

def test_mock_agents():
    """Test all mock agents"""
    # Test Flight Booking Agent
    flight_agent = MockFlightBookingAgent()
    flight_response = flight_agent.process_request(
        "test_session", 
        "I need a flight from Jeddah to Riyadh", 
        "english"
    )
    print("\nFlight Booking Response:")
    print(flight_response["text"])
    print(f"Mock Data: {json.dumps(flight_response['mock_data'], indent=2)[:200]}...")
    
    # Test Hotel Booking Agent
    hotel_agent = MockHotelBookingAgent()
    hotel_response = hotel_agent.process_request(
        "test_session", 
        "I need a hotel in Riyadh", 
        "english"
    )
    print("\nHotel Booking Response:")
    print(hotel_response["text"])
    print(f"Mock Data: {json.dumps(hotel_response['mock_data'], indent=2)[:200]}...")
    
    # Test Trip Planning Agent
    trip_agent = MockTripPlanningAgent()
    trip_response = trip_agent.process_request(
        "test_session", 
        "I want to plan a trip from Jeddah to Riyadh", 
        "english"
    )
    print("\nTrip Planning Response:")
    print(trip_response["text"])
    print(f"Mock Data: {json.dumps(trip_response['mock_data'], indent=2)[:200]}...")

if __name__ == "__main__":
    test_mock_agents()

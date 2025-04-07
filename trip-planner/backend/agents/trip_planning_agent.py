"""
Trip Planning Agent for Trip Planning Assistant
Combines flight and hotel options into complete trip plans
"""
import os
import logging
import json
import re
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from .flight_booking_agent import FlightBookingAgent
from .hotel_booking_agent import HotelBookingAgent

# Import LangGraph utilities
from agents.llm_utils import create_agent_node

# Configure logging
logger = logging.getLogger(__name__)

class TripPlanningAgent:
    """
    Specialized agent for creating complete trip plans
    Combines flight and hotel information into cohesive packages
    """
    
    def __init__(self):
        """Initialize the trip planning agent"""
        logger.info("Trip Planning Agent initialized with LangGraph integration")
        self.flight_agent = FlightBookingAgent()
        self.hotel_agent = HotelBookingAgent()
    
    def process_request(self, session_id, message, language):
        """
        Process trip planning request and generate response
        
        Args:
            session_id (str): Unique identifier for the conversation
            message (str): User's message
            language (str): Language of the conversation ("english" or "arabic")
            
        Returns:
            dict: Response containing text, mock data, and success status
        """
        try:
            logger.info(f"Processing trip planning request: {message}")
            
            # Check if this is a request for an itinerary
            is_itinerary_request = self._is_itinerary_request(message)
            
            # Extract origin and destination from message
            trip_details = self._extract_trip_details(message)
            
            # Get flight options from FlightBookingAgent's mock data generator
            flight_response = self.flight_agent.process_request(
                session_id,
                f"Flight from {trip_details['origin']} to {trip_details['destination']}",
                language
            )
            flight_data = flight_response.get("mock_data", {}).get("flights", [])
            
            # Get hotel options from HotelBookingAgent's mock data generator
            hotel_response = self.hotel_agent.process_request(
                session_id,
                f"Hotel in {trip_details['destination']}",
                language
            )
            hotel_data = hotel_response.get("mock_data", {}).get("hotels", [])
            
            # Create trip packages combining flights and hotels
            trip_packages = self._create_trip_packages(flight_data, hotel_data)
            
            if is_itinerary_request:
                # Generate a detailed itinerary for the requested location and duration
                days = self._extract_trip_duration(message)
                itinerary = self._generate_itinerary(trip_details["destination"], days, language)
                
                # Generate response text with itinerary information
                response_text = self._format_itinerary_response(itinerary, trip_details, language)
                
                return {
                    "text": response_text,
                    "intent": "trip_planning",
                    "mock_data": {"trip_packages": trip_packages, "itinerary": itinerary},
                    "success": True
                }
            else:
                # Generate standard response with package options
                response_text = self._format_response(trip_packages, trip_details, language)
                
                return {
                    "text": response_text,
                    "intent": "trip_planning",
                    "mock_data": {"trip_packages": trip_packages},
                    "success": True
                }
            
        except Exception as e:
            logger.error(f"Error processing trip planning request: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error planning your trip.",
                "intent": "error",
                "mock_data": {},
                "success": False
            }
    
    def _format_response(self, trip_packages, trip_details, language):
        """
        Format the response message based on language and trip packages
        
        Args:
            trip_packages (list): List of trip package dictionaries
            trip_details (dict): Dictionary with origin and destination
            language (str): Language of the conversation ("english" or "arabic")
            
        Returns:
            str: Formatted response message
        """
        origin = trip_details.get("origin", "your origin")
        destination = trip_details.get("destination", "your destination")
        
        # Handle empty packages list
        if not trip_packages:
            if language.lower() == "arabic":
                return f"عذراً، لم أتمكن من العثور على حزم سفر من {origin} إلى {destination}. يرجى المحاولة بتواريخ أخرى."
            else:
                return f"Sorry, I couldn't find any travel packages from {origin} to {destination}. Please try with different dates."
        
        # Add default values to trip packages to avoid key errors
        for package in trip_packages:
            # Ensure flight has all required fields
            if "flight" not in package:
                package["flight"] = {
                    "airline": "Unknown Airline",
                    "origin": origin,
                    "destination": destination,
                    "departure_date": trip_details.get("departure_date", "Unknown"),
                    "departure_time": "Unknown",
                    "price": 0,
                    "currency": "SAR"
                }
            else:
                flight = package["flight"]
                flight.setdefault("airline", "Unknown Airline")
                flight.setdefault("origin", origin)
                flight.setdefault("destination", destination)
                flight.setdefault("departure_date", trip_details.get("departure_date", "Unknown"))
                flight.setdefault("departure_time", "Unknown")
                flight.setdefault("price", 0)
                flight.setdefault("currency", "SAR")
            
            # Ensure hotel has all required fields
            if "hotel" not in package:
                package["hotel"] = {
                    "name": "Unknown Hotel",
                    "star_rating": 3,
                    "price_per_night": 0,
                    "currency": "SAR"
                }
            else:
                hotel = package["hotel"]
                hotel.setdefault("name", "Unknown Hotel")
                hotel.setdefault("star_rating", 3)
                hotel.setdefault("price_per_night", 0)
                hotel.setdefault("currency", "SAR")
            
            # Ensure package has all required fields
            package.setdefault("name", f"Trip to {destination}")
            package.setdefault("total_price", 0)
            package.setdefault("currency", "SAR")
        
        try:
            if language.lower() == "arabic":
                # Arabic response
                response = f"مرحبًا! وجدت {len(trip_packages)} خيارات رحلة من {origin} إلى {destination}.\n\n"
                
                # Add flight summary
                response += "🛫 خيارات الرحلات الجوية:\n"
                for i, package in enumerate(trip_packages):
                    flight = package.get("flight", {})
                    response += f"  {i+1}. {flight.get('airline')} من {flight.get('origin')} إلى {flight.get('destination')} "
                    response += f"({flight.get('departure_date')}, {flight.get('departure_time')}) - {flight.get('price')} {flight.get('currency')}\n"
                
                # Add hotel summary
                response += "\n🏨 خيارات الفندق:\n"
                for i, package in enumerate(trip_packages):
                    hotel = package.get("hotel", {})
                    response += f"  {i+1}. {hotel.get('name')} ({hotel.get('star_rating')} نجوم) - "
                    response += f"{hotel.get('price_per_night')} {hotel.get('currency')} في الليلة\n"
                
                # Add package summary
                response += "\n📦 الحزم الكاملة:\n"
                for i, package in enumerate(trip_packages):
                    response += f"  {i+1}. {package.get('name')} - إجمالي: {package.get('total_price')} {package.get('currency')}\n"
                    response += f"     يتضمن رحلة {package.get('flight', {}).get('airline')} وإقامة في {package.get('hotel', {}).get('name')}\n"
                
                response += "\nلحجز أي من هذه الحزم، الرجاء إخباري بالخيار الذي ترغب فيه!"
                
            else:
                # English response
                response = f"Hello! I found {len(trip_packages)} trip options from {origin} to {destination}.\n\n"
                
                # Add flight summary
                response += "🛫 Flight Options:\n"
                for i, package in enumerate(trip_packages):
                    flight = package.get("flight", {})
                    response += f"  {i+1}. {flight.get('airline')} from {flight.get('origin')} to {flight.get('destination')} "
                    response += f"({flight.get('departure_date')}, {flight.get('departure_time')}) - {flight.get('price')} {flight.get('currency')}\n"
                
                # Add hotel summary
                response += "\n🏨 Hotel Options:\n"
                for i, package in enumerate(trip_packages):
                    hotel = package.get("hotel", {})
                    response += f"  {i+1}. {hotel.get('name')} ({hotel.get('star_rating')} stars) - "
                    response += f"{hotel.get('price_per_night')} {hotel.get('currency')} per night\n"
                
                # Add package summary
                response += "\n📦 Complete Packages:\n"
                for i, package in enumerate(trip_packages):
                    response += f"  {i+1}. {package.get('name')} - Total: {package.get('total_price')} {package.get('currency')}\n"
                    response += f"     Includes {package.get('flight', {}).get('airline')} flight and stay at {package.get('hotel', {}).get('name')}\n"
                
                response += "\n\nTo book any of these packages, please let me know which option you prefer!"
            
            return response
        except Exception as e:
            logger.error(f"Error formatting response: {str(e)}")
            if language.lower() == "arabic":
                return "عذراً، حدث خطأ أثناء عرض حزم السفر. يرجى المحاولة مرة أخرى لاحقاً."
            else:
                return "Sorry, I encountered an issue creating your travel packages. Please try again later."

    def _is_itinerary_request(self, message):
        """
        Check if the message is requesting an itinerary
        
        Args:
            message (str): User's message
            
        Returns:
            bool: True if itinerary request, False otherwise
        """
        message_lower = message.lower()
        itinerary_keywords = [
            "itinerary", "plan", "schedule", "things to do", "activities", "attractions", "places to visit",
            "tourist spots", "sightseeing", "day plan", "day trip", "day-by-day", "day itinerary"
        ]
        
        # Check for presence of itinerary-related keywords
        return any(keyword in message_lower for keyword in itinerary_keywords)
    
    def _extract_trip_duration(self, message):
        """
        Extract the requested duration of the trip in days
        
        Args:
            message (str): User's message
            
        Returns:
            int: Number of days for the trip, defaults to 3
        """
        message_lower = message.lower()
        
        # Look for number of days mentioned
        days_match = re.search(r"(\d+)[\s-]*day", message_lower)
        if days_match:
            try:
                return int(days_match.group(1))
            except ValueError:
                pass
        
        # Default to 3 days if no specific duration found
        return 3
    
    def _extract_trip_details(self, message):
        """
        Extract trip origin and destination from message
        
        Args:
            message (str): User's message
            
        Returns:
            dict: Dictionary with origin and destination
        """
        # Default values
        origin = "Riyadh"
        destination = "Jeddah"
        
        # Try to extract origin and destination from message
        message_lower = message.lower()
        
        # Look for common patterns like "from X to Y"
        from_to_match = re.search(r"from\s+([a-zA-Z\s]+)\s+to\s+([a-zA-Z\s]+)", message_lower)
        if from_to_match:
            origin = from_to_match.group(1).strip().title()
            destination = from_to_match.group(2).strip().title()
        
        # Look for specific mentions of cities
        cities = ["Riyadh", "Jeddah", "Makkah", "Madinah", "Dammam", "Abha", "AlUla", "Tabuk"]
        mentioned_cities = [city for city in cities if city.lower() in message_lower]
        
        if len(mentioned_cities) >= 2:
            # Assume first mention is origin, second is destination
            origin = mentioned_cities[0]
            destination = mentioned_cities[1]
        elif len(mentioned_cities) == 1:
            # Assume destination is mentioned
            destination = mentioned_cities[0]
        
        # Special handling for "in X" which usually means destination
        in_match = re.search(r"in\s+([a-zA-Z\s]+)", message_lower)
        if in_match:
            destination = in_match.group(1).strip().title()
        
        return {
            "origin": origin,
            "destination": destination,
            "departure_date": datetime.now().strftime("%Y-%m-%d")
        }
    
    def _generate_itinerary(self, destination, days, language):
        """
        Generate a detailed day-by-day itinerary for the destination
        
        Args:
            destination (str): Destination city
            days (int): Number of days for the trip
            language (str): Language of the response
            
        Returns:
            list: List of dictionaries with daily activities
        """
        # Generate itinerary for the specified number of days
        itinerary = []
        
        # Mock attractions for different cities in Saudi Arabia
        attractions = {
            "Riyadh": [
                "Kingdom Centre Tower", "National Museum of Saudi Arabia",
                "Masmak Fortress", "Diriyah", "King Abdullah Park", 
                "Riyadh Zoo", "Wadi Hanifah", "Edge of the World", 
                "Al Bujairi Heritage Park", "King Abdulaziz Historical Center"
            ],
            "Jeddah": [
                "Al-Balad (Historic Jeddah)", "Jeddah Corniche", 
                "King Fahd's Fountain", "Fakieh Aquarium", "Jeddah Sculpture Museum", 
                "Floating Mosque", "Red Sea Mall", "Atallah Happy Land Park", 
                "Al Shallal Theme Park", "Jeddah Jungle"
            ],
            "Makkah": [
                "Masjid Al-Haram", "Abraj Al-Bait", "Jabal al-Nour", 
                "Jabal Thawr", "Makkah Museum", "Mina", 
                "Muzdalifah", "Arafat", "Al Noor Mall", "Makkah Mall"
            ],
            "Madinah": [
                "Al-Masjid an-Nabawi", "Quba Mosque", "Jannat al-Baqi", 
                "Masjid al-Qiblatain", "Mount Uhud", "The Seven Mosques", 
                "Al Noor Mall", "Prophet's Mosque Museum", "Old Bazaar", 
                "Al Baqi Cemetery"
            ],
            "AlUla": [
                "Hegra Archaeological Site", "Elephant Rock", "AlUla Old Town", 
                "Dadan", "Jabal Ikmah", "AlUla Oasis", "Maraya Concert Hall", 
                "Al-Khuraybah", "Hijaz Railway Station", "Desert X AlUla"
            ],
            "Abha": [
                "Abha Palace", "Green Mountain", "Habala Village", 
                "Rijal Alma Village", "Abha Dam Lake", "Al Sooda Mountain", 
                "Cable Car", "Shada Mountain", "Abha Cultural Palace", "Asir National Park"
            ]
        }
        
        # Default to destination's attractions if not found
        city_attractions = attractions.get(destination, attractions.get("Riyadh"))
        
        # Generate activities for each day
        for day in range(1, days + 1):
            # Shuffle attractions to get random selection each time
            random.shuffle(city_attractions)
            
            # Pick 3 attractions for this day
            day_attractions = city_attractions[:3]
            
            # Create morning, afternoon, and evening activities
            daily_itinerary = {
                "day": day,
                "morning": {
                    "activity": f"Visit {day_attractions[0]}",
                    "description": f"Explore the magnificent {day_attractions[0]} in the morning when it's less crowded."
                },
                "afternoon": {
                    "activity": f"Explore {day_attractions[1]}",
                    "description": f"After lunch, spend your afternoon at {day_attractions[1]} and enjoy the local culture."
                },
                "evening": {
                    "activity": f"Experience {day_attractions[2]}",
                    "description": f"In the evening, relax and enjoy your time at {day_attractions[2]} followed by dinner at a local restaurant."
                }
            }
            
            itinerary.append(daily_itinerary)
            
            # Rotate the attractions to avoid repeating on consecutive days
            city_attractions = city_attractions[3:] + city_attractions[:3]
        
        return itinerary
    
    def _format_itinerary_response(self, itinerary, trip_details, language):
        """
        Format the itinerary response message based on language
        
        Args:
            itinerary (list): List of daily itinerary dictionaries
            trip_details (dict): Dictionary with origin and destination
            language (str): Language of the conversation ("english" or "arabic")
            
        Returns:
            str: Formatted itinerary response message
        """
        destination = trip_details.get("destination", "your destination")
        
        if language.lower() == "arabic":
            # Arabic response
            response = f"مرحبًا! إليك خطة رحلة مفصلة إلى {destination}:\n\n"
            
            for day in itinerary:
                response += f"🗓️ اليوم {day['day']}:\n"
                response += f"   🌅 الصباح: {day['morning']['activity']}\n"
                response += f"      {day['morning']['description']}\n"
                response += f"   🌞 بعد الظهر: {day['afternoon']['activity']}\n"
                response += f"      {day['afternoon']['description']}\n"
                response += f"   🌆 المساء: {day['evening']['activity']}\n"
                response += f"      {day['evening']['description']}\n\n"
            
            response += "هذه خطة رحلة مقترحة. هل ترغب في تعديلها أو حجز تذاكر طيران وفنادق؟"
            
        else:
            # English response
            response = f"Hello! Here's a detailed itinerary for your trip to {destination}:\n\n"
            
            for day in itinerary:
                response += f"🗓️ Day {day['day']}:\n"
                response += f"   🌅 Morning: {day['morning']['activity']}\n"
                response += f"      {day['morning']['description']}\n"
                response += f"   🌞 Afternoon: {day['afternoon']['activity']}\n"
                response += f"      {day['afternoon']['description']}\n"
                response += f"   🌆 Evening: {day['evening']['activity']}\n"
                response += f"      {day['evening']['description']}\n\n"
            
            response += "This is a suggested itinerary. Would you like to modify it or book flights and hotels?"
        
        return response
    
    def _create_trip_packages(self, flights, hotels):
        """
        Create trip packages by combining flight and hotel options
        
        Args:
            flights (list): List of flight dictionaries
            hotels (list): List of hotel dictionaries
            
        Returns:
            list: List of trip package dictionaries
        """
        # If no flights or hotels, return empty list
        if not flights or not hotels:
            return []
            
        # Create at least 5 package options with various combinations
        packages = []
        for i in range(min(12, max(5, len(flights) * len(hotels)))):
            flight_idx = i % len(flights)
            hotel_idx = (i // len(flights)) % len(hotels)
            
            flight = flights[flight_idx]
            hotel = hotels[hotel_idx]
            
            # Calculate total price
            flight_price = flight.get("price", 0)
            hotel_price = hotel.get("price_per_night", 0) * 3  # Assume 3 nights
            total_price = flight_price + hotel_price
            
            # Create package
            package = {
                "name": f"{flight.get('airline', 'Flight')} + {hotel.get('name', 'Hotel')}",
                "flight": flight,
                "hotel": hotel,
                "total_price": total_price,
                "currency": flight.get("currency", "SAR")
            }
            
            packages.append(package)
        
        return packages

# Create LangGraph node function
def create_trip_planning_node():
    """
    Create a LangGraph node for the trip planning agent
    
    Returns:
        Callable: Node function for LangGraph
    """
    trip_planning_agent = TripPlanningAgent()
    
    def trip_planning_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Trip planning node function for LangGraph"""
        session_id = state.get("session_id", "")
        message = state.get("user_message", "")
        language = state.get("language", "english")
        
        # Process the message with the trip planning agent
        response = trip_planning_agent.process_request(session_id, message, language)
        
        # Update the state with the response
        state["response"] = response.get("text", "")
        state["intent"] = response.get("intent", "")
        state["mock_data"] = response.get("mock_data", {})
        state["success"] = response.get("success", False)
        
        return state
    
    return trip_planning_node

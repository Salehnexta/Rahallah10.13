"""
Trip Planning Agent for Trip Planning Assistant
Combines flight and hotel options into complete trip plans
"""
import os
import logging
import json
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
            
            # Generate response text based on language
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
                
                response += "\nTo book any of these packages, please let me know which option you prefer!"
            
            return response
        except Exception as e:
            logger.error(f"Error formatting trip response: {str(e)}")
            if language.lower() == "arabic":
                return "عذراً، واجهت مشكلة في إنشاء الحزم السياحية. يرجى المحاولة مرة أخرى لاحقاً."
            else:
                return "Sorry, I encountered an issue creating your travel packages. Please try again later."
    
    def _extract_trip_details(self, message):
        """
        Extract trip details from user message
        
        Args:
            message (str): User's message
            
        Returns:
            dict: Extracted trip details with default values
        """
        # Initialize with default values
        trip_details = {
            "origin": "Riyadh",
            "destination": "Jeddah",
            "departure_date": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "return_date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "travelers": 2,
            "duration": 3,
            "interests": ["Sightseeing", "Shopping"]
        }
        
        try:
            # Try to extract city names
            from_pattern = r"from\s+([A-Za-z\s]+)\s+to"
            to_pattern = r"to\s+([A-Za-z\s]+)"
            import re
            
            # Look for 'from [city] to' pattern
            from_match = re.search(from_pattern, message, re.IGNORECASE)
            if from_match and from_match.group(1).strip():
                trip_details["origin"] = from_match.group(1).strip()
            
            # Look for 'to [city]' pattern
            to_match = re.search(to_pattern, message, re.IGNORECASE)
            if to_match and to_match.group(1).strip():
                trip_details["destination"] = to_match.group(1).strip()
            
            # Extract dates (YYYY-MM-DD format)
            date_pattern = r"\d{4}-\d{2}-\d{2}"
            dates = re.findall(date_pattern, message)
            if dates:
                trip_details['departure_date'] = dates[0]
                if len(dates) > 1:
                    trip_details['return_date'] = dates[1]
            
            # Look for travelers count
            traveler_pattern = r"(\d+)\s+(?:traveler|passenger|people|person)s?"
            traveler_match = re.search(traveler_pattern, message, re.IGNORECASE)
            if traveler_match:
                trip_details['travelers'] = int(traveler_match.group(1))
            
            # Calculate duration based on dates
            try:
                departure = datetime.strptime(trip_details['departure_date'], '%Y-%m-%d')
                return_date = datetime.strptime(trip_details['return_date'], '%Y-%m-%d')
                trip_details['duration'] = (return_date - departure).days
            except:
                # Keep default duration if date parsing fails
                pass
            
            # Extract interests
            interest_keywords = {
                "beach": ["beach", "swimming", "ocean", "sea"],
                "culture": ["culture", "museum", "history", "art"],
                "adventure": ["adventure", "hiking", "safari", "outdoor"],
                "shopping": ["shopping", "mall", "souq", "market"],
                "food": ["food", "cuisine", "restaurant", "dining"],
                "relaxation": ["spa", "resort", "relax", "peaceful"],
                "sightseeing": ["sightseeing", "landmark", "tourist"]
            }
            
            interests = []
            for interest, keywords in interest_keywords.items():
                if any(keyword in message.lower() for keyword in keywords):
                    interests.append(interest.capitalize())
            
            if interests:
                trip_details['interests'] = interests
            
            logger.info(f"Extracted trip details: {trip_details}")
            return trip_details
            
        except Exception as e:
            logger.error(f"Error extracting trip info: {str(e)}")
            # Return the defaults since we already set them
            return trip_details
    
    def _format_trip_response(self, llm_response, trip_info):
        """Format the trip plan response"""
        try:
            # Extract JSON if it's in the response
            json_start = llm_response.find('{')
            json_end = llm_response.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                trip_data = json.loads(llm_response[json_start:json_end])
                
                # Format the response with both text and structured data
                formatted = f"""
                Here's your trip plan to {trip_info['destination']}:
                
                {llm_response[:json_start].strip()}
                
                Total Price: {trip_data.get('total_price', 'N/A')} SAR
                """
                return formatted
            
            return llm_response
            
        except Exception as e:
            logger.error(f"Error formatting trip response: {str(e)}")
            return "I apologize, there was an error formatting your trip plan."
    
    def _create_trip_packages(self, flight_data, hotel_data):
        """
        Combine flight and hotel options into complete trip packages
        
        Args:
            flight_data (list): List of flight options
            hotel_data (list): List of hotel options
            
        Returns:
            list: List of trip packages combining flights and hotels
        """
        try:
            # Initialize empty list for trip packages
            trip_packages = []
            
            # Handle empty input data
            if not flight_data or not hotel_data:
                logger.warning("No flight or hotel data available to create packages")
                return trip_packages
            
            # Limit number of combinations to avoid too many packages
            max_flights = min(len(flight_data), 3)
            max_hotels = min(len(hotel_data), 3)
            
            # Create combinations of flights and hotels
            for i in range(max_flights):
                flight = flight_data[i]
                # Ensure required flight fields exist
                flight.setdefault('airline', "Unknown Airline")
                flight.setdefault('flight_number', "XXX")
                flight.setdefault('price', 0)
                flight.setdefault('currency', "SAR")
                
                for j in range(max_hotels):
                    hotel = hotel_data[j]
                    # Ensure required hotel fields exist
                    hotel.setdefault('name', "Unknown Hotel")
                    hotel.setdefault('star_rating', 3)
                    hotel.setdefault('price_per_night', 0)
                    hotel.setdefault('currency', "SAR")
                    
                    # Create a package with one flight and one hotel
                    # Calculate total price based on hotel nights and flight cost
                    package_name = f"{flight.get('airline')} + {hotel.get('name')}"
                    
                    # Default to 3 nights if check_in/check_out not available
                    nights = 3
                    if 'check_in' in hotel and 'check_out' in hotel:
                        try:
                            from datetime import datetime
                            check_in = datetime.strptime(hotel['check_in'], '%Y-%m-%d')
                            check_out = datetime.strptime(hotel['check_out'], '%Y-%m-%d')
                            nights = (check_out - check_in).days
                            nights = max(1, nights)  # Ensure at least 1 night
                        except:
                            nights = 3  # Default if date parsing fails
                    
                    # Calculate total price
                    hotel_total = hotel.get('price_per_night', 0) * nights
                    flight_price = flight.get('price', 0)
                    total_price = hotel_total + flight_price
                    
                    # Use hotel currency as default for package
                    currency = hotel.get('currency', 'SAR')
                    
                    # Create package object
                    package = {
                        "name": package_name,
                        "flight": flight,
                        "hotel": hotel,
                        "nights": nights,
                        "total_price": total_price,
                        "currency": currency,
                        "description": f"Flight with {flight.get('airline')} and {nights} nights at {hotel.get('name')}"
                    }
                    
                    trip_packages.append(package)
            
            logger.info(f"Created {len(trip_packages)} trip packages")
            return trip_packages
            
        except Exception as e:
            logger.error(f"Error creating trip packages: {str(e)}")
            return []  # Return empty list on error
    
    def _generate_mock_trip_data(self, trip_info):
        """Generate mock data for a complete trip plan"""
        try:
            # Generate mock flight data
            flight_data = {
                "airline": "Saudia",
                "flight_number": "SV123",
                "departure": trip_info["start_date"],
                "return": trip_info["end_date"],
                "price": "1200 SAR"
            }
            
            # Generate mock hotel data
            hotel_data = {
                "name": "Luxury Hotel Riyadh",
                "rating": 5,
                "location": "Downtown Riyadh",
                "price_per_night": "800 SAR",
                "total_price": str(int(flight_data["price"].split()[0]) + 
                                 int(hotel_data["price_per_night"].split()[0]) * trip_info["duration"]) + " SAR"
            }
            
            return {
                "flight": flight_data,
                "hotel": hotel_data,
                "total_price": hotel_data["total_price"],
                "activities": self._generate_mock_activities(trip_info["destination"])  # TO DO: Implement activity generation
            }
            
        except Exception as e:
            logger.error(f"Error generating mock trip data: {str(e)}")
            return {}
    
    def _generate_mock_activities(self, destination):
        """Generate mock tourist activities for the destination"""
        # TO DO: Implement activity generation based on destination
        return []


# Create LangGraph node function
def create_trip_planning_node():
    """
    Create a LangGraph node for the trip planning agent
    
    Returns:
        Callable: Node function for LangGraph
    """
    agent = TripPlanningAgent()
    return create_agent_node("trip_planning_agent", agent.process_request)

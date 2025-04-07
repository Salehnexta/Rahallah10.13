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
        origin = trip_details["origin"]
        destination = trip_details["destination"]
        
        if language.lower() == "arabic":
            # Arabic response
            response = f"مرحبًا! وجدت {len(trip_packages)} خيارات رحلة من {origin} إلى {destination}.\n\n"
            
            # Add flight summary
            response += "🛫 خيارات الرحلات الجوية:\n"
            for i, package in enumerate(trip_packages):
                flight = package["flight"]
                response += f"  {i+1}. {flight['airline']} من {flight['origin']} إلى {flight['destination']} "
                response += f"({flight['departure_date']}, {flight['departure_time']}) - {flight['price']} {flight['currency']}\n"
            
            # Add hotel summary
            response += "\n🏨 خيارات الفندق:\n"
            for i, package in enumerate(trip_packages):
                hotel = package["hotel"]
                response += f"  {i+1}. {hotel['name']} ({hotel['star_rating']} نجوم) - "
                response += f"{hotel['price_per_night']} {hotel['currency']} في الليلة\n"
            
            # Add package summary
            response += "\n📦 الحزم الكاملة:\n"
            for i, package in enumerate(trip_packages):
                response += f"  {i+1}. {package['name']} - إجمالي: {package['total_price']} {package['currency']}\n"
                response += f"     يتضمن رحلة {package['flight']['airline']} وإقامة في {package['hotel']['name']}\n"
            
            response += "\nلحجز أي من هذه الحزم، الرجاء إخباري بالخيار الذي ترغب فيه!"
            
        else:
            # English response
            response = f"Hello! I found {len(trip_packages)} trip options from {origin} to {destination}.\n\n"
            
            # Add flight summary
            response += "🛫 Flight Options:\n"
            for i, package in enumerate(trip_packages):
                flight = package["flight"]
                response += f"  {i+1}. {flight['airline']} from {flight['origin']} to {flight['destination']} "
                response += f"({flight['departure_date']}, {flight['departure_time']}) - {flight['price']} {flight['currency']}\n"
            
            # Add hotel summary
            response += "\n🏨 Hotel Options:\n"
            for i, package in enumerate(trip_packages):
                hotel = package["hotel"]
                response += f"  {i+1}. {hotel['name']} ({hotel['star_rating']} stars) - "
                response += f"{hotel['price_per_night']} {hotel['currency']} per night\n"
            
            # Add package summary
            response += "\n📦 Complete Packages:\n"
            for i, package in enumerate(trip_packages):
                response += f"  {i+1}. {package['name']} - Total: {package['total_price']} {package['currency']}\n"
                response += f"     Includes {package['flight']['airline']} flight and stay at {package['hotel']['name']}\n"
            
            response += "\nTo book any of these packages, please let me know which option you prefer!"
        
        return response
    
    def _extract_trip_details(self, message):
        """Extract trip planning parameters from the message"""
        try:
            # TO DO: Implement more sophisticated parameter extraction
            # For now, return a basic structure
            return {
                "destination": "",  # Will be extracted from message
                "duration": 3,    # Default duration
                "start_date": "",  # Will be extracted from message
                "end_date": "",    # Will be calculated based on duration
                "interests": []    # Will be extracted from message
            }
        except Exception as e:
            logger.error(f"Error extracting trip info: {str(e)}")
            return None
    
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

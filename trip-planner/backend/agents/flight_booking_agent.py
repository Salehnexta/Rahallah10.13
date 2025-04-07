"""
Flight Booking Agent for Trip Planning Assistant
Generates fictional but realistic flight options
"""
import logging
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

# Import LangGraph utilities
from agents.llm_utils import create_agent_node

# Configure logging
logger = logging.getLogger(__name__)

# System prompt for the Flight Booking Agent
SYSTEM_PROMPT = """
You are the Flight Booking Agent for a Saudi-focused Trip Planning Assistant.
Your role is to generate fictional but realistic flight options based on user requests.

When generating flight options:
1. Create 3-5 fictional flight options with Saudi airlines (Saudia, flynas, flyadeal)
2. Include realistic flight numbers, times, durations, and prices
3. Focus on flights to/from Saudi cities (Riyadh, Jeddah, Dammam, Medina, etc.)
4. Include both economy and business class options when appropriate
5. Add realistic amenities based on the airline and class
6. Generate fictional but plausible booking links

Important guidelines:
- Make the options varied in terms of price, time, and convenience
- Ensure times and durations are realistic for the routes
- Use Saudi Riyals (SAR) for pricing
- Support both English and Arabic responses
- NEVER claim these are real flights - they are fictional examples

Format the response in a clean, organized way that's easy for users to compare options.
"""

# Saudi airlines
AIRLINES = [
    {"name": "Saudia", "code": "SV", "base_price": 800},
    {"name": "flynas", "code": "XY", "base_price": 600},
    {"name": "flyadeal", "code": "F3", "base_price": 500}
]

# Saudi cities and airports
SAUDI_AIRPORTS = [
    {"city": "Riyadh", "code": "RUH", "name": "King Khalid International Airport"},
    {"city": "Jeddah", "code": "JED", "name": "King Abdulaziz International Airport"},
    {"city": "Dammam", "code": "DMM", "name": "King Fahd International Airport"},
    {"city": "Medina", "code": "MED", "name": "Prince Mohammad Bin Abdulaziz International Airport"},
    {"city": "Abha", "code": "AHB", "name": "Abha International Airport"},
    {"city": "Tabuk", "code": "TUU", "name": "Tabuk Regional Airport"}
]

class FlightBookingAgent:
    """Specialized agent for handling flight booking requests
    Generates realistic flight options using mock data"""
    
    def __init__(self):
        """Initialize the flight booking agent"""
        self.mock_data = {}  # Store mock data for the current session
        logger.info("Flight Booking Agent initialized with LangGraph integration")
        
    def process_request(self, session_id, message, language):
        """
        Process a flight booking request
        
        Args:
            session_id (str): Unique identifier for the conversation
            message (str): User's request message
            language (str): Language of the request ('english' or 'arabic')
            
        Returns:
            dict: Response containing text and mock data
        """
        try:
            logger.info(f"Processing flight booking request: {message}")
            
            # Extract flight information from the message
            flight_info = self._extract_flight_info(message)
            
            # Generate mock flight options
            mock_flights = self._generate_mock_flight_options(flight_info)
            mock_data = {"flights": mock_flights}
            
            # Store mock data for this session
            self.mock_data[session_id] = mock_data
            
            # Format response based on language
            response_text = self._format_flight_response(mock_data, flight_info, language)
            
            return {
                "text": response_text,
                "mock_data": mock_data,
                "success": True,
                "intent": "flight_booking"
            }
            
        except Exception as e:
            logger.error(f"Error in FlightBookingAgent: {str(e)}")
            error_msg = "I'm sorry, I encountered an error processing your flight booking request."
            if language.lower() == 'arabic':
                error_msg = "عذراً، حدث خطأ أثناء معالجة طلب حجز الرحلة الخاص بك."
                
            return {
                "text": error_msg,
                "mock_data": {},
                "success": False,
                "intent": "error"
            }
    
    def _extract_flight_info(self, message):
        """
        Extract flight information from user message
        
        Args:
            message (str): User's message
            
        Returns:
            dict: Extracted flight information
        """
        try:
            # Basic flight information extraction
            # This should be enhanced with a more sophisticated NLP approach
            flight_info = {}
            
            # Look for common keywords
            if "to" in message.lower():
                parts = message.lower().split("to")
                if len(parts) > 1:
                    flight_info['destination'] = parts[1].strip()
                if len(parts[0].split()) > 1:
                    flight_info['origin'] = parts[0].split()[-1].strip()
            
            # Look for dates
            import re
            date_pattern = r"\d{4}-\d{2}-\d{2}"
            dates = re.findall(date_pattern, message)
            if dates:
                flight_info['departure_date'] = dates[0]
                if len(dates) > 1:
                    flight_info['return_date'] = dates[1]
            
            return flight_info
            
        except Exception as e:
            logger.error(f"Error extracting flight info: {str(e)}")
            return {}
    
    def _format_flight_response(self, mock_data, flight_info, language):
        """
        Format the flight options response
        
        Args:
            mock_data (dict): Mock flight data
            flight_info (dict): Extracted flight information
            language (str): Language of the response
            
        Returns:
            str: Formatted response text
        """
        flights = mock_data.get("flights", [])
        if not flights:
            if language.lower() == 'arabic':
                return "عذراً، لم أتمكن من العثور على خيارات رحلات تطابق معاييرك."
            else:
                return "Sorry, I couldn't find any flight options matching your criteria."
        
        origin = flight_info.get("origin", "your origin")
        destination = flight_info.get("destination", "your destination")
        date = flight_info.get("departure_date", "the specified date")
        
        if language.lower() == 'arabic':
            response = f"وجدت {len(flights)} خيارات رحلات من {origin} إلى {destination} ليوم {date}:\n\n"
            
            for i, flight in enumerate(flights, 1):
                response += f"{i}. {flight['airline']} {flight['flight_number']} - {flight['departure_time']} إلى {flight['arrival_time']}\n"
                response += f"   السعر: {flight['price']} {flight['currency']} ({flight['class']})\n"
                response += f"   المدة: {flight['duration']} | المرافق: {', '.join(flight['amenities'])}\n\n"
            
            response += "هل ترغب في المتابعة مع حجز أي من هذه الخيارات؟"
        else:
            response = f"I found {len(flights)} flight options from {origin} to {destination} for {date}:\n\n"
            
            for i, flight in enumerate(flights, 1):
                response += f"{i}. {flight['airline']} {flight['flight_number']} - {flight['departure_time']} to {flight['arrival_time']}\n"
                response += f"   Price: {flight['price']} {flight['currency']} ({flight['class']})\n"
                response += f"   Duration: {flight['duration']} | Amenities: {', '.join(flight['amenities'])}\n\n"
            
            response += "Would you like to proceed with booking any of these options?"
        
        return response
    
    def _generate_mock_flight_options(self, flight_info):
        """
        Generate mock flight options
        
        Args:
            flight_info (dict): Extracted flight information
            
        Returns:
            list: Mock flight options
        """
        try:
            # Generate mock flight options based on the flight information
            # This should be enhanced with a more sophisticated approach
            mock_flight_options = []
            
            for airline in AIRLINES:
                flight_number = f"{airline['code']} {random.randint(100, 999)}"
                departure_time = f"{flight_info['departure_date']} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
                arrival_time = f"{flight_info['departure_date']} {random.randint(0, 23):02d}:{random.randint(0, 59):02d}"
                duration = f"{random.randint(1, 5)} hours {random.randint(0, 59)} minutes"
                price = airline['base_price'] + random.randint(-100, 100)
                seat_options = {
                    "economy": random.randint(10, 50),
                    "business": random.randint(5, 20)
                }
                
                mock_flight_options.append({
                    "airline": airline['name'],
                    "flight_number": flight_number,
                    "departure_time": departure_time,
                    "arrival_time": arrival_time,
                    "duration": duration,
                    "price": price,
                    "seat_options": seat_options
                })
            
            return mock_flight_options
            
        except Exception as e:
            logger.error(f"Error generating mock flight options: {str(e)}")
            return []


# Create LangGraph node function
def create_flight_booking_node():
    """
    Create a LangGraph node for the flight booking agent
    
    Returns:
        Callable: Node function for LangGraph
    """
    agent = FlightBookingAgent()
    return create_agent_node("flight_booking_agent", agent.process_request)

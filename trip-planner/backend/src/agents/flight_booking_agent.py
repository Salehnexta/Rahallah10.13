"""
Flight Booking Agent for Trip Planning Assistant
Generates fictional but realistic flight options
"""
import logging
import json
import random
from datetime import datetime, timedelta
from .langchain_utils import create_basic_chain
from .llm_utils import LLMUtils

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
    """
    Specialized agent for handling flight booking requests
    Uses DeepSeek LLM to generate realistic flight options
    """
    
    def __init__(self):
        """Initialize the flight booking agent"""
        self.llm_utils = LLMUtils()
        self.mock_data = {}  # Store mock data for the current session
        
    def process_request(self, session_id, message, language):
        """
        Process a flight booking request
        
        Args:
            session_id (str): Unique session identifier
            message (str): User's message
            language (str): Language of the conversation
            
        Returns:
            dict: Response with flight options or error message
        """
        try:
            # Extract flight information from the message
            flight_info = self._extract_flight_info(message)
            
            if not flight_info:
                return {
                    "text": "I'm sorry, I couldn't understand your flight request. Please provide the origin and destination cities.",
                    "intent": "error",
                    "language": language
                }
            
            # Generate mock flight options using DeepSeek
            response = self.llm_utils.generate_flight_options(
                origin=flight_info.get('origin', ''),
                destination=flight_info.get('destination', ''),
                departure_date=flight_info.get('departure_date', ''),
                return_date=flight_info.get('return_date', None)
            )
            
            if not response.get('success'):
                return {
                    "text": f"I'm sorry, I encountered an error generating flight options: {response.get('error', 'Unknown error')}",
                    "intent": "error",
                    "language": language
                }
            
            # Store mock data for this session
            self.mock_data[session_id] = response.get('mock_data', {})
            
            # Format the response
            formatted_response = self._format_flight_response(response['mock_data'], language)
            
            return {
                "text": formatted_response,
                "intent": "flight_options",
                "language": language,
                "mock_data": response['mock_data']  # Include raw mock data for frontend
            }
            
        except Exception as e:
            logger.error(f"Error in FlightBookingAgent: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your flight request.",
                "intent": "error",
                "language": language
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
    
    def _format_flight_response(self, mock_data, language):
        """
        Format the flight options response
        
        Args:
            mock_data (dict): Mock flight data
            language (str): Language of the response
            
        Returns:
            str: Formatted response text
        """
        try:
            if not mock_data or 'flights' not in mock_data:
                return "I'm sorry, I couldn't find any flight options at the moment."
            
            flights = mock_data['flights']
            response = "Here are your flight options:\n\n"
            
            for i, flight in enumerate(flights, 1):
                response += f"Flight {i}:\n"
                response += f"Airline: {flight.get('airline', 'Unknown')}\n"
                response += f"Departure: {flight.get('departure_time', 'Unknown')}\n"
                response += f"Arrival: {flight.get('arrival_time', 'Unknown')}\n"
                response += f"Duration: {flight.get('duration', 'Unknown')}\n"
                response += f"Price: {flight.get('price', 'Unknown')} SAR\n"
                response += f"Seat Options: {flight.get('seat_options', {}).get('economy', 0)} Economy, {flight.get('seat_options', {}).get('business', 0)} Business\n"
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting flight response: {str(e)}")
            return "I'm sorry, I encountered an error formatting the flight options."

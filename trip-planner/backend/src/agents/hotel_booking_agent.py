"""
Hotel Booking Agent for Trip Planning Assistant
Uses DeepSeek LLM to generate realistic hotel options
"""
import logging
import json
from datetime import datetime
from .llm_utils import LLMUtils

# Configure logging
logger = logging.getLogger(__name__)

class HotelBookingAgent:
    """
    Specialized agent for handling hotel booking requests
    Uses DeepSeek LLM to generate realistic hotel options
    """
    
    def __init__(self):
        """Initialize the hotel booking agent"""
        self.llm_utils = LLMUtils()
        self.mock_data = {}  # Store mock data for the current session
        logger.info("Hotel Booking Agent initialized")
    
    def process_request(self, session_id, message, language):
        """
        Process a hotel booking request
        
        Args:
            session_id (str): Unique session identifier
            message (str): User's message
            language (str): Language of the conversation
            
        Returns:
            dict: Response with hotel options or error message
        """
        try:
            # Extract hotel information from the message
            hotel_info = self._extract_hotel_info(message)
            
            if not hotel_info:
                return {
                    "text": "I'm sorry, I couldn't understand your hotel request. Please provide the destination city.",
                    "intent": "error",
                    "language": language
                }
            
            # Generate mock hotel options using DeepSeek
            response = self.llm_utils.generate_hotel_options(
                destination=hotel_info.get('destination', ''),
                check_in=hotel_info.get('check_in', ''),
                check_out=hotel_info.get('check_out', '')
            )
            
            if not response.get('success'):
                return {
                    "text": f"I'm sorry, I encountered an error generating hotel options: {response.get('error', 'Unknown error')}",
                    "intent": "error",
                    "language": language
                }
            
            # Store mock data for this session
            self.mock_data[session_id] = response.get('mock_data', {})
            
            # Format the response
            formatted_response = self._format_hotel_response(response['mock_data'], language)
            
            return {
                "text": formatted_response,
                "intent": "hotel_options",
                "language": language,
                "mock_data": response['mock_data']  # Include raw mock data for frontend
            }
            
        except Exception as e:
            logger.error(f"Error in HotelBookingAgent: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your hotel request.",
                "intent": "error",
                "language": language
            }
    
    def _extract_hotel_info(self, message):
        """
        Extract hotel information from user message
        
        Args:
            message (str): User's message
            
        Returns:
            dict: Extracted hotel information
        """
        try:
            # Basic hotel information extraction
            hotel_info = {}
            
            # Look for destination
            import re
            # Look for city names (improved pattern matching needed)
            city_pattern = r"\b(?:Riyadh|Jeddah|Dammam|Medina|Mecca|Al Khobar|Tabuk|Abha|Taif|Yanbu)\b"
            cities = re.findall(city_pattern, message, re.IGNORECASE)
            if cities:
                hotel_info['destination'] = cities[0]
            
            # Look for dates
            date_pattern = r"\d{4}-\d{2}-\d{2}"
            dates = re.findall(date_pattern, message)
            if dates:
                hotel_info['check_in'] = dates[0]
                if len(dates) > 1:
                    hotel_info['check_out'] = dates[1]
            
            # Look for number of guests
            guest_pattern = r"\b(?:1|2|3|4|5|6|7|8|9)\b\s*(?:guest|people|person)s?"
            guest_match = re.search(guest_pattern, message, re.IGNORECASE)
            if guest_match:
                hotel_info['guests'] = int(guest_match.group(0).split()[0])
            
            return hotel_info
            
        except Exception as e:
            logger.error(f"Error extracting hotel info: {str(e)}")
            return {}
    
    def _format_hotel_response(self, mock_data, language):
        """
        Format the hotel options response
        
        Args:
            mock_data (dict): Mock hotel data
            language (str): Language of the response
            
        Returns:
            str: Formatted response text
        """
        try:
            if not mock_data or 'hotels' not in mock_data:
                return "I'm sorry, I couldn't find any hotel options at the moment."
            
            hotels = mock_data['hotels']
            response = "Here are your hotel options:\n\n"
            
            for i, hotel in enumerate(hotels, 1):
                response += f"Hotel {i}:\n"
                response += f"Name: {hotel.get('name', 'Unknown')}\n"
                response += f"Rating: {hotel.get('stars', 'Unknown')} stars\n"
                response += f"Location: {hotel.get('location', 'Unknown')}\n"
                response += f"Price per night: {hotel.get('price_per_night', 'Unknown')} SAR\n"
                
                if 'amenities' in hotel:
                    amenities = ", ".join(hotel['amenities'])
                    response += f"Amenities: {amenities}\n"
                
                if 'room_types' in hotel:
                    room_text = ", ".join([
                        f"{k}: {v}" for k, v in hotel['room_types'].items()
                    ])
                    response += f"Room Types: {room_text}\n"
                
                response += "\n"
            
            return response
            
        except Exception as e:
            logger.error(f"Error formatting hotel response: {str(e)}")
            return "I'm sorry, I encountered an error formatting the hotel options."

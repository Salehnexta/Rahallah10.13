"""
Hotel Booking Agent for Trip Planning Assistant
Generates fictional but realistic hotel options
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

# System prompt for the Hotel Booking Agent
SYSTEM_PROMPT = """
You are the Hotel Booking Agent for a Saudi-focused Trip Planning Assistant.
Your role is to generate fictional but realistic hotel options based on user requests.

When generating hotel options:
1. Create 3-5 fictional hotels with realistic names and ratings
2. Include realistic amenities and services
3. Generate varied room types with different prices
4. Include both luxury and budget options
5. Add fictional but plausible booking links

Important guidelines:
- Make the options varied in terms of price, amenities, and location
- Use Saudi Riyals (SAR) for pricing
- Support both English and Arabic responses
- NEVER claim these are real hotels - they are fictional examples

Format the response in a clean, organized way that's easy for users to compare options.
"""

class HotelBookingAgent:
    """
    Specialized agent for handling hotel booking requests
    Generates fictional but realistic hotel options
    """
    
    def __init__(self):
        """Initialize the hotel booking agent"""
        logger.info("Hotel Booking Agent initialized with LangGraph integration")
    
    def process_request(self, session_id, message, language):
        """
        Process a hotel booking request
        
        Args:
            session_id (str): Unique identifier for the conversation
            message (str): User's request message
            language (str): Language of the request ('english' or 'arabic')
            
        Returns:
            dict: Response containing text and mock data
        """
        try:
            logger.info(f"Processing hotel booking request: {message}")
            
            # Extract hotel information from the message
            hotel_info = self._extract_hotel_info(message)
            
            # Generate mock hotel options
            mock_hotels = self._generate_mock_hotel_options(hotel_info)
            mock_data = {"hotels": mock_hotels}
            
            # Format response based on language
            response_text = self._format_hotel_response(mock_data, hotel_info, language)
            
            return {
                "text": response_text,
                "mock_data": mock_data,
                "success": True,
                "intent": "hotel_booking"
            }
            
        except Exception as e:
            logger.error(f"Error in HotelBookingAgent: {str(e)}")
            error_msg = "I'm sorry, I encountered an error processing your hotel booking request."
            if language.lower() == 'arabic':
                error_msg = "عذراً، حدث خطأ أثناء معالجة طلب حجز الفندق الخاص بك."
                
            return {
                "text": error_msg,
                "mock_data": {},
                "success": False,
                "intent": "error"
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
    
    def _format_hotel_response(self, mock_data, hotel_info, language):
        """
        Format the hotel options response
        
        Args:
            mock_data (dict): Mock hotel data
            hotel_info (dict): Extracted hotel information
            language (str): Language of the response
            
        Returns:
            str: Formatted response text
        """
        hotels = mock_data.get("hotels", [])
        if not hotels:
            if language.lower() == 'arabic':
                return "عذراً، لم أتمكن من العثور على خيارات فنادق تطابق معاييرك."
            else:
                return "Sorry, I couldn't find any hotel options matching your criteria."
        
        city = hotel_info.get("destination", "your destination")
        check_in = hotel_info.get("check_in", "your check-in date")
        check_out = hotel_info.get("check_out", "your check-out date")
        
        if language.lower() == 'arabic':
            response = f"وجدت {len(hotels)} خيارات فنادق في {city} من {check_in} إلى {check_out}:\n\n"
            
            for i, hotel in enumerate(hotels, 1):
                response += f"{i}. {hotel['name']} - {hotel['star_rating']} نجوم\n"
                response += f"   السعر: {hotel['price_per_night']} {hotel['currency']} في الليلة\n"
                response += f"   المرافق: {', '.join(hotel['amenities'])}\n\n"
            
            response += "هل ترغب في المتابعة مع حجز أي من هذه الخيارات؟"
        else:
            response = f"I found {len(hotels)} hotel options in {city} from {check_in} to {check_out}:\n\n"
            
            for i, hotel in enumerate(hotels, 1):
                response += f"{i}. {hotel['name']} - {hotel['star_rating']} stars\n"
                response += f"   Price: {hotel['price_per_night']} {hotel['currency']} per night\n"
                response += f"   Amenities: {', '.join(hotel['amenities'])}\n\n"
            
            response += "Would you like to proceed with booking any of these options?"
        
        return response
    
    def _generate_mock_hotel_options(self, hotel_info):
        """
        Generate mock hotel options
        
        Args:
            hotel_info (dict): Extracted hotel information
            
        Returns:
            list: Mock hotel options
        """
        try:
            # List of mock hotel names
            hotel_names = [
                "Al Faisaliah Hotel",
                "Ritz-Carlton Riyadh",
                "Four Seasons Hotel Riyadh",
                "JW Marriott Hotel Riyadh",
                "Fairmont Riyadh",
                "Hilton Riyadh",
                "Pullman Riyadh",
                "Sheraton Riyadh"
            ]
            
            # Generate mock hotel options
            mock_hotel_options = []
            
            for i in range(random.randint(3, 5)):
                hotel = {
                    "name": hotel_names[i % len(hotel_names)],
                    "star_rating": random.randint(3, 5),
                    "price": {
                        "per_night": random.randint(500, 3000),
                        "currency": "SAR"
                    },
                    "amenities": random.sample([
                        "Free WiFi",
                        "Breakfast included",
                        "Airport shuttle",
                        "Gym",
                        "Swimming pool",
                        "Spa",
                        "Restaurant"
                    ], random.randint(3, 5)),
                    "room_types": {
                        "standard": {
                            "available": random.randint(10, 20),
                            "price": random.randint(500, 1000)
                        },
                        "deluxe": {
                            "available": random.randint(5, 15),
                            "price": random.randint(1000, 2000)
                        },
                        "suite": {
                            "available": random.randint(2, 8),
                            "price": random.randint(2000, 3000)
                        }
                    },
                    "total_rooms": random.randint(100, 300),
                    "location": {
                        "city": hotel_info.get("destination", "Riyadh"),
                        "area": random.choice([
                            "Al-Malaz",
                            "Al-Salam",
                            "Al-Olaya",
                            "Al-Rawdah",
                            "Al-Nazar"
                        ])
                    }
                }
                mock_hotel_options.append(hotel)
            
            return mock_hotel_options
            
        except Exception as e:
            logger.error(f"Error generating mock hotel options: {str(e)}")
            return []


# Create LangGraph node function
def create_hotel_booking_node():
    """
    Create a LangGraph node for the hotel booking agent
    
    Returns:
        Callable: Node function for LangGraph
    """
    agent = HotelBookingAgent()
    return create_agent_node("hotel_booking_agent", agent.process_request)

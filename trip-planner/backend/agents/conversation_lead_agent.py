import os
import json
import logging
import re
from typing import Dict, Any, List, Optional

# Import LangGraph utilities
from agents.llm_utils import create_agent_node

# Configure logging
logger = logging.getLogger(__name__)

class ConversationLeadAgent:
    """Agent that handles the main conversation flow and determines user intent"""
    
    def __init__(self):
        """Initialize the Conversation Lead Agent"""
        logger.info("Conversation Lead Agent initialized")
        
    def process_request(self, session_id, message, language):
        """
        Process a user message and determine intent
        
        Args:
            session_id (str): Unique identifier for the conversation
            message (str): User's message
            language (str): Language of the conversation ("english" or "arabic")
            
        Returns:
            dict: Response containing text, intent, and success status
        """
        try:
            # Use simple pattern matching for intent detection
            intent = self._detect_intent(message, language)
            
            # Generate appropriate response based on intent
            response_text = self._generate_response(intent, message, language)
            
            # Add LangGraph-compatible state information
            return {
                "text": response_text,
                "intent": intent,
                "mock_data": {},  # No mock data at this stage
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error understanding your request.",
                "intent": "error",
                "mock_data": {},
                "success": False
            }
    
    def _get_system_prompt(self, language):
        """Get the appropriate system prompt based on language"""
        # This method is kept for compatibility with the LangGraph implementation
        if language.lower() == "arabic":
            return (
                "أنت مساعد سفر ودود ومفيد متخصص في تخطيط الرحلات في المملكة العربية السعودية. "
                "ساعد المستخدمين في حجز الرحلات الجوية والفنادق وتخطيط رحلاتهم. "
                "كن ودودًا ومفيدًا ومهنيًا. "
                "عندما يطلب المستخدمون معلومات محددة عن الرحلات أو الفنادق، اطلب التفاصيل اللازمة بأسلوب محادثة طبيعي."
            )
        else:
            return (
                "You are a friendly and helpful travel assistant specializing in trip planning in Saudi Arabia. "
                "Help users book flights, hotels, and plan their trips. "
                "Be friendly, helpful, and professional. "
                "When users ask for specific flight or hotel information, ask for the necessary details in a natural conversational way."
            )
    
    def _detect_intent(self, message, language):
        """
        Detect user intent based on message content using keyword matching
        
        Args:
            message (str): User's message
            language (str): Language of the conversation
            
        Returns:
            str: Detected intent
        """
        message_lower = message.lower()
        
        # Keywords for flight booking intent
        flight_keywords_en = ['flight', 'fly', 'plane', 'airport', 'airline']
        flight_keywords_ar = ['طيران', 'رحلة', 'مطار', 'طائرة']
        
        # Keywords for hotel booking intent
        hotel_keywords_en = ['hotel', 'stay', 'room', 'accommodation', 'lodge']
        hotel_keywords_ar = ['فندق', 'إقامة', 'غرفة', 'سكن']
        
        # Keywords for trip planning intent
        trip_keywords_en = ['trip', 'plan', 'vacation', 'holiday', 'itinerary', 'package']
        trip_keywords_ar = ['رحلة', 'خطة', 'إجازة', 'عطلة', 'حزمة', 'سفر']
        
        # Select keywords based on language
        flight_keywords = flight_keywords_ar if language.lower() == 'arabic' else flight_keywords_en
        hotel_keywords = hotel_keywords_ar if language.lower() == 'arabic' else hotel_keywords_en
        trip_keywords = trip_keywords_ar if language.lower() == 'arabic' else trip_keywords_en
        
        # Check for flight booking intent
        if any(keyword in message_lower for keyword in flight_keywords):
            return 'flight_booking'
        
        # Check for hotel booking intent
        elif any(keyword in message_lower for keyword in hotel_keywords):
            return 'hotel_booking'
        
        # Check for trip planning intent
        elif any(keyword in message_lower for keyword in trip_keywords):
            return 'trip_planning'
        
        # Default to general conversation
        else:
            return 'general_conversation'
    
    def _generate_response(self, intent, message, language):
        """
        Generate a response based on the detected intent
        
        Args:
            intent (str): Detected intent
            message (str): User's message
            language (str): Language of the conversation
            
        Returns:
            str: Response text
        """
        if language.lower() == 'arabic':
            # Arabic responses
            responses = {
                'flight_booking': 'سأساعدك في العثور على رحلات جوية مناسبة. هل يمكنك تقديم المزيد من التفاصيل حول وجهتك وتواريخ سفرك؟',
                'hotel_booking': 'سأساعدك في العثور على فندق مناسب. هل يمكنك تقديم المزيد من التفاصيل حول المدينة ومدة إقامتك؟',
                'trip_planning': 'سأساعدك في تخطيط رحلتك الكاملة. دعني أجمع بعض الخيارات الرائعة للرحلات الجوية والفنادق.',
                'general_conversation': 'مرحبًا! أنا مساعد تخطيط الرحلات الخاص بك. كيف يمكنني مساعدتك اليوم؟',
                'error': 'آسف، لم أفهم طلبك. هل يمكنك إعادة صياغته؟'
            }
        else:
            # English responses
            responses = {
                'flight_booking': 'I can help you find suitable flights. Could you provide more details about your destination and travel dates?',
                'hotel_booking': 'I can help you find a suitable hotel. Could you provide more details about the city and your stay duration?',
                'trip_planning': 'I can help you plan your complete trip. Let me gather some great options for flights and hotels.',
                'general_conversation': 'Hello! I am your trip planning assistant. How can I help you today?',
                'error': 'Sorry, I did not understand your request. Could you rephrase it?'
            }
            
        # Extract cities from message (simple implementation)
        cities_mentioned = self._extract_cities(message)
        
        # Personalize response if cities are detected
        if cities_mentioned and intent in ['flight_booking', 'hotel_booking', 'trip_planning']:
            if language.lower() == 'arabic':
                if intent == 'flight_booking':
                    return f'سأساعدك في العثور على رحلات جوية إلى {cities_mentioned[0]}. دعني أجمع بعض الخيارات لك.'
                elif intent == 'hotel_booking':
                    return f'سأساعدك في العثور على فندق في {cities_mentioned[0]}. دعني أجمع بعض الخيارات لك.'
                else:  # trip_planning
                    if len(cities_mentioned) >= 2:
                        return f'سأساعدك في تخطيط رحلتك من {cities_mentioned[0]} إلى {cities_mentioned[1]}. دعني أجمع بعض الخيارات الرائعة للرحلات الجوية والفنادق.'
                    else:
                        return f'سأساعدك في تخطيط رحلتك إلى {cities_mentioned[0]}. دعني أجمع بعض الخيارات الرائعة للرحلات الجوية والفنادق.'
            else:
                if intent == 'flight_booking':
                    return f'I will help you find flights to {cities_mentioned[0]}. Let me gather some options for you.'
                elif intent == 'hotel_booking':
                    return f'I will help you find a hotel in {cities_mentioned[0]}. Let me gather some options for you.'
                else:  # trip_planning
                    if len(cities_mentioned) >= 2:
                        return f'I will help you plan your trip from {cities_mentioned[0]} to {cities_mentioned[1]}. Let me gather some great options for flights and hotels.'
                    else:
                        return f'I will help you plan your trip to {cities_mentioned[0]}. Let me gather some great options for flights and hotels.'
                
        return responses[intent]
    
    def _extract_cities(self, message):
        """
        Extract city names from user message
        Simple implementation for demo purposes
        
        Args:
            message (str): User's message
            
        Returns:
            list: List of city names found in the message
        """
        # List of Saudi cities to look for
        saudi_cities = [
            'Riyadh', 'Jeddah', 'Mecca', 'Medina', 'Dammam', 'Tabuk', 'Abha',
            'الرياض', 'جدة', 'مكة', 'المدينة', 'الدمام', 'تبوك', 'أبها'
        ]
        
        found_cities = []
        for city in saudi_cities:
            if re.search(r'\b' + re.escape(city) + r'\b', message, re.IGNORECASE):
                found_cities.append(city)
                
        return found_cities
    
    def _flight_booking(self, query):
        """Tool for flight booking"""
        return "Flight booking tool called with query: " + query
    
    def _hotel_booking(self, query):
        """Tool for hotel booking"""
        return "Hotel booking tool called with query: " + query
    
    def _trip_planning(self, query):
        """Tool for complete trip planning"""
        return "Trip planning tool called with query: " + query


# Create LangGraph node function
def create_conversation_lead_node():
    """
    Create a LangGraph node for the conversation lead agent
    
    Returns:
        Callable: Node function for LangGraph
    """
    agent = ConversationLeadAgent()
    return create_agent_node("conversation_lead_agent", agent.process_request)

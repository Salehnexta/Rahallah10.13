"""
Agent System for Trip Planning Assistant
Orchestrates the different agents and manages the conversation flow
"""
import logging
import re
from .conversation_lead_agent import ConversationLeadAgent
from .flight_booking_agent import FlightBookingAgent
from .hotel_booking_agent import HotelBookingAgent
from .trip_planning_agent import TripPlanningAgent
from .llm_utils import generate_response

# Configure logging
logger = logging.getLogger(__name__)

class AgentSystem:
    """Agent System class for orchestrating the different agents"""
    
    def __init__(self):
        """Initialize the Agent System with all the specialized agents"""
        self.conversation_lead = ConversationLeadAgent()
        self.flight_booking = FlightBookingAgent()
        self.hotel_booking = HotelBookingAgent()
        self.trip_planning = TripPlanningAgent()
        
        # Session state
        self.sessions = {}
        
        logger.info("Agent System initialized with all specialized agents")
    
    def process_message(self, session_id, message, language="english"):
        """
        Process a user message and generate a response using the appropriate agent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language of the conversation (english or arabic)
            
        Returns:
            dict: Response with text and metadata
        """
        try:
            # Initialize session if it doesn't exist
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "conversation_history": [],
                    "flight_options": [],
                    "hotel_options": [],
                    "language": language,
                    "mock_data": {},
                    "user_preferences": {},
                    "current_context": None,  # Track the current conversation context
                    "last_intent": None  # Track the last detected intent
                }
            
            # Update session language if provided
            if language:
                self.sessions[session_id]["language"] = language
            else:
                language = self.sessions[session_id]["language"]
            
            # Add user message to conversation history
            self.sessions[session_id]["conversation_history"].append({
                "role": "user",
                "content": message
            })
            
            # Determine intent using Conversation Lead Agent
            lead_response = self.conversation_lead.process_message(session_id, message, language)
            raw_intent = lead_response["intent"]
            
            # Get previous intent for context awareness
            last_intent = self.sessions[session_id].get("last_intent")
            
            # Apply intent continuity logic for follow-up questions
            intent = self._resolve_intent_with_context(session_id, raw_intent, message, last_intent)
            
            logger.info(f"Session {session_id}: Raw intent: {raw_intent}, Resolved intent: {intent}")
            
            # Process based on intent
            if intent == "flight_booking":
                response = self._handle_flight_booking(session_id, message, language)
            elif intent == "hotel_booking":
                response = self._handle_hotel_booking(session_id, message, language)
            elif intent == "trip_planning":
                response = self._handle_trip_planning(session_id, message, language)
            else:
                # General conversation - just use conversation lead response
                response = {
                    "text": lead_response["text"],
                    "intent": "general",
                    "success": True,
                    "mock_data": {}
                }
            
            # Update last intent
            self.sessions[session_id]["last_intent"] = intent
            
            # Add assistant response to conversation history
            self.sessions[session_id]["conversation_history"].append({
                "role": "assistant",
                "content": response["text"]
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error in Agent System: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your request. Please try again.",
                "intent": "error",
                "success": False,
                "mock_data": {}
            }
    
    def _handle_flight_booking(self, session_id, message, language):
        """
        Handle flight booking intent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language of the conversation
            
        Returns:
            dict: Response with flight options
        """
        try:
            # Process request with flight booking agent
            response = self.flight_booking.process_request(
                session_id=session_id,
                message=message,
                language=language
            )
            
            # Store flight options in session
            if "mock_data" in response and "flight_options" in response["mock_data"]:
                self.sessions[session_id]["flight_options"] = response["mock_data"]["flight_options"]
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling flight booking: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your flight booking request.",
                "intent": "error",
                "success": False,
                "mock_data": {}
            }
    
    def _handle_hotel_booking(self, session_id, message, language):
        """
        Handle hotel booking intent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language of the conversation
            
        Returns:
            dict: Response with hotel options
        """
        try:
            # Process request with hotel booking agent
            response = self.hotel_booking.process_request(
                session_id=session_id,
                message=message,
                language=language
            )
            
            # Store hotel options in session
            if "mock_data" in response and "hotel_options" in response["mock_data"]:
                self.sessions[session_id]["hotel_options"] = response["mock_data"]["hotel_options"]
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling hotel booking: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your hotel booking request.",
                "intent": "error",
                "success": False,
                "mock_data": {}
            }
    
    def _handle_trip_planning(self, session_id, message, language):
        """
        Handle trip planning intent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language (english or arabic)
            
        Returns:
            dict: Response with trip plan
        """
        try:
            # Process request with trip planning agent
            response = self.trip_planning.process_request(
                session_id=session_id,
                message=message,
                language=language
            )
            
            # Ensure the response has the correct format
            return {
                "text": response.get("text", ""),
                "intent": "trip_planning",
                "success": response.get("success", True),
                "mock_data": response.get("mock_data", {})
            }
            
        except Exception as e:
            logger.error(f"Error handling trip planning: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your trip planning request.",
                "intent": "trip_planning",
                "success": False,
                "mock_data": {}
            }
            
    def _resolve_intent_with_context(self, session_id, raw_intent, message, last_intent):
        """
        Resolve the final intent by considering conversation context and continuity
        
        Args:
            session_id (str): Session identifier
            raw_intent (str): Raw intent detected from the message
            message (str): Current user message
            last_intent (str): Previous intent in the conversation
            
        Returns:
            str: Resolved intent considering context
        """
        # Extract conversation history for context
        history = self.sessions[session_id]["conversation_history"]
        
        # If message is explicitly about a new topic, use the new raw intent
        topic_change_indicators = [
            "now I need", "let's talk about", "I want to", "can you help me with", 
            "what about", "I'd like to", "switch to", "instead", "also"
        ]
        
        # Process specific intent transitions
        is_topic_change = any(indicator in message.lower() for indicator in topic_change_indicators)
        
        # Handle specific intent markers
        if "hotel" in message.lower() and (is_topic_change or not last_intent):
            logger.info(f"Session {session_id}: Detected hotel mention with topic change indicator")
            return "hotel_booking"
            
        elif "flight" in message.lower() and (is_topic_change or not last_intent):
            logger.info(f"Session {session_id}: Detected flight mention with topic change indicator")
            return "flight_booking"
            
        elif any(word in message.lower() for word in ["itinerary", "plan", "things to do"]) and (is_topic_change or not last_intent):
            logger.info(f"Session {session_id}: Detected trip planning mention with topic change indicator")
            return "trip_planning"
        
        # For follow-up questions, maintain context unless explicit intent is detected
        if raw_intent == "general_conversation" and last_intent and len(message.split()) < 10:
            logger.info(f"Session {session_id}: Short follow-up detected, maintaining {last_intent} context")
            return last_intent
            
        # If raw intent is a specific booking intent, prioritize it
        if raw_intent in ["flight_booking", "hotel_booking", "trip_planning"]:
            return raw_intent
            
        # If we get here, use the raw intent
        return raw_intent
    
    def reset_session(self, session_id):
        """
        Reset a session's conversation history
        
        Args:
            session_id (str): Session identifier
        """
        if session_id in self.sessions:
            self.sessions[session_id]["conversation_history"] = []
            self.sessions[session_id]["flight_options"] = []
            self.sessions[session_id]["hotel_options"] = []
            self.sessions[session_id]["mock_data"] = {}
            self.sessions[session_id]["user_preferences"] = {}

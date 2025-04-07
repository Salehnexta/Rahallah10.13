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
                    "user_preferences": {}
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
            lead_response = self.conversation_lead.process_message(message, language)
            intent = lead_response["intent"]
            
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
            language (str): Language of the conversation
            
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
            
            return response
            
        except Exception as e:
            logger.error(f"Error handling trip planning: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your trip planning request.",
                "intent": "error",
                "success": False,
                "mock_data": {}
            }
    
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

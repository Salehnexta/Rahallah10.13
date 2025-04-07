"""
Agent Orchestrator for Trip Planning Assistant
Manages the conversation flow and delegates to specialized agents
"""
import logging
import re
from .agent_system import AgentSystem
from .language_utils import detect_language, format_response_for_language

# Configure logging
logger = logging.getLogger(__name__)

class AgentOrchestrator:
    """
    Orchestrates the conversation flow between different specialized agents
    """
    
    def __init__(self):
        """Initialize the orchestrator"""
        self.agent_system = AgentSystem()
        self.user_preferences = {}
        logger.info("Agent Orchestrator initialized with Agent System")
    
    def process_message(self, user_message, session_id, conversation_history=None):
        """
        Process a user message and generate an appropriate response
        
        Args:
            user_message (str): The user's message
            session_id (str): Unique session identifier
            conversation_history (list): Previous messages in the conversation
            
        Returns:
            dict: Response with text and metadata
        """
        try:
            if not conversation_history:
                conversation_history = []
                
            # Detect language
            language = detect_language(user_message)
            logger.info(f"Processing message in {language} for session {session_id}")
            
            # Update user preferences based on conversation
            self._update_preferences(user_message, conversation_history)
            
            # Process message with agent system
            response = self.agent_system.process_message(
                session_id=session_id,
                message=user_message,
                language=language
            )
            
            # Format response for the detected language if needed
            if language.lower() == "arabic":
                response_text = format_response_for_language(response["text"], language)
            else:
                response_text = response["text"]
            
            # Add additional metadata
            response["language"] = language
            response["session_id"] = session_id
            response["text"] = response_text
            
            logger.info(f"Generated response for session {session_id} with intent {response['intent']}")
            return response
            
        except Exception as e:
            logger.error(f"Error in Agent Orchestrator: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your request. Please try again.",
                "language": language if 'language' in locals() else "english",
                "intent": "error",
                "session_id": session_id
            }
    
    def _update_preferences(self, user_message, conversation_history):
        """
        Update user preferences based on conversation
        
        Args:
            user_message (str): Current user message
            conversation_history (list): Previous messages
        """
        try:
            # Track language preference
            language = detect_language(user_message)
            self.user_preferences["language"] = language
            
            # Simple keyword-based preference tracking
            if "business class" in user_message.lower():
                self.user_preferences["flight_class"] = "business"
            elif "economy" in user_message.lower():
                self.user_preferences["flight_class"] = "economy"
            
            # Extract destination preferences
            destinations = self._extract_destinations(user_message)
            if destinations:
                self.user_preferences["destinations"] = destinations
                
            # Log updated preferences
            logger.info(f"Updated user preferences: {self.user_preferences}")
            
        except Exception as e:
            logger.error(f"Error updating preferences: {str(e)}")
    
    def _extract_destinations(self, message):
        """
        Extract destination mentions from a message
        
        Args:
            message (str): User message
            
        Returns:
            list: Extracted destinations
        """
        # List of Saudi cities to look for
        saudi_cities = [
            "Riyadh", "Jeddah", "Dammam", "Medina", "Mecca", "Al Khobar", 
            "Tabuk", "Abha", "Taif", "Yanbu", "Jubail", "Dhahran"
        ]
        
        found_destinations = []
        for city in saudi_cities:
            if re.search(r'\b' + city + r'\b', message, re.IGNORECASE):
                found_destinations.append(city)
                
        return found_destinations

"""
Conversation Lead Agent for Trip Planning Assistant
Handles main conversation flow and determines user intent
"""
import logging
from .langchain_utils import create_conversation_chain, run_chain_with_memory

# Configure logging
logger = logging.getLogger(__name__)

# System prompt for the Conversation Lead Agent
SYSTEM_PROMPT = """
You are the Conversation Lead Agent for a Saudi-focused Trip Planning Assistant.
Your role is to handle the main conversation flow with the user, determine their intent, 
and extract relevant information in a natural conversational manner.

Key responsibilities:
1. Identify if the user wants to book a flight, book a hotel, or plan a complete trip
2. Extract relevant information (dates, destinations, preferences) through natural conversation
3. Maintain a friendly, helpful tone that reflects Saudi hospitality
4. Support both English and Arabic conversations
5. For Arabic conversations, ensure proper formatting and cultural context

When responding:
- Be concise but friendly
- Ask clarifying questions when needed
- Acknowledge user preferences
- Provide helpful suggestions based on Saudi tourism highlights
- If the user's intent is unclear, guide them toward flight booking, hotel booking, or complete trip planning

Do not make up information about real flights, hotels, or travel packages.
Instead, indicate when you need to consult specialized agents for this information.
"""

class ConversationLeadAgent:
    """Conversation Lead Agent class"""
    
    def __init__(self):
        """Initialize the Conversation Lead Agent"""
        self.chain, self.memory = create_conversation_chain(SYSTEM_PROMPT)
        logger.info("Conversation Lead Agent initialized")
    
    def process_message(self, user_message, language="english"):
        """
        Process a user message and generate a response
        
        Args:
            user_message (str): User's message
            language (str): Language of the conversation (english or arabic)
            
        Returns:
            dict: Response with text and detected intent
        """
        try:
            # Add language context if needed
            if language.lower() == "arabic":
                context_message = f"The user is speaking in Arabic. Respond in Arabic. Original message: {user_message}"
            else:
                context_message = user_message
            
            # Process message through LangChain
            response_text = run_chain_with_memory(self.chain, self.memory, context_message)
            
            # Detect intent (simplified version - in a real system, this would be more sophisticated)
            intent = self._detect_intent(user_message)
            
            return {
                "text": response_text,
                "intent": intent
            }
        except Exception as e:
            logger.error(f"Error in Conversation Lead Agent: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your request.",
                "intent": "error"
            }
    
    def _detect_intent(self, message):
        """
        Detect the user's intent from their message
        
        Args:
            message (str): User's message
            
        Returns:
            str: Detected intent (flight_booking, hotel_booking, trip_planning, general)
        """
        message = message.lower()
        
        # Simple keyword-based intent detection
        if any(word in message for word in ["flight", "fly", "plane", "airport", "airline"]):
            return "flight_booking"
        elif any(word in message for word in ["hotel", "stay", "room", "accommodation", "lodge"]):
            return "hotel_booking"
        elif any(word in message for word in ["trip", "travel", "vacation", "holiday", "itinerary", "plan"]):
            return "trip_planning"
        else:
            return "general"

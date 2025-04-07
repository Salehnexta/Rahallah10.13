"""
Conversation Lead Agent for Trip Planning Assistant
Handles the main conversation flow and determines user intent
"""
import logging
from .llm_utils import generate_response
from .language_utils import detect_language

# Configure logging
logger = logging.getLogger(__name__)

# System prompt for the conversation lead agent
CONVERSATION_LEAD_PROMPT = """
You are a friendly travel assistant that helps users book flights, hotels, or plan trips.
You engage in casual, natural conversation like ChatGPT. Your job is to:

1. Make the conversation feel natural and friendly
2. Determine what the user needs (flight booking, hotel booking, or trip planning)
3. Extract only the essential information needed through casual conversation
4. When you have enough information, pass the request to a specialized agent
5. If the user speaks Arabic, respond in Arabic with the same natural, conversational style

Important: Keep responses short and conversational. Don't ask multiple questions at once.
Don't use forms or lengthy questions. Just have a natural chat until you understand what they need.

For Arabic users, be sure to maintain the same casual, helpful tone. Use common Saudi travel terms when appropriate.

Current conversation:
{history}
Human: {input}
AI:
"""

# System prompt for intent recognition
INTENT_RECOGNITION_PROMPT = """
Analyze the following conversation and determine if there's enough information to proceed with one of these actions:
1. Book a flight
2. Book a hotel
3. Plan a trip (combining flight and hotel)
4. None yet - need more information

Only respond with one of these exact values: "flight", "hotel", "trip", or "continue_conversation"

If it's a flight booking, there should be information about destination and approximate dates.
If it's a hotel booking, there should be information about location and approximate dates.
If it's trip planning, there should be information about destination and approximate duration.

If any essential information is missing, respond with "continue_conversation".

User's message: {user_input}
Previous conversation: {conversation_history}

Intent:
"""

def format_conversation_history(history):
    """
    Format conversation history for the prompt
    
    Args:
        history (list): List of message dictionaries
        
    Returns:
        str: Formatted conversation history
    """
    formatted = ""
    for msg in history:
        role = "Human" if msg["role"] == "user" else "AI"
        formatted += f"{role}: {msg['content']}\n"
    return formatted

def detect_intent(user_message, conversation_history):
    """
    Detect the user's intent from the conversation
    
    Args:
        user_message (str): Current user message
        conversation_history (list): Previous messages
        
    Returns:
        str: Detected intent ("flight", "hotel", "trip", or "continue_conversation")
    """
    # Format conversation history for the prompt
    history_text = ""
    if conversation_history:
        history_text = format_conversation_history(conversation_history)
    
    # Replace placeholders in the prompt
    prompt = INTENT_RECOGNITION_PROMPT.replace("{user_input}", user_message)
    prompt = prompt.replace("{conversation_history}", history_text)
    
    # Generate response with low temperature for more deterministic output
    response = generate_response(
        system_prompt=prompt,
        user_message="",  # Intent is determined from system prompt
        temperature=0.1
    )
    
    # Clean and validate the response
    response = response.strip().lower()
    valid_intents = ["flight", "hotel", "trip", "continue_conversation"]
    
    if response in valid_intents:
        logger.info(f"Detected intent: {response}")
        return response
    else:
        logger.warning(f"Invalid intent detected: {response}, defaulting to continue_conversation")
        return "continue_conversation"

def generate_lead_response(user_message, conversation_history=None):
    """
    Generate a response from the conversation lead agent
    
    Args:
        user_message (str): Current user message
        conversation_history (list): Previous messages
        
    Returns:
        dict: Response with text and detected language
    """
    # Detect language
    language = detect_language(user_message)
    
    # Format conversation history for the prompt
    history_text = ""
    if conversation_history:
        history_text = format_conversation_history(conversation_history)
    
    # Replace placeholders in the prompt
    prompt = CONVERSATION_LEAD_PROMPT.replace("{history}", history_text)
    prompt = prompt.replace("{input}", user_message)
    
    # Generate response
    response_text = generate_response(
        system_prompt=prompt,
        user_message="",  # Input is already in the system prompt
        temperature=0.7
    )
    
    return {
        "text": response_text,
        "language": language
    }

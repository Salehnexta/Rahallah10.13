"""
Flight Booking Agent for Trip Planning Assistant
Generates fictional flight booking options based on user requests
"""
import logging
from .llm_utils import generate_response
from .language_utils import detect_language

# Configure logging
logger = logging.getLogger(__name__)

# System prompt for the flight booking agent
FLIGHT_AGENT_PROMPT = """
You are a flight booking assistant. Generate completely fictional but realistic-sounding flight options.
DO NOT use real flight data - create mock flight information that seems plausible.
Include airlines, prices, times, and flight numbers. If the user speaks Arabic,
respond in Arabic. Format your response like a real booking assistant.

Include only one fictional flight option with:
- Airline (prefer Saudi airlines like Saudia, flynas, flyadeal)
- Departure and arrival times
- Flight duration
- Price in SAR (use realistic price ranges for the route)
- Flight number (fictional)
- A mock booking link (not a real URL)

Remember, all data should be completely made-up but realistic seeming.

Current conversation:
{history}
Human: {input}
AI:
"""

def generate_flight_response(user_message, conversation_history=None, extracted_info=None):
    """
    Generate a flight booking response
    
    Args:
        user_message (str): Current user message
        conversation_history (list): Previous messages
        extracted_info (dict): Optional extracted information about the flight request
        
    Returns:
        dict: Response with text and detected language
    """
    # Detect language
    language = detect_language(user_message)
    
    # Format conversation history
    history_text = ""
    if conversation_history:
        history_text = "\n".join([
            f"{'Human' if msg['role'] == 'user' else 'AI'}: {msg['content']}"
            for msg in conversation_history
        ])
    
    # Add extracted information to the prompt if available
    enhanced_prompt = FLIGHT_AGENT_PROMPT
    if extracted_info:
        # Add details to the prompt to guide the response
        details = []
        if 'origin' in extracted_info:
            details.append(f"Origin: {extracted_info['origin']}")
        if 'destination' in extracted_info:
            details.append(f"Destination: {extracted_info['destination']}")
        if 'date' in extracted_info:
            details.append(f"Date: {extracted_info['date']}")
        if 'passengers' in extracted_info:
            details.append(f"Passengers: {extracted_info['passengers']}")
        if 'class' in extracted_info:
            details.append(f"Class: {extracted_info['class']}")
            
        if details:
            enhanced_prompt += "\n\nInclude these details in your response:\n" + "\n".join(details)
    
    # Replace placeholders in the prompt
    prompt = enhanced_prompt.replace("{history}", history_text)
    prompt = prompt.replace("{input}", user_message)
    
    # Generate response
    response_text = generate_response(
        system_prompt=prompt,
        user_message="",  # Input is already in the system prompt
        temperature=0.7
    )
    
    logger.info(f"Generated flight response in {language}")
    
    return {
        "text": response_text,
        "language": language
    }

def extract_flight_info(conversation_history):
    """
    Extract flight booking information from conversation history
    
    Args:
        conversation_history (list): Previous messages
        
    Returns:
        dict: Extracted information (origin, destination, date, etc.)
    """
    # This would typically use an LLM to extract structured information
    # For now, we'll implement a simple placeholder
    
    # Combine all user messages
    all_user_text = " ".join([
        msg["content"] for msg in conversation_history 
        if msg["role"] == "user"
    ])
    
    # For demonstration, return a placeholder
    # In a real implementation, this would use NLP or an LLM to extract details
    extracted = {
        "intent": "flight",
        # Add other fields that would be extracted
    }
    
    logger.info(f"Extracted flight info: {extracted}")
    return extracted

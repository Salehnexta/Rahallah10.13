"""
Hotel Booking Agent for Trip Planning Assistant
Generates fictional hotel booking options based on user requests
"""
import logging
from .llm_utils import generate_response
from .language_utils import detect_language

# Configure logging
logger = logging.getLogger(__name__)

# System prompt for the hotel booking agent
HOTEL_AGENT_PROMPT = """
You are a hotel booking assistant. Generate completely fictional but realistic-sounding hotel options.
DO NOT use real hotel data - create mock hotel information that seems plausible for the location.
Include hotel names, prices, amenities, and locations. If the user speaks Arabic,
respond in Arabic. Format your response like a real booking assistant.

Include only one fictional hotel option with:
- Hotel name (realistic for the location but invented)
- Star rating (3-5 stars)
- Location description (plausible but fictional)
- 2-3 key amenities
- Price per night in SAR (use realistic price ranges for the location)
- A mock booking link (not a real URL)

Remember, all data should be completely made-up but realistic seeming.

Current conversation:
{history}
Human: {input}
AI:
"""

def generate_hotel_response(user_message, conversation_history=None, extracted_info=None):
    """
    Generate a hotel booking response
    
    Args:
        user_message (str): Current user message
        conversation_history (list): Previous messages
        extracted_info (dict): Optional extracted information about the hotel request
        
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
    enhanced_prompt = HOTEL_AGENT_PROMPT
    if extracted_info:
        # Add details to the prompt to guide the response
        details = []
        if 'location' in extracted_info:
            details.append(f"Location: {extracted_info['location']}")
        if 'check_in' in extracted_info:
            details.append(f"Check-in date: {extracted_info['check_in']}")
        if 'check_out' in extracted_info:
            details.append(f"Check-out date: {extracted_info['check_out']}")
        if 'guests' in extracted_info:
            details.append(f"Number of guests: {extracted_info['guests']}")
        if 'preferences' in extracted_info:
            details.append(f"Preferences: {extracted_info['preferences']}")
            
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
    
    logger.info(f"Generated hotel response in {language}")
    
    return {
        "text": response_text,
        "language": language
    }

def extract_hotel_info(conversation_history):
    """
    Extract hotel booking information from conversation history
    
    Args:
        conversation_history (list): Previous messages
        
    Returns:
        dict: Extracted information (location, dates, guests, etc.)
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
        "intent": "hotel",
        # Add other fields that would be extracted
    }
    
    logger.info(f"Extracted hotel info: {extracted}")
    return extracted

"""
Trip Planning Agent for Trip Planning Assistant
Generates fictional complete travel packages combining flights and hotels
"""
import logging
from .llm_utils import generate_response
from .language_utils import detect_language

# Configure logging
logger = logging.getLogger(__name__)

# System prompt for the trip planning agent
TRIP_AGENT_PROMPT = """
You are a trip planning assistant. Generate completely fictional but realistic-sounding travel packages.
DO NOT use real travel data - create mock flight and hotel information that seems plausible.
If the user speaks Arabic, respond in Arabic. Format your response like a real travel agent.

Include:
- One fictional flight option with airline, times, and price
- One fictional hotel option with name, rating, and price
- Total package price in SAR
- Brief 1-2 sentence suggestion about the destination
- Mock booking links for both flight and hotel (not real URLs)

Remember, all data should be completely made-up but realistic seeming.

Current conversation:
{history}
Human: {input}
AI:
"""

def generate_trip_response(user_message, conversation_history=None, extracted_info=None):
    """
    Generate a complete trip planning response
    
    Args:
        user_message (str): Current user message
        conversation_history (list): Previous messages
        extracted_info (dict): Optional extracted information about the trip request
        
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
    enhanced_prompt = TRIP_AGENT_PROMPT
    if extracted_info:
        # Add details to the prompt to guide the response
        details = []
        if 'origin' in extracted_info:
            details.append(f"Origin: {extracted_info['origin']}")
        if 'destination' in extracted_info:
            details.append(f"Destination: {extracted_info['destination']}")
        if 'start_date' in extracted_info:
            details.append(f"Start date: {extracted_info['start_date']}")
        if 'end_date' in extracted_info:
            details.append(f"End date: {extracted_info['end_date']}")
        if 'travelers' in extracted_info:
            details.append(f"Number of travelers: {extracted_info['travelers']}")
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
    
    logger.info(f"Generated trip planning response in {language}")
    
    return {
        "text": response_text,
        "language": language
    }

def extract_trip_info(conversation_history):
    """
    Extract trip planning information from conversation history
    
    Args:
        conversation_history (list): Previous messages
        
    Returns:
        dict: Extracted information (origin, destination, dates, travelers, etc.)
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
        "intent": "trip",
        # Add other fields that would be extracted
    }
    
    logger.info(f"Extracted trip info: {extracted}")
    return extracted

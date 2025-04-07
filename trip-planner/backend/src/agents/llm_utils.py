"""
LLM Utilities for Trip Planning Assistant
Handles connection to DeepSeek LLM via OpenAI compatibility layer
"""
import os
from dotenv import load_dotenv
import logging
import json
from openai import OpenAI

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    logger.error("DEEPSEEK_API_KEY not found in environment variables")
    raise ValueError("DEEPSEEK_API_KEY not set in .env file")

# DeepSeek API base URL - note the correct base URL without v1
DEEPSEEK_API_BASE = "https://api.deepseek.com"

def get_openai_client():
    """
    Initialize and return an OpenAI client configured for DeepSeek
    
    Returns:
        OpenAI: Configured OpenAI client for DeepSeek
    """
    try:
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_BASE
        )
        return client
    except Exception as e:
        logger.error(f"Error initializing OpenAI client: {str(e)}")
        raise

def generate_response(system_prompt, user_message, conversation_history=None, temperature=0.7, model="deepseek-chat"):
    """
    Generate a response using the DeepSeek LLM with mock data generation
    
    Args:
        system_prompt (str): Instructions for the AI
        user_message (str): Current user message
        conversation_history (list): Previous messages in the format 
                                    [{"role": "user/assistant", "content": "message"}]
        temperature (float): Controls randomness in responses
        model (str): Model identifier for DeepSeek
        
    Returns:
        dict: Generated response with mock data
    """
    try:
        client = get_openai_client()
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
        
        # Add current user message
        if user_message:
            messages.append({"role": "user", "content": user_message})
        
        # Generate response
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            stream=False
        )
        
        # Parse the response
        content = response.choices[0].message.content
        
        # Try to parse JSON if it's in the response
        try:
            # Extract JSON if it's in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                mock_data = json.loads(content[json_start:json_end])
                return {
                    "text": content,
                    "mock_data": mock_data,
                    "success": True
                }
        except json.JSONDecodeError:
            pass
            
        return {
            "text": content,
            "mock_data": {},
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return {
            "text": f"I'm sorry, I encountered an error: {str(e)}",
            "mock_data": {},
            "success": False,
            "error": str(e)
        }

def generate_flight_options(origin, destination, departure_date, return_date=None, num_options=3):
    """
    Generate mock flight options using DeepSeek
    
    Args:
        origin (str): Departure city
        destination (str): Arrival city
        departure_date (str): Departure date (YYYY-MM-DD)
        return_date (str, optional): Return date (YYYY-MM-DD)
        num_options (int): Number of flight options to generate
        
    Returns:
        dict: Mock flight options with detailed information
    """
    system_prompt = f"""You are a flight booking assistant for Saudi Arabia. Generate {num_options} realistic flight options between {origin} and {destination}.
    For each flight, include:
    - Airline name (Saudi airlines only)
    - Flight number
    - Departure time
    - Arrival time
    - Duration
    - Price in SAR
    - Booking link (mock)
    - Seat options (economy, business)
    
    Return the data in JSON format with the following structure:
    {{
        "flights": [
            {{
                "airline": "string",
                "flight_number": "string",
                "departure_time": "HH:MM",
                "arrival_time": "HH:MM",
                "duration": "HH:MM",
                "price": "number",
                "booking_link": "string",
                "seat_options": {{"economy": "number", "business": "number"}}
            }}
        ]
    }}
    """
    
    response = generate_response(
        system_prompt=system_prompt,
        user_message=f"Generate flight options from {origin} to {destination} on {departure_date}",
        temperature=0.5  # Lower temperature for more consistent results
    )
    
    return response

def generate_hotel_options(destination, check_in, check_out, num_options=3):
    """
    Generate mock hotel options using DeepSeek
    
    Args:
        destination (str): City name
        check_in (str): Check-in date (YYYY-MM-DD)
        check_out (str): Check-out date (YYYY-MM-DD)
        num_options (int): Number of hotel options to generate
        
    Returns:
        dict: Mock hotel options with detailed information
    """
    system_prompt = f"""You are a hotel booking assistant for Saudi Arabia. Generate {num_options} realistic hotel options in {destination}.
    For each hotel, include:
    - Hotel name
    - Star rating (3-5 stars)
    - Location description
    - Price per night in SAR
    - Amenities (Wi-Fi, pool, etc.)
    - Booking link (mock)
    - Room types available
    
    Return the data in JSON format with the following structure:
    {{
        "hotels": [
            {{
                "name": "string",
                "stars": "number",
                "location": "string",
                "price_per_night": "number",
                "amenities": ["string"],
                "booking_link": "string",
                "room_types": {{"standard": "number", "deluxe": "number", "suite": "number"}}
            }}
        ]
    }}
    """
    
    response = generate_response(
        system_prompt=system_prompt,
        user_message=f"Generate hotel options in {destination} for {check_in} to {check_out}",
        temperature=0.5  # Lower temperature for more consistent results
    )
    
    return response

def test_llm_connection():
    """
    Test the connection to the DeepSeek LLM
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        response = generate_response(
            system_prompt="You are a helpful assistant.",
            user_message="Hello, are you working correctly?"
        )
        logger.info(f"LLM test response: {response}")
        return True, response
    except Exception as e:
        logger.error(f"LLM connection test failed: {str(e)}")
        return False, str(e)

"""
LLM Utilities for Trip Planning Assistant
Handles connection to DeepSeek LLM via OpenAI compatibility layer
Uses LangGraph for agent orchestration
"""
import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional, Callable
import langgraph.graph as lg
from langgraph.graph import END, StateGraph, START
from typing_extensions import TypedDict, NotRequired

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

def init_openai_client():
    """
    Initialize and return an OpenAI client configured for DeepSeek
    
    Returns:
        OpenAI: Configured OpenAI client for DeepSeek
    """
    try:
        # Configure OpenAI client with DeepSeek settings
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
    Generate a response using the DeepSeek LLM with LangChain
    
    Args:
        system_prompt (str): Instructions for the AI
        user_message (str): Current user message
        conversation_history (list): Previous messages in the format 
                                 [{"role": "user/assistant", "content": "message"}]
        temperature (float): Controls randomness in responses
        
    Returns:
        dict: Response containing text and other attributes
    """
    try:
        # Initialize OpenAI client
        client = init_openai_client()
        
        # Build messages including conversation history if provided
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            for message in conversation_history:
                role = message.get("role", "")
                content = message.get("content", "")
                
                if role in ["user", "assistant", "system"]:
                    messages.append({"role": role, "content": content})
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Generate response using OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        
        response_text = response.choices[0].message.content
        
        # Try to parse JSON if present
        try:
            # Extract JSON if included in response
            if '{' in response_text and '}' in response_text:
                json_start = response_text.find('{')
                json_end = response_text.rfind('}') + 1
                json_str = response_text[json_start:json_end]
                parsed_json = json.loads(json_str)
                
                # Return parsed response
                return {
                    "text": parsed_json.get("response", response_text),
                    "intent": parsed_json.get("intent", "general"),
                    "mock_data": parsed_json.get("mock_data", {}),
                    "success": True
                }
        except json.JSONDecodeError:
            # If not valid JSON, return as plain text
            pass
            
        # Return plain text response
        return {
            "text": response_text,
            "intent": "general",
            "mock_data": {},
            "success": True
        }
        
    except Exception as e:
        logger.error(f"Error generating response: {str(e)}")
        return {
            "text": "I'm sorry, I encountered an error processing your request.",
            "intent": "error",
            "mock_data": {},
            "success": False
        }

def generate_flight_options(origin, destination, departure_date, return_date=None, num_options=5):
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
    try:
        # Set default values for missing parameters
        origin = origin or "Riyadh"
        destination = destination or "Jeddah"
        departure_date = departure_date or "2025-05-01"  # Default to next month
        
        # Create a system prompt to generate realistic flight data
        system_prompt = f"""You are a flight booking API for Saudi Arabia. Generate {num_options} realistic flight options between {origin} and {destination} for {departure_date}.
        
        Return ONLY a valid JSON object with the following structure:
        {{"flights": [
            {{"airline": "Saudia", "flight_number": "SV1234", "origin": "{origin}", "destination": "{destination}", 
             "departure_date": "{departure_date}", "departure_time": "08:30", "arrival_time": "10:15", 
             "duration": "1h 45m", "price": 750, "currency": "SAR", "class": "Economy", 
             "amenities": ["Wi-Fi", "In-flight entertainment"], "available_seats": 45}}]
        }}
        
        Make sure each flight has a different airline from ["Saudia", "flynas", "flyadeal", "Nesma Airlines", "SaudiGulf Airlines"],
        realistic flight numbers, departure/arrival times, durations, and prices between 500-2000 SAR.
        """
        
        # Generate response from DeepSeek
        user_message = f"Generate flight options from {origin} to {destination} on {departure_date}" + \
                     (f" with return on {return_date}" if return_date else "")
        
        # Call the DeepSeek API to generate flight data
        client = init_openai_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5
        )
        
        response_text = response.choices[0].message.content
        
        # Extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            flight_data = json.loads(json_str)
            
            # Create empty return flights list by default
            return_flights = []
            
            # If it's a round trip, generate return flights
            if return_date:
                # Create return flight system prompt
                return_system_prompt = f"""You are a flight booking API for Saudi Arabia. Generate {num_options} realistic return flight options 
                from {destination} back to {origin} for {return_date}.
                
                Return ONLY a valid JSON object with the following structure:
                {{"return_flights": [
                    {{"airline": "Saudia", "flight_number": "SV1234", "origin": "{destination}", "destination": "{origin}", 
                     "departure_date": "{return_date}", "departure_time": "19:30", "arrival_time": "21:15", 
                     "duration": "1h 45m", "price": 750, "currency": "SAR", "class": "Economy", 
                     "amenities": ["Wi-Fi", "In-flight entertainment"], "available_seats": 45}}]
                }}
                
                Make sure each flight has a different airline from ["Saudia", "flynas", "flyadeal", "Nesma Airlines", "SaudiGulf Airlines"],
                realistic flight numbers, departure/arrival times, durations, and prices between 500-2000 SAR.
                """
                
                # Generate return flights
                return_response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[
                        {"role": "system", "content": return_system_prompt},
                        {"role": "user", "content": f"Generate return flight options from {destination} to {origin} on {return_date}"}
                    ],
                    temperature=0.5
                )
                
                return_text = return_response.choices[0].message.content
                
                # Extract JSON from return response
                json_start = return_text.find('{')
                json_end = return_text.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = return_text[json_start:json_end]
                    return_data = json.loads(json_str)
                    return_flights = return_data.get("return_flights", [])
            
            # Combine and return all flight data
            return {
                "flights": flight_data.get("flights", []),
                "return_flights": return_flights,
                "is_round_trip": bool(return_date)
            }
        
        # Fallback to empty response if JSON parsing fails
        return {"flights": [], "return_flights": [], "is_round_trip": bool(return_date)}
        
    except Exception as e:
        logger.error(f"Error generating flight options: {str(e)}")
        return {"flights": [], "return_flights": [], "is_round_trip": False}

def generate_hotel_options(destination, check_in, check_out=None, num_options=5):
    """
    Generate mock hotel options using DeepSeek
    
    Args:
        destination (str): City name
        check_in (str): Check-in date (YYYY-MM-DD)
        check_out (str, optional): Check-out date (YYYY-MM-DD)
        num_options (int): Number of hotel options to generate
        
    Returns:
        dict: Mock hotel options with detailed information
    """
    try:
        # Set default values for missing parameters
        destination = destination or "Riyadh"
        check_in = check_in or "2025-05-01"  # Default to next month
        check_out = check_out or "2025-05-05"  # Default to 4-day stay
        
        # Create a system prompt to generate realistic hotel data
        system_prompt = f"""You are a hotel booking API for Saudi Arabia. Generate {num_options} realistic hotel options in {destination} for a stay from {check_in} to {check_out}.
        
        Return ONLY a valid JSON object with the following structure:
        {{"hotels": [
            {{"name": "Four Seasons Hotel Riyadh", "stars": 5, "location": "{destination} city center", 
             "price_per_night": 1500, "total_price": 6000, "currency": "SAR", 
             "amenities": ["Wi-Fi", "pool", "gym", "spa", "restaurant"], 
             "distance_from_center": "1.5 km", "rating": 4.8, "reviews": 450,
             "room_types": {{"standard": 15, "deluxe": 8, "suite": 3}}}}
        ]}}
        
        Make sure each hotel has a realistic Saudi hotel name (include some international chains like Hilton, Marriott, and local Saudi hotel chains),
        accurate star ratings (3-5 stars), realistic prices for the star level (3-star: 300-700 SAR, 4-star: 600-1200 SAR, 5-star: 1000-3000 SAR per night),
        and calculate the total_price based on the number of nights between {check_in} and {check_out}.
        """
        
        # Generate response from DeepSeek
        user_message = f"Generate hotel options in {destination} from {check_in} to {check_out}"
        
        # Call the DeepSeek API to generate hotel data
        client = init_openai_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.5
        )
        
        response_text = response.choices[0].message.content
        
        # Extract JSON from response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start >= 0 and json_end > json_start:
            json_str = response_text[json_start:json_end]
            hotel_data = json.loads(json_str)
            return hotel_data
        
        # Fallback to empty response if JSON parsing fails
        return {"hotels": []}
        
    except Exception as e:
        logger.error(f"Error generating hotel options: {str(e)}")
        return {"hotels": []}

def test_llm_connection():
    """
    Test the connection to the DeepSeek LLM
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Initialize client
        client = init_openai_client()
        
        # Test with a simple request - use the updated SDK format
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello"}
            ]
        )
        
        # Check for a successful response
        if response and response.choices and len(response.choices) > 0:
            logger.info("LLM connection test successful")
            return True
        else:
            logger.error("LLM connection test failed: No valid response received")
            return False
            
    except Exception as e:
        logger.error(f"LLM connection test failed: {str(e)}")
        return False


def create_agent_node(name: str, process_func: Callable):
    """
    Create a LangGraph agent node
    
    Args:
        name (str): Name of the agent node
        process_func (Callable): Function to process agent requests
        
    Returns:
        Callable: Node function for LangGraph
    """
    def node_func(state: Dict):
        # Extract data from state
        session_id = state.get("session_id", "default")
        message = state.get("message", "")
        language = state.get("language", "english")
        
        # Process the request
        result = process_func(session_id, message, language)
        
        # Update state with result
        state["current_agent"] = name
        state["response"] = result.get("text", "")
        state["intent"] = result.get("intent", "general")
        state["mock_data"] = result.get("mock_data", {})
        
        return state
    
    return node_func


def route_by_intent(state: Dict) -> str:
    """
    Route to the next agent based on intent
    
    Args:
        state (Dict): Current state
        
    Returns:
        str: Next agent to route to
    """
    intent = state.get("intent", "general")
    
    if intent == "flight_booking":
        return "flight_booking_agent"
    elif intent == "hotel_booking":
        return "hotel_booking_agent"
    elif intent == "trip_planning":
        return "trip_planning_agent"
    else:
        return END


# Define state schema for LangGraph
class AgentState(TypedDict):
    session_id: str
    message: str
    language: str
    current_agent: NotRequired[str]
    response: NotRequired[str]
    intent: NotRequired[str]
    mock_data: NotRequired[Dict]


def create_agent_workflow(agents: Dict[str, Callable]):
    """
    Create a LangGraph workflow with the provided agents
    
    Args:
        agents (Dict[str, Callable]): Dictionary of agent functions
        
    Returns:
        StateGraph: LangGraph workflow
    """
    # Create the graph
    workflow = StateGraph(AgentState)
    
    # Add nodes for each agent
    workflow.add_node("conversation_lead_agent", agents["conversation_lead_agent"])
    workflow.add_node("flight_booking_agent", agents["flight_booking_agent"])
    workflow.add_node("hotel_booking_agent", agents["hotel_booking_agent"])
    workflow.add_node("trip_planning_agent", agents["trip_planning_agent"])
    
    # Simple edge structure instead of conditional routing
    # Start with conversation agent
    workflow.add_edge(START, "conversation_lead_agent")
    
    # Connect each agent to END
    workflow.add_edge("conversation_lead_agent", END)
    workflow.add_edge("flight_booking_agent", END)
    workflow.add_edge("hotel_booking_agent", END)
    workflow.add_edge("trip_planning_agent", END)
    
    # Set entry point
    workflow.set_entry_point("conversation_lead_agent")
    
    # Compile the workflow
    return workflow.compile()

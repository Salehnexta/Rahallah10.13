"""
LLM Utilities for Trip Planning Assistant
Handles connection to DeepSeek LLM via OpenAI compatibility layer
Uses LangGraph for agent orchestration
"""
import os
import json
import logging
import openai
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
        # Configure OpenAI settings
        openai.api_key = os.getenv("DEEPSEEK_API_KEY")
        openai.api_base = "https://api.deepseek.com"
        return openai
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
        response = client.ChatCompletion.create(
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
    try:
        # Generate Saudi airline names
        saudi_airlines = ["Saudia", "flynas", "flyadeal", "Nesma Airlines", "SaudiGulf Airlines"]
        
        # Generate mock flights
        flights = []
        for i in range(num_options):
            # Create a flight option with randomized details
            flight = {
                "airline": saudi_airlines[i % len(saudi_airlines)],
                "flight_number": f"SV{1000 + i*111}",
                "origin": origin,
                "destination": destination,
                "departure_date": departure_date,
                "departure_time": f"{(6 + i*2) % 24:02d}:00",
                "arrival_time": f"{(9 + i*2) % 24:02d}:30",
                "duration": f"{3 + i}h 30m",
                "price": 800 + i * 200,
                "currency": "SAR",
                "class": "Economy",
                "available_seats": 10 + i*5,
                "booking_link": f"https://example.com/flights/{1000 + i}"
            }
            
            flights.append(flight)
        
        # If it's a round trip, add return flights
        return_flights = []
        if return_date:
            for i in range(num_options):
                # Create a return flight option
                return_flight = {
                    "airline": saudi_airlines[(i+2) % len(saudi_airlines)],
                    "flight_number": f"SV{2000 + i*111}",
                    "origin": destination,
                    "destination": origin,
                    "departure_date": return_date,
                    "departure_time": f"{(16 + i*2) % 24:02d}:00",
                    "arrival_time": f"{(19 + i*2) % 24:02d}:30",
                    "duration": f"{3 + i}h 30m",
                    "price": 850 + i * 200,
                    "currency": "SAR",
                    "class": "Economy",
                    "available_seats": 15 + i*5,
                    "booking_link": f"https://example.com/flights/{2000 + i}"
                }
                
                return_flights.append(return_flight)
        
        # Return mock data
        return {
            "flights": flights,
            "return_flights": return_flights if return_date else [],
            "is_round_trip": bool(return_date)
        }
        
    except Exception as e:
        logger.error(f"Error generating flight options: {str(e)}")
        return {"flights": [], "return_flights": [], "is_round_trip": False}

def generate_hotel_options(destination, check_in, check_out, num_options=3):
    """
    Generate mock hotel options
    
    Args:
        destination (str): City name
        check_in (str): Check-in date (YYYY-MM-DD)
        check_out (str): Check-out date (YYYY-MM-DD)
        num_options (int): Number of hotel options to generate
        
    Returns:
        dict: Mock hotel options with detailed information
    """
    try:
        # Generate hotel names
        hotel_names = ["Hotel 1", "Hotel 2", "Hotel 3", "Hotel 4", "Hotel 5"]
        
        # Generate mock hotels
        hotels = []
        for i in range(num_options):
            # Create a hotel option with randomized details
            hotel = {
                "name": hotel_names[i % len(hotel_names)],
                "stars": 3 + i % 2,
                "location": f"{destination} city center",
                "price_per_night": 500 + i * 100,
                "currency": "SAR",
                "amenities": ["Wi-Fi", "pool", "gym"],
                "booking_link": f"https://example.com/hotels/{1000 + i}",
                "room_types": {
                    "standard": 10 + i*5,
                    "deluxe": 5 + i*2,
                    "suite": 2 + i
                }
            }
            
            hotels.append(hotel)
        
        # Return mock data
        return {
            "hotels": hotels
        }
        
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
        
        # Test with a simple request
        response = client.ChatCompletion.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": "Say hello"}],
            temperature=0.7
        )
        
        if response and response.choices:
            logger.info("Successfully connected to DeepSeek API")
            return True
        return False
    except Exception as e:
        logger.error(f"Error connecting to DeepSeek: {str(e)}")
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

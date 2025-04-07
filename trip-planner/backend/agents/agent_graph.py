"""
LangGraph Implementation for Trip Planning Assistant
Defines the agent graph structure for coordinating multiple specialized agents
"""
import logging
from typing import Dict, Any, Callable
from langgraph.graph import StateGraph
from typing_extensions import TypedDict, NotRequired

# Define constants for LangGraph 0.0.19 compatibility
START = "__start__"
END = "__end__"

# Configure logging
logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """
    State schema for the LangGraph workflow
    
    Attributes:
        session_id: Unique session identifier
        message: User message
        language: Language of the conversation
        current_agent: Currently active agent
        response: Response text
        intent: Detected intent
        mock_data: Generated mock data
    """
    session_id: str
    message: str
    language: str
    current_agent: NotRequired[str]
    response: NotRequired[str]
    intent: NotRequired[str]
    mock_data: NotRequired[Dict]

def create_agent_workflow(agents: Dict[str, Callable]) -> StateGraph:
    """
    Create a LangGraph workflow with the provided agents
    
    Args:
        agents (Dict[str, Callable]): Dictionary of agent functions
        
    Returns:
        StateGraph: LangGraph workflow
    """
    try:
        logger.info("Creating agent workflow...")
        
        # Create the graph
        workflow = StateGraph(AgentState)
        
        # Add agent nodes
        workflow.add_node("conversation_lead_agent", agents.get("conversation_lead_agent"))
        workflow.add_node("flight_booking_agent", agents.get("flight_booking_agent"))
        workflow.add_node("hotel_booking_agent", agents.get("hotel_booking_agent"))
        workflow.add_node("trip_planning_agent", agents.get("trip_planning_agent"))
        
        # Add edges from START to the conversation lead agent
        workflow.add_edge(START, "conversation_lead_agent")
        
        # Add conditional routing based on intent
        workflow.add_conditional_edges(
            "conversation_lead_agent",
            route_by_intent,
            {
                "flight_booking": "flight_booking_agent",
                "hotel_booking": "hotel_booking_agent",
                "trip_planning": "trip_planning_agent",
                "general": END
            }
        )
        
        # Connect specialized agents to END
        workflow.add_edge("flight_booking_agent", END)
        workflow.add_edge("hotel_booking_agent", END)
        workflow.add_edge("trip_planning_agent", END)
        
        # Set entry point
        workflow.set_entry_point("conversation_lead_agent")
        
        # Compile the workflow
        logger.info("Agent workflow created successfully")
        return workflow.compile()
        
    except Exception as e:
        logger.error(f"Error creating agent workflow: {str(e)}")
        raise

def route_by_intent(state: Dict[str, Any]) -> str:
    """
    Route to the next agent based on intent
    
    Args:
        state (Dict): Current state
        
    Returns:
        str: Next agent to route to
    """
    try:
        # Get the intent
        intent = state.get("intent", "general")
        logger.info(f"Routing by intent: {intent}")
        
        # Route based on intent
        if intent == "flight_booking":
            return "flight_booking"
        elif intent == "hotel_booking":
            return "hotel_booking"
        elif intent == "trip_planning":
            return "trip_planning"
        else:
            return "general"
            
    except Exception as e:
        logger.error(f"Error routing by intent: {str(e)}")
        return "general" # Default to general if error occurs

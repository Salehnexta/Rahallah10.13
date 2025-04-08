from langgraph.graph import StateGraph
from typing import Dict, Any
from .agent_orchestrator import AgentOrchestrator
from .llm_utils import get_llm

def create_trip_workflow():
    # Create our agent orchestrator
    orchestrator = AgentOrchestrator()
    
    # Define the state with type annotations
    class GraphState:
        user_message: str
        session_id: str
        conversation_history: list = []
        current_intent: str = ""
        current_step: str = ""
        trip_details: dict = {}
        requires_flight: bool = False
        requires_hotel: bool = False
        requires_details: bool = False
        
    # Define the graph
    workflow = StateGraph(GraphState)
    
    # Define nodes
    def process_message(state):
        """Process user message and determine intent"""
        response = orchestrator.process_message(
            user_message=state.user_message,
            session_id=state.session_id,
            conversation_history=state.conversation_history
        )
        
        # Update state based on response
        state.conversation_history.append({
            "role": "user",
            "content": state.user_message
        })
        state.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        # Analyze response to determine next steps
        if "flight" in response.lower():
            state.requires_flight = True
        if "hotel" in response.lower():
            state.requires_hotel = True
        if "details" in response.lower():
            state.requires_details = True
            
        return state
    
    def get_flight_details(state):
        """Get flight details using flight agent"""
        from .flight_booking_agent import FlightBookingAgent
        flight_agent = FlightBookingAgent()
        
        # Get flight details based on conversation history
        flight_details = flight_agent.get_flight_details(
            state.conversation_history,
            state.trip_details
        )
        
        state.trip_details.update(flight_details)
        return state
    
    def get_hotel_details(state):
        """Get hotel details using hotel agent"""
        from .hotel_booking_agent import HotelBookingAgent
        hotel_agent = HotelBookingAgent()
        
        # Get hotel details based on conversation history
        hotel_details = hotel_agent.get_hotel_details(
            state.conversation_history,
            state.trip_details
        )
        
        state.trip_details.update(hotel_details)
        return state
    
    def generate_final_response(state):
        """Generate final response with all trip details"""
        llm = get_llm()
        
        # Generate summary response
        response = llm.invoke({
            "template": """
            Based on the conversation history and trip details, generate a concise summary of the trip plan.
            Conversation: {conversation}
            Trip Details: {details}
            
            Summary:
            """,
            "variables": {
                "conversation": state.conversation_history,
                "details": state.trip_details
            }
        })
        
        # Update conversation history
        state.conversation_history.append({
            "role": "assistant",
            "content": response
        })
        
        return state
    
    # Add nodes to the graph
    workflow.add_node("process_message", process_message)
    workflow.add_node("get_flight_details", get_flight_details)
    workflow.add_node("get_hotel_details", get_hotel_details)
    workflow.add_node("generate_final_response", generate_final_response)
    
    # Set entry point
    workflow.set_entry_point("process_message")
    
    # Add conditional edges
    workflow.add_conditional_edges(
        "process_message",
        lambda state: "get_flight_details" if state.requires_flight else
                     "get_hotel_details" if state.requires_hotel else
                     "generate_final_response"
    )
    
    workflow.add_conditional_edges(
        "get_flight_details",
        lambda state: "get_hotel_details" if state.requires_hotel else
                     "generate_final_response"
    )
    
    # Add the missing edge from get_hotel_details to generate_final_response
    workflow.add_edge("get_hotel_details", "generate_final_response")
    
    # Set finish point
    workflow.set_finish_point("generate_final_response")
    
    return workflow.compile()

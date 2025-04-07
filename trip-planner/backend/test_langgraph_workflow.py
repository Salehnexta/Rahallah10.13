"""
LangGraph Workflow Test for Trip Planning Assistant
This script tests the complete LangGraph workflow with all agents
"""
import logging
import json
import uuid
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import agent nodes
from agents.conversation_lead_agent import create_conversation_lead_node
from agents.flight_booking_agent import create_flight_booking_node
from agents.hotel_booking_agent import create_hotel_booking_node
from agents.trip_planning_agent import create_trip_planning_node
from agents.llm_utils import create_agent_workflow

def test_workflow():
    """Test the LangGraph workflow with all agents"""
    logger.info("Creating LangGraph workflow with all agents")
    
    # Create agent nodes
    try:
        logger.info("Creating agent nodes...")
        conversation_lead = create_conversation_lead_node()
        flight_booking = create_flight_booking_node()
        hotel_booking = create_hotel_booking_node()
        trip_planning = create_trip_planning_node()
        
        logger.info("✅ All agent nodes created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating agent nodes: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create workflow
    try:
        logger.info("Creating agent workflow...")
        agents = {
            "conversation_lead_agent": conversation_lead,
            "flight_booking_agent": flight_booking,
            "hotel_booking_agent": hotel_booking,
            "trip_planning_agent": trip_planning
        }
        
        workflow = create_agent_workflow(agents)
        logger.info("✅ Workflow created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test messages
    test_messages = [
        {
            "message": "I want to book a flight from Riyadh to Jeddah next week",
            "expected_intent": "flight_booking",
            "language": "english",
            "description": "Flight booking request in English"
        },
        {
            "message": "أريد حجز فندق في الرياض لمدة 3 أيام",
            "expected_intent": "hotel_booking",
            "language": "arabic",
            "description": "Hotel booking request in Arabic (I want to book a hotel in Riyadh for 3 days)"
        },
        {
            "message": "I need to plan a complete trip from Jeddah to Riyadh next month",
            "expected_intent": "trip_planning", 
            "language": "english",
            "description": "Trip planning request in English"
        }
    ]
    
    # Run tests
    success_count = 0
    
    for i, test in enumerate(test_messages):
        session_id = f"test_session_{uuid.uuid4().hex[:8]}"
        logger.info(f"\n\n===== Test {i+1}: {test['description']} =====")
        logger.info(f"Message: '{test['message']}'")
        logger.info(f"Expected intent: {test['expected_intent']}")
        
        try:
            # Create initial state
            state = {
                "session_id": session_id,
                "message": test["message"],
                "language": test["language"]
            }
            
            # Execute workflow
            logger.info(f"Running workflow...")
            result = workflow.invoke(state)
            
            # Log results
            logger.info(f"Workflow completed")
            logger.info(f"Final agent: {result.get('current_agent', 'unknown')}")
            logger.info(f"Detected intent: {result.get('intent', 'unknown')}")
            
            # Check response
            response = result.get('response', '')
            logger.info(f"Response: {response[:150]}..." if response else "No response generated")
            
            # Check mock data
            mock_data = result.get('mock_data', {})
            if 'flights' in mock_data:
                logger.info(f"Generated {len(mock_data['flights'])} flight options")
            if 'hotels' in mock_data:
                logger.info(f"Generated {len(mock_data['hotels'])} hotel options")
            if 'trip_packages' in mock_data:
                logger.info(f"Generated {len(mock_data['trip_packages'])} trip packages")
            
            # Check if intent matches expected
            detected_intent = result.get('intent', 'unknown')
            if detected_intent == test['expected_intent']:
                logger.info("✅ Test passed: Intent detected correctly")
                success_count += 1
            else:
                logger.warning(f"❌ Test failed: Expected intent '{test['expected_intent']}' but got '{detected_intent}'")
                
        except Exception as e:
            logger.error(f"❌ Error running workflow: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Summary
    logger.info(f"\n\n===== Test Summary =====")
    logger.info(f"Total tests: {len(test_messages)}")
    logger.info(f"Successful tests: {success_count}")
    logger.info(f"Success rate: {success_count/len(test_messages)*100:.1f}%")
    
    return success_count == len(test_messages)

if __name__ == "__main__":
    logger.info("Starting LangGraph Workflow Test for Trip Planning Assistant")
    success = test_workflow()
    logger.info(f"\nOverall test {'succeeded' if success else 'failed'}")

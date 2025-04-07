"""
Test script for Agent System
This script tests the agent system with various user intents
"""
import os
import sys
import uuid
from dotenv import load_dotenv
from agents.agent_system import AgentSystem

# Load environment variables
load_dotenv()

# Check for API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("Error: DEEPSEEK_API_KEY not found in environment variables")
    print("Make sure you have a .env file with DEEPSEEK_API_KEY=your_api_key")
    sys.exit(1)

def test_conversation_lead():
    """Test the Conversation Lead Agent"""
    print("\n--- Testing Conversation Lead Agent ---")
    
    try:
        # Initialize agent system
        agent_system = AgentSystem()
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Test general conversation
        print("Sending general conversation message...")
        response = agent_system.process_message(
            session_id=session_id,
            message="Hello! I'm planning to visit Saudi Arabia. Can you help me?"
        )
        
        # Print response
        print("\nResponse from Conversation Lead Agent:")
        print(response["text"])
        print(f"Detected intent: {response['intent']}")
        
        print("\nConversation Lead Agent test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing Conversation Lead Agent: {str(e)}")
        return False

def test_flight_booking():
    """Test the Flight Booking Agent"""
    print("\n--- Testing Flight Booking Agent ---")
    
    try:
        # Initialize agent system
        agent_system = AgentSystem()
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Test flight booking
        print("Sending flight booking message...")
        response = agent_system.process_message(
            session_id=session_id,
            message="I need a flight from Riyadh to Jeddah on 2025-05-15 for 2 passengers in economy class."
        )
        
        # Print response
        print("\nResponse from Flight Booking Agent:")
        print(response["text"])
        print(f"Detected intent: {response['intent']}")
        
        print("\nFlight Booking Agent test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing Flight Booking Agent: {str(e)}")
        return False

def test_hotel_booking():
    """Test the Hotel Booking Agent"""
    print("\n--- Testing Hotel Booking Agent ---")
    
    try:
        # Initialize agent system
        agent_system = AgentSystem()
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Test hotel booking
        print("Sending hotel booking message...")
        response = agent_system.process_message(
            session_id=session_id,
            message="I need a hotel in Riyadh from 2025-05-15 to 2025-05-18 for 2 guests and 1 room."
        )
        
        # Print response
        print("\nResponse from Hotel Booking Agent:")
        print(response["text"])
        print(f"Detected intent: {response['intent']}")
        
        print("\nHotel Booking Agent test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing Hotel Booking Agent: {str(e)}")
        return False

def test_trip_planning():
    """Test the Trip Planning Agent"""
    print("\n--- Testing Trip Planning Agent ---")
    
    try:
        # Initialize agent system
        agent_system = AgentSystem()
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # First, get flight options
        print("Setting up flight options...")
        flight_response = agent_system.process_message(
            session_id=session_id,
            message="I need a flight from Riyadh to Jeddah on 2025-05-15 for 2 passengers in economy class."
        )
        
        # Then, get hotel options
        print("\nSetting up hotel options...")
        hotel_response = agent_system.process_message(
            session_id=session_id,
            message="I need a hotel in Jeddah from 2025-05-15 to 2025-05-18 for 2 guests and 1 room."
        )
        
        # Finally, request a trip plan
        print("\nSending trip planning message...")
        response = agent_system.process_message(
            session_id=session_id,
            message="Can you create a 3-day trip plan for me in Jeddah? I'm interested in history, culture, and food."
        )
        
        # Print response
        print("\nResponse from Trip Planning Agent:")
        print(response["text"])
        print(f"Detected intent: {response['intent']}")
        
        print("\nTrip Planning Agent test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing Trip Planning Agent: {str(e)}")
        return False

def test_arabic_support():
    """Test Arabic language support"""
    print("\n--- Testing Arabic Language Support ---")
    
    try:
        # Initialize agent system
        agent_system = AgentSystem()
        
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Test Arabic conversation
        print("Sending Arabic message...")
        response = agent_system.process_message(
            session_id=session_id,
            message="مرحبا! أنا أخطط لزيارة المملكة العربية السعودية. هل يمكنك مساعدتي؟",
            language="arabic"
        )
        
        # Print response
        print("\nResponse in Arabic:")
        print(response["text"])
        print(f"Detected intent: {response['intent']}")
        
        print("\nArabic language support test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing Arabic language support: {str(e)}")
        return False

def main():
    """Main function to run tests"""
    print("=== Agent System Integration Test ===")
    
    # Run tests
    lead_success = test_conversation_lead()
    flight_success = test_flight_booking()
    hotel_success = test_hotel_booking()
    trip_success = test_trip_planning()
    arabic_success = test_arabic_support()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Conversation Lead Agent test: {'PASSED' if lead_success else 'FAILED'}")
    print(f"Flight Booking Agent test: {'PASSED' if flight_success else 'FAILED'}")
    print(f"Hotel Booking Agent test: {'PASSED' if hotel_success else 'FAILED'}")
    print(f"Trip Planning Agent test: {'PASSED' if trip_success else 'FAILED'}")
    print(f"Arabic language support test: {'PASSED' if arabic_success else 'FAILED'}")
    
    if lead_success and flight_success and hotel_success and trip_success and arabic_success:
        print("\nAll tests passed! Agent system is working correctly.")
    else:
        print("\nSome tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

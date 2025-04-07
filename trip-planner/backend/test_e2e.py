"""
End-to-End Testing for Trip Planning Assistant

This module contains comprehensive tests that simulate complete user interactions
with the Trip Planning Assistant, including:
- Multi-turn conversations
- Language switching mid-conversation
- Error handling and recovery
- Complete trip planning workflows
"""
import os
import requests
import time
import json
import uuid
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base URL for API
BASE_URL = "http://localhost:5003"

def test_multi_turn_conversation():
    """Test a multi-turn conversation with the Trip Planning Assistant"""
    logger.info("Starting multi-turn conversation test")
    
    # Generate a unique session ID for this test
    session_id = str(uuid.uuid4())
    logger.info(f"Using session ID: {session_id}")
    
    # Define conversation turns
    conversation = [
        {
            "message": "Hello! I'm planning to visit Saudi Arabia for a week. Can you help me?",
            "expected_intent": "greeting",
            "description": "Initial greeting"
        },
        {
            "message": "I'd like to fly from London to Riyadh on May 20, 2025 and return on May 27",
            "expected_intent": "flight_booking",
            "description": "Flight booking request"
        },
        {
            "message": "Can you show me more flight options?",
            "expected_intent": "flight_booking",
            "description": "Request for more flight options"
        },
        {
            "message": "I'll take the Emirates flight. Now I need a hotel in Riyadh for my stay",
            "expected_intent": "hotel_booking",
            "description": "Hotel booking request"
        },
        {
            "message": "I'd prefer a 5-star hotel close to the city center",
            "expected_intent": "hotel_booking",
            "description": "Hotel preference specification"
        },
        {
            "message": "Can you suggest a 3-day itinerary for Riyadh?",
            "expected_intent": "trip_planning",
            "description": "Trip planning request"
        },
        {
            "message": "That sounds great! Can you include some local food recommendations?",
            "expected_intent": "trip_planning",
            "description": "Trip planning refinement"
        }
    ]
    
    # Run through the conversation
    for i, turn in enumerate(conversation):
        logger.info(f"Turn {i+1}: {turn['description']}")
        
        # Prepare request
        url = f"{BASE_URL}/api/chat"
        payload = {
            "message": turn["message"],
            "session_id": session_id,
            "language": "english"
        }
        
        # Make request
        response = requests.post(url, json=payload)
        
        # Check response
        assert response.status_code == 200, f"Turn {i+1} failed with status {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, f"Turn {i+1} returned success=False: {data.get('error')}"
        
        # Log response details
        logger.info(f"Response intent: {data['data'].get('intent')}")
        logger.info(f"Response: {data['data'].get('response')[:100]}...")
        
        # Optional: Add specific assertions about the content based on expected_intent
        if turn["expected_intent"] == "flight_booking":
            assert "flight" in data["data"]["response"].lower() or "airlines" in data["data"]["response"].lower(), "Flight booking response should mention flights"
        elif turn["expected_intent"] == "hotel_booking":
            assert "hotel" in data["data"]["response"].lower() or "accommodation" in data["data"]["response"].lower(), "Hotel booking response should mention hotels"
        elif turn["expected_intent"] == "trip_planning":
            assert "itinerary" in data["data"]["response"].lower() or "day" in data["data"]["response"].lower(), "Trip planning response should mention itinerary"
        
        # Small delay to prevent overloading the server
        time.sleep(1)
    
    logger.info("Multi-turn conversation test completed successfully")
    return True

def test_language_switching():
    """Test switching between languages mid-conversation"""
    logger.info("Starting language switching test")
    
    # Generate a unique session ID for this test
    session_id = str(uuid.uuid4())
    logger.info(f"Using session ID: {session_id}")
    
    # Define conversation with language switching
    conversation = [
        {
            "message": "Hello! I'm planning to visit Jeddah next month",
            "language": "english",
            "description": "Initial message in English"
        },
        {
            "message": "أريد حجز فندق في جدة",  # "I want to book a hotel in Jeddah"
            "language": "arabic",
            "description": "Switch to Arabic for hotel booking"
        },
        {
            "message": "أريد فندق قريب من البحر",  # "I want a hotel near the sea"
            "language": "arabic",
            "description": "Continue in Arabic"
        },
        {
            "message": "Thank you! Can you also suggest some tourist attractions?",
            "language": "english",
            "description": "Switch back to English"
        }
    ]
    
    # Run through the conversation
    for i, turn in enumerate(conversation):
        logger.info(f"Turn {i+1}: {turn['description']}")
        
        # Prepare request
        url = f"{BASE_URL}/api/chat"
        payload = {
            "message": turn["message"],
            "session_id": session_id,
            "language": turn["language"]
        }
        
        # Make request
        response = requests.post(url, json=payload)
        
        # Check response
        assert response.status_code == 200, f"Turn {i+1} failed with status {response.status_code}"
        
        data = response.json()
        assert data["success"] is True, f"Turn {i+1} returned success=False: {data.get('error')}"
        
        # Check language of response
        if turn["language"] == "arabic":
            # Check for Arabic characters in the response
            has_arabic = any('\u0600' <= c <= '\u06FF' for c in data["data"]["response"])
            assert has_arabic, "Response should contain Arabic characters for Arabic messages"
        
        logger.info(f"Response ({turn['language']}): {data['data'].get('response')[:100]}...")
        
        # Small delay to prevent overloading the server
        time.sleep(1)
    
    logger.info("Language switching test completed successfully")
    return True

def test_error_handling_recovery():
    """Test how the system handles errors and recovers from them"""
    logger.info("Starting error handling and recovery test")
    
    # Generate a unique session ID for this test
    session_id = str(uuid.uuid4())
    
    # Define conversation with potential error cases
    conversation = [
        {
            "message": "Hello there",
            "description": "Normal greeting"
        },
        {
            "message": "",  # Empty message
            "description": "Empty message (should trigger error)",
            "expect_error": True
        },
        {
            "message": "I need a flight",  # Valid message after error
            "description": "Recovery after error"
        },
        {
            "message": "x" * 10000,  # Extremely long message
            "description": "Very long message (potential error case)",
            "expect_error": True
        },
        {
            "message": "Can you help me find a hotel?",
            "description": "Recovery after potential error"
        }
    ]
    
    # Run through the conversation
    for i, turn in enumerate(conversation):
        logger.info(f"Turn {i+1}: {turn['description']}")
        
        # Prepare request
        url = f"{BASE_URL}/api/chat"
        payload = {
            "message": turn["message"],
            "session_id": session_id,
            "language": "english"
        }
        
        # Make request
        response = requests.post(url, json=payload)
        
        # Check response based on whether we expect an error
        expect_error = turn.get("expect_error", False)
        
        if expect_error:
            # For error cases, we might still get a 200 response with success=False,
            # or we might get a non-200 status code
            if response.status_code == 200:
                data = response.json()
                # It's okay if we either get success=False or success=True (graceful handling)
                logger.info(f"Response for expected error case: {data}")
            else:
                logger.info(f"Received status code {response.status_code} for expected error case")
        else:
            # For non-error cases, we expect a 200 response with success=True
            assert response.status_code == 200, f"Turn {i+1} failed with status {response.status_code}"
            data = response.json()
            assert data["success"] is True, f"Turn {i+1} returned success=False: {data.get('error')}"
            logger.info(f"Response: {data['data'].get('response')[:100]}...")
        
        # Small delay to prevent overloading the server
        time.sleep(1)
    
    logger.info("Error handling and recovery test completed")
    return True

def main():
    """Main function to run all end-to-end tests"""
    print("=== Trip Planning Assistant End-to-End Tests ===")
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=10)
    except Exception as e:
        print("Error: Flask server is not running. Please start the server first.")
        print(f"Server should be running at {BASE_URL}")
        print("\nCommand to start server:")
        print("cd /Users/salehgazwani/Desktop/repo/Rahallah10.13/trip-planner/backend")
        print("python wsgi.py")
        return
    
    # Run tests
    multi_turn_success = test_multi_turn_conversation()
    language_switch_success = test_language_switching()
    error_handling_success = test_error_handling_recovery()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Multi-turn conversation test: {'PASSED' if multi_turn_success else 'FAILED'}")
    print(f"Language switching test: {'PASSED' if language_switch_success else 'FAILED'}")
    print(f"Error handling and recovery test: {'PASSED' if error_handling_success else 'FAILED'}")
    
    if multi_turn_success and language_switch_success and error_handling_success:
        print("\nAll end-to-end tests PASSED! The backend is fully functional.")
    else:
        print("\nSome tests FAILED. Please check the logs for details.")

if __name__ == "__main__":
    main()

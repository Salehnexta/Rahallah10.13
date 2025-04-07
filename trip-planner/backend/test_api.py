"""
Test script for Trip Planning Assistant API endpoints
This script tests the Flask API endpoints using requests
"""
import os
import sys
import json
import uuid
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base URL for API
BASE_URL = "http://localhost:5000"

def test_health_endpoint():
    """Test the health check endpoint"""
    print("\n--- Testing Health Check Endpoint ---")
    
    try:
        # Make request to health endpoint
        response = requests.get(f"{BASE_URL}/api/health")
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(f"Status: {data.get('status')}")
            print(f"Version: {data.get('version')}")
            print(f"LLM Status: {data.get('llm_status')}")
            print("\nHealth check endpoint test successful!")
            return True
        else:
            print(f"\nError: Received status code {response.status_code}")
            print(response.text)
            return False
        
    except Exception as e:
        print(f"\nError testing health check endpoint: {str(e)}")
        return False

def test_languages_endpoint():
    """Test the supported languages endpoint"""
    print("\n--- Testing Supported Languages Endpoint ---")
    
    try:
        # Make request to languages endpoint
        response = requests.get(f"{BASE_URL}/api/languages")
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(f"Supported Languages: {data.get('supported_languages')}")
            print(f"Default Language: {data.get('default_language')}")
            print("\nSupported languages endpoint test successful!")
            return True
        else:
            print(f"\nError: Received status code {response.status_code}")
            print(response.text)
            return False
        
    except Exception as e:
        print(f"\nError testing supported languages endpoint: {str(e)}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("\n--- Testing Chat Endpoint ---")
    
    try:
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Test messages for different intents
        test_messages = [
            {
                "description": "General greeting",
                "message": "Hello! I'm planning to visit Saudi Arabia. Can you help me?"
            },
            {
                "description": "Flight booking intent",
                "message": "I need a flight from Riyadh to Jeddah on 2025-05-15 for 2 passengers in economy class."
            },
            {
                "description": "Hotel booking intent",
                "message": "I need a hotel in Jeddah from 2025-05-15 to 2025-05-18 for 2 guests and 1 room."
            },
            {
                "description": "Trip planning intent",
                "message": "Can you create a 3-day trip plan for me in Jeddah? I'm interested in history, culture, and food."
            }
        ]
        
        # Test each message
        for test in test_messages:
            print(f"\nTesting: {test['description']}")
            print(f"Message: {test['message']}")
            
            # Prepare payload
            payload = {
                "session_id": session_id,
                "message": test["message"]
            }
            
            # Make request to chat endpoint
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            # Check response
            if response.status_code == 200:
                data = response.json()
                print(f"Session ID: {data.get('session_id')}")
                print(f"Intent: {data.get('intent')}")
                print(f"Language: {data.get('language')}")
                print(f"Response: {data.get('response')[:100]}..." if len(data.get('response', '')) > 100 else f"Response: {data.get('response')}")
            else:
                print(f"\nError: Received status code {response.status_code}")
                print(response.text)
                return False
        
        print("\nChat endpoint test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing chat endpoint: {str(e)}")
        return False

def test_reset_endpoint():
    """Test the reset session endpoint"""
    print("\n--- Testing Reset Session Endpoint ---")
    
    try:
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # First, create a session with a message
        chat_payload = {
            "session_id": session_id,
            "message": "Hello, this is a test message."
        }
        
        chat_response = requests.post(
            f"{BASE_URL}/api/chat",
            json=chat_payload,
            headers={"Content-Type": "application/json"}
        )
        
        if chat_response.status_code != 200:
            print(f"\nError creating test session: {chat_response.status_code}")
            return False
        
        # Now reset the session
        reset_payload = {
            "session_id": session_id
        }
        
        reset_response = requests.post(
            f"{BASE_URL}/api/reset",
            json=reset_payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        if reset_response.status_code == 200:
            data = reset_response.json()
            print(f"Status: {data.get('status')}")
            print(f"Message: {data.get('message')}")
            print("\nReset session endpoint test successful!")
            return True
        else:
            print(f"\nError: Received status code {reset_response.status_code}")
            print(reset_response.text)
            return False
        
    except Exception as e:
        print(f"\nError testing reset session endpoint: {str(e)}")
        return False

def test_arabic_support():
    """Test Arabic language support"""
    print("\n--- Testing Arabic Language Support ---")
    
    try:
        # Generate a session ID
        session_id = str(uuid.uuid4())
        
        # Prepare payload with Arabic message
        payload = {
            "session_id": session_id,
            "message": "مرحبا! أنا أخطط لزيارة المملكة العربية السعودية. هل يمكنك مساعدتي؟"
        }
        
        # Make request to chat endpoint
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        # Check response
        if response.status_code == 200:
            data = response.json()
            print(f"Session ID: {data.get('session_id')}")
            print(f"Intent: {data.get('intent')}")
            print(f"Language: {data.get('language')}")
            print(f"Response: {data.get('response')[:100]}..." if len(data.get('response', '')) > 100 else f"Response: {data.get('response')}")
            print("\nArabic language support test successful!")
            return True
        else:
            print(f"\nError: Received status code {response.status_code}")
            print(response.text)
            return False
        
    except Exception as e:
        print(f"\nError testing Arabic language support: {str(e)}")
        return False

def main():
    """Main function to run tests"""
    print("=== Trip Planning Assistant API Test ===")
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/api/health", timeout=2)
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to the server. Please make sure the Flask app is running.")
        print(f"Expected server at: {BASE_URL}")
        print("Run the server with: python app.py")
        return
    
    # Run tests
    health_success = test_health_endpoint()
    languages_success = test_languages_endpoint()
    chat_success = test_chat_endpoint()
    reset_success = test_reset_endpoint()
    arabic_success = test_arabic_support()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Health check endpoint test: {'PASSED' if health_success else 'FAILED'}")
    print(f"Supported languages endpoint test: {'PASSED' if languages_success else 'FAILED'}")
    print(f"Chat endpoint test: {'PASSED' if chat_success else 'FAILED'}")
    print(f"Reset session endpoint test: {'PASSED' if reset_success else 'FAILED'}")
    print(f"Arabic language support test: {'PASSED' if arabic_success else 'FAILED'}")
    
    if health_success and languages_success and chat_success and reset_success and arabic_success:
        print("\nAll tests passed! API endpoints are working correctly.")
    else:
        print("\nSome tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

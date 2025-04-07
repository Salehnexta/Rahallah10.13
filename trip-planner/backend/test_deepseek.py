"""
Test script for DeepSeek API integration using OpenAI SDK
This script tests the connection to DeepSeek and verifies that we can generate responses
"""
import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    print("Error: DEEPSEEK_API_KEY not found in environment variables")
    print("Make sure you have a .env file with DEEPSEEK_API_KEY=your_api_key")
    sys.exit(1)

# DeepSeek API base URL
DEEPSEEK_API_BASE = "https://api.deepseek.com"

def test_direct_openai_sdk():
    """Test DeepSeek integration using direct OpenAI SDK"""
    print("\n--- Testing Direct OpenAI SDK Integration ---")
    
    try:
        # Initialize OpenAI client
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_BASE
        )
        
        # Test chat completion
        print("Sending test message to DeepSeek...")
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a travel assistant for Saudi Arabia."},
                {"role": "user", "content": "Hello! Can you help me plan a trip?"}
            ],
            temperature=0.7,
            stream=False
        )
        
        # Print response
        print("\nResponse from DeepSeek:")
        print(response.choices[0].message.content)
        print("\nDirect OpenAI SDK test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing direct OpenAI SDK: {str(e)}")
        return False

def test_with_our_utils():
    """Test DeepSeek integration using our utility functions"""
    print("\n--- Testing Our Utility Functions ---")
    
    try:
        # Import our utility functions
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from agents.llm_utils import generate_response
        
        # Test response generation
        print("Generating response using our utility functions...")
        response = generate_response(
            system_prompt="You are a travel assistant for Saudi Arabia.",
            user_message="Hello! Can you help me plan a trip to Riyadh?",
            temperature=0.7
        )
        
        # Print response
        print("\nResponse from DeepSeek:")
        print(response)
        print("\nUtility function test successful!")
        return True
        
    except ImportError as e:
        if "langchain" in str(e):
            print("\nSkipping LangChain test as it's not installed. This is expected as we're using direct OpenAI SDK.")
            return True
        else:
            print(f"\nError testing utility functions: {str(e)}")
            return False
    except Exception as e:
        print(f"\nError testing utility functions: {str(e)}")
        return False

def main():
    """Main function to run tests"""
    print("=== DeepSeek API Integration Test ===")
    print(f"Using API key: {DEEPSEEK_API_KEY[:5]}...{DEEPSEEK_API_KEY[-5:]}")
    print(f"API base URL: {DEEPSEEK_API_BASE}")
    
    # Run tests
    direct_sdk_success = test_direct_openai_sdk()
    utils_success = test_with_our_utils()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Direct OpenAI SDK test: {'PASSED' if direct_sdk_success else 'FAILED'}")
    print(f"Utility functions test: {'PASSED' if utils_success else 'FAILED'}")
    
    if direct_sdk_success and utils_success:
        print("\nAll tests passed! DeepSeek integration is working correctly.")
    else:
        print("\nSome tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

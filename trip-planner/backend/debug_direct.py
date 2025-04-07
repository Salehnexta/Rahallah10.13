"""
Debug script for testing direct OpenAI integration with DeepSeek
"""
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print(f"API Key available: {'Yes' if DEEPSEEK_API_KEY else 'No'}")
if DEEPSEEK_API_KEY:
    print(f"First 5 chars of API key: {DEEPSEEK_API_KEY[:5]}...")

# Initialize client
try:
    print("Initializing OpenAI client...")
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )
    print("Client initialized successfully")
    
    # Create messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello in Arabic."}
    ]
    
    print(f"Sending request to DeepSeek with messages: {json.dumps(messages, indent=2)}")
    
    # Generate response
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        temperature=0.7
    )
    
    print(f"Response received successfully!")
    print(f"Content: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

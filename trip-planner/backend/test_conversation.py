"""
Simple conversation test script for DeepSeek API integration
"""
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment variable
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("DEEPSEEK_API_KEY not found in environment variables. Please check your .env file.")

# Initialize the OpenAI client with DeepSeek API base URL
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

def test_conversation():
    """Test a simple conversation with DeepSeek API"""
    # System message to set the assistant's role
    system_message = "You are a travel planning assistant for Saudi Arabia, helping users book flights, hotels, and plan trips."
    
    # Define conversation (you can modify these messages to test different scenarios)
    conversation = [
        {"role": "user", "content": "Hello! I'm planning a trip to Riyadh next month."}
    ]
    
    # Initialize messages array with system message
    messages = [{"role": "system", "content": system_message}]
    messages.extend(conversation)
    
    print("Sending the following conversation to DeepSeek:")
    for msg in conversation:
        print(f"{msg['role']}: {msg['content']}")
    print()
    
    # Generate response
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and display the response
        assistant_message = response.choices[0].message.content
        print("Assistant:", assistant_message)
        
        # Continue the conversation
        conversation.append({"role": "assistant", "content": assistant_message})
        conversation.append({"role": "user", "content": "What are the must-visit places in Riyadh?"})
        
        # Update messages with the full conversation history
        messages = [{"role": "system", "content": system_message}]
        messages.extend(conversation)
        
        print("\nContinuing the conversation:")
        print(f"user: What are the must-visit places in Riyadh?")
        print()
        
        # Generate another response
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and display the response
        assistant_message = response.choices[0].message.content
        print("Assistant:", assistant_message)
        
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing conversation with DeepSeek API...\n")
    success = test_conversation()
    if success:
        print("\nConversation test completed successfully!")
    else:
        print("\nConversation test failed.")

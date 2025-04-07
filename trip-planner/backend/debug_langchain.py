"""
Debug script for testing LangChain integration with DeepSeek
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print(f"API Key available: {'Yes' if DEEPSEEK_API_KEY else 'No'}")

try:
    print("Importing LangChain components...")
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.schema import HumanMessage, SystemMessage
    print("LangChain imports successful")
    
    # Print LangChain version
    import langchain
    print(f"LangChain version: {langchain.__version__}")
    
    # Initialize LangChain chat model
    print("Initializing LangChain ChatOpenAI...")
    chat = ChatOpenAI(
        model="deepseek-chat",
        temperature=0.7,
        openai_api_base="https://api.deepseek.com",
        openai_api_key=DEEPSEEK_API_KEY
    )
    print("ChatOpenAI initialized successfully")
    
    # Create messages
    messages = [
        SystemMessage(content="You are a helpful assistant."),
        HumanMessage(content="What's the capital of Saudi Arabia?")
    ]
    
    print(f"Sending request to DeepSeek using LangChain...")
    
    # Generate response
    response = chat.invoke(messages)
    
    print(f"Response received successfully!")
    print(f"Content: {response.content}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()

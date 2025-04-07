"""
Test script for LangChain integration with DeepSeek
This script tests the LangChain framework with conversation memory
"""
import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

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

def test_basic_chain():
    """Test basic LangChain setup with DeepSeek"""
    print("\n--- Testing Basic LangChain Setup ---")
    
    try:
        # Initialize ChatOpenAI model
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_BASE
        )
        
        # Create a simple prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a travel assistant for Saudi Arabia."),
            ("human", "{input}")
        ])
        
        # Create a simple chain
        chain = prompt | llm | StrOutputParser()
        
        # Test the chain
        print("Sending test message to LangChain...")
        response = chain.invoke({"input": "Hello! Can you recommend a 3-day itinerary for Riyadh?"})
        
        # Print response
        print("\nResponse from LangChain:")
        print(response)
        print("\nBasic LangChain test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing basic LangChain: {str(e)}")
        return False

def test_conversation_memory():
    """Test LangChain with conversation memory"""
    print("\n--- Testing LangChain with Conversation Memory ---")
    
    try:
        # Initialize ChatOpenAI model
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_BASE
        )
        
        # Initialize conversation memory
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            input_key="input"
        )
        
        # Create a prompt template with memory
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a travel assistant for Saudi Arabia. Be helpful, concise, and friendly."),
            ("placeholder", "{chat_history}"),
            ("human", "{input}")
        ])
        
        # Create a chain with memory
        chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: memory.load_memory_variables({})["chat_history"]
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # First message
        print("Sending first message...")
        first_response = chain.invoke({"input": "I'm planning to visit Riyadh next month. What are the must-see attractions?"})
        memory.save_context(
            {"input": "I'm planning to visit Riyadh next month. What are the must-see attractions?"},
            {"output": first_response}
        )
        
        print("\nFirst response:")
        print(first_response)
        
        # Follow-up message
        print("\nSending follow-up message...")
        follow_up_response = chain.invoke({"input": "What about local food? Any recommendations?"})
        memory.save_context(
            {"input": "What about local food? Any recommendations?"},
            {"output": follow_up_response}
        )
        
        print("\nFollow-up response:")
        print(follow_up_response)
        
        print("\nConversation Memory test successful!")
        return True
        
    except Exception as e:
        print(f"\nError testing conversation memory: {str(e)}")
        return False

def main():
    """Main function to run tests"""
    print("=== LangChain Integration Test ===")
    print(f"Using API key: {DEEPSEEK_API_KEY[:5]}...{DEEPSEEK_API_KEY[-5:]}")
    print(f"API base URL: {DEEPSEEK_API_BASE}")
    
    # Run tests
    basic_chain_success = test_basic_chain()
    memory_success = test_conversation_memory()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Basic LangChain test: {'PASSED' if basic_chain_success else 'FAILED'}")
    print(f"Conversation Memory test: {'PASSED' if memory_success else 'FAILED'}")
    
    if basic_chain_success and memory_success:
        print("\nAll tests passed! LangChain integration is working correctly.")
    else:
        print("\nSome tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

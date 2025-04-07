"""
Debug script for testing DeepSeek LLM integration with LangChain
"""

import os
import sys
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema.messages import SystemMessage, HumanMessage

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

def test_direct_openai():
    """Test direct OpenAI API integration with DeepSeek"""
    logger.info("Testing direct OpenAI integration with DeepSeek")
    
    try:
        # Initialize client
        logger.debug(f"Initializing OpenAI client with base URL: https://api.deepseek.com")
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        
        # Create messages
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello in Arabic."}
        ]
        
        logger.debug(f"Sending request to DeepSeek with messages: {messages}")
        
        # Generate response
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7
        )
        
        logger.info(f"Received response from DeepSeek: {response}")
        logger.info(f"Content: {response.choices[0].message.content}")
        
        return True, response.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error in direct OpenAI test: {str(e)}", exc_info=True)
        return False, str(e)

def test_langchain_integration():
    """Test LangChain integration with DeepSeek"""
    logger.info("Testing LangChain integration with DeepSeek")
    
    try:
        # Initialize LangChain chat model
        logger.debug(f"Initializing LangChain ChatOpenAI with DeepSeek")
        llm = ChatOpenAI(
            model="deepseek-chat",
            temperature=0.7,
            openai_api_base="https://api.deepseek.com",
            openai_api_key=DEEPSEEK_API_KEY
        )
        
        # Create messages
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="What's the capital of Saudi Arabia?")
        ]
        
        logger.debug(f"Sending request to DeepSeek using LangChain with messages: {messages}")
        
        # Generate response
        response = llm.invoke(messages)
        
        logger.info(f"Received response from LangChain: {response}")
        logger.info(f"Content: {response.content}")
        
        return True, response.content
    
    except Exception as e:
        logger.error(f"Error in LangChain test: {str(e)}", exc_info=True)
        return False, str(e)

def check_environment():
    """Check environment variables and package versions"""
    logger.info("Checking environment")
    
    try:
        # Check API key
        if not DEEPSEEK_API_KEY:
            logger.error("DEEPSEEK_API_KEY not found in environment variables")
            return False, "API key not found"
        
        logger.debug(f"API key found: {DEEPSEEK_API_KEY[:5]}...")
        
        # Check package versions
        import pkg_resources
        
        packages = [
            "openai",
            "langchain",
            "pydantic",
            "requests"
        ]
        
        version_info = {}
        for package in packages:
            try:
                version = pkg_resources.get_distribution(package).version
                version_info[package] = version
                logger.debug(f"{package}: {version}")
            except pkg_resources.DistributionNotFound:
                logger.error(f"{package} not installed")
                version_info[package] = "Not installed"
        
        return True, version_info
    
    except Exception as e:
        logger.error(f"Error checking environment: {str(e)}", exc_info=True)
        return False, str(e)

if __name__ == "__main__":
    logger.info("Starting debug script")
    
    # Check environment
    logger.info("=" * 50)
    env_status, env_info = check_environment()
    if env_status:
        logger.info(f"Environment check successful: {json.dumps(env_info, indent=2)}")
    else:
        logger.error(f"Environment check failed: {env_info}")
    
    # Test direct OpenAI integration
    logger.info("=" * 50)
    openai_status, openai_response = test_direct_openai()
    if openai_status:
        logger.info(f"Direct OpenAI test successful: {openai_response}")
    else:
        logger.error(f"Direct OpenAI test failed: {openai_response}")
    
    # Test LangChain integration
    logger.info("=" * 50)
    langchain_status, langchain_response = test_langchain_integration()
    if langchain_status:
        logger.info(f"LangChain test successful: {langchain_response}")
    else:
        logger.error(f"LangChain test failed: {langchain_response}")
    
    logger.info("=" * 50)
    logger.info("Debug script completed")

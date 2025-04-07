"""
LangChain Utilities for Trip Planning Assistant
Implements LangChain integration with DeepSeek LLM
"""
import os
from dotenv import load_dotenv
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationBufferMemory
from langchain_core.runnables import RunnablePassthrough

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get API key
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    logger.error("DEEPSEEK_API_KEY not found in environment variables")
    raise ValueError("DEEPSEEK_API_KEY not set in .env file")

# DeepSeek API base URL
DEEPSEEK_API_BASE = "https://api.deepseek.com"

def get_llm(temperature=0.7, model="deepseek-chat"):
    """
    Initialize and return a ChatOpenAI model configured for DeepSeek
    
    Args:
        temperature (float): Controls randomness in responses (0.0 to 1.0)
        model (str): Model identifier for DeepSeek
        
    Returns:
        ChatOpenAI: Configured chat model
    """
    try:
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_API_BASE
        )
        return llm
    except Exception as e:
        logger.error(f"Error initializing LLM: {str(e)}")
        raise

def create_basic_chain(system_prompt):
    """
    Create a basic LangChain chain with a system prompt
    
    Args:
        system_prompt (str): System prompt for the LLM
        
    Returns:
        Chain: LangChain chain
    """
    try:
        # Initialize LLM
        llm = get_llm()
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])
        
        # Create chain
        chain = prompt | llm | StrOutputParser()
        
        return chain
    except Exception as e:
        logger.error(f"Error creating basic chain: {str(e)}")
        raise

def create_conversation_chain(system_prompt):
    """
    Create a LangChain chain with conversation memory
    
    Args:
        system_prompt (str): System prompt for the LLM
        
    Returns:
        tuple: (Chain, Memory) - LangChain chain and memory object
    """
    try:
        # Initialize LLM
        llm = get_llm()
        
        # Initialize conversation memory
        memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history",
            input_key="input"
        )
        
        # Create prompt template with memory
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("placeholder", "{chat_history}"),
            ("human", "{input}")
        ])
        
        # Create chain with memory
        chain = (
            RunnablePassthrough.assign(
                chat_history=lambda x: memory.load_memory_variables({})["chat_history"]
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return chain, memory
    except Exception as e:
        logger.error(f"Error creating conversation chain: {str(e)}")
        raise

def run_chain_with_memory(chain, memory, user_input):
    """
    Run a chain with memory and save the context
    
    Args:
        chain: LangChain chain
        memory: ConversationBufferMemory object
        user_input (str): User message
        
    Returns:
        str: LLM response
    """
    try:
        # Run the chain
        response = chain.invoke({"input": user_input})
        
        # Save the context
        memory.save_context(
            {"input": user_input},
            {"output": response}
        )
        
        return response
    except Exception as e:
        logger.error(f"Error running chain with memory: {str(e)}")
        return f"I'm sorry, I encountered an error: {str(e)}"

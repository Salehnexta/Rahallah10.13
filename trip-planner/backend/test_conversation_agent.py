"""
Simple test for the ConversationLeadAgent
"""
import os
import json
import unittest
from dotenv import load_dotenv
from agents.conversation_lead_agent import ConversationLeadAgent

# Load environment variables
load_dotenv()

class TestConversationAgent(unittest.TestCase):
    """Test class for ConversationLeadAgent"""
    
    def setUp(self):
        """Set up test environment"""
        self.conversation_agent = ConversationLeadAgent()
    
    def test_conversation_agent(self):
        """Test basic conversation agent functionality"""
        print("\nTesting conversation agent...")
        
        # Process a simple message
        response = self.conversation_agent.process_message(
            "test_session_123", 
            "Hello, I'm planning a trip to Riyadh", 
            "english"
        )
        
        print(f"Response: {response}")
        self.assertTrue("text" in response)
        self.assertTrue("intent" in response)
        self.assertTrue(response.get("success", False))

if __name__ == '__main__':
    unittest.main()

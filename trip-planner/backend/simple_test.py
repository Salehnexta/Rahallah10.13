"""
Simple test script for Trip Planning Assistant
Tests the basic LLM integration
"""
import os
import json
import unittest
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

class SimpleTest(unittest.TestCase):
    """Basic test class for Trip Planning Assistant"""
    
    def setUp(self):
        """Set up test environment"""
        openai.api_key = DEEPSEEK_API_KEY
        openai.api_base = "https://api.deepseek.com"
    
    def test_api_connection(self):
        """Test connection to DeepSeek API"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in Arabic."}
            ]
            
            response = openai.ChatCompletion.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            self.assertIsNotNone(content)
            self.assertTrue(len(content) > 0)
            print(f"API Response: {content[:100]}...")
            
        except Exception as e:
            self.fail(f"API connection test failed: {str(e)}")
    
if __name__ == '__main__':
    unittest.main()

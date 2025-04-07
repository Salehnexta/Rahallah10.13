"""
Simple test script for Trip Planning Assistant
Tests the basic LLM integration
"""
import os
import json
import unittest
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

class SimpleTest(unittest.TestCase):
    """Basic test class for Trip Planning Assistant"""
    
    def setUp(self):
        """Set up test environment"""
        self.client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )

        # Test system
        print("\nTesting system...")

        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello in Arabic."}
                ],
                temperature=0.7
            )
            print(f"API Response: {response.choices[0].message.content[:100]}...")
        except Exception as e:
            self.fail(f"API connection test failed: {str(e)}")
    
    def test_api_connection(self):
        """Test connection to DeepSeek API"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello in Arabic."}
            ]
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7
            )
            
            # Check if response contains expected fields
            self.assertTrue(len(response.choices) > 0)
            self.assertIsNotNone(response.choices[0].message)
            self.assertIsNotNone(response.choices[0].message.content)
            
            # Print response for debugging
            print(f"\nAPI Response: {response.choices[0].message.content[:100]}...")
            
        except Exception as e:
            self.fail(f"API connection test failed: {str(e)}")
    
if __name__ == '__main__':
    unittest.main()

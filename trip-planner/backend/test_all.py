"""
Comprehensive test script for Trip Planning Assistant
Tests all components including LLM integration, agent functionality, and API endpoints
"""
import os
import json
import logging
import unittest
from datetime import datetime
from dotenv import load_dotenv
from agents.agent_system import AgentSystem
from agents.llm_utils import generate_response
from langchain.output_parsers.structured import ResponseSchema, StructuredOutputParser
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class TestTripPlanningAssistant(unittest.TestCase):
    """Test class for Trip Planning Assistant"""
    
    def setUp(self):
        """Set up test environment"""
        self.session_id = "test_session_123"
        self.agent_system = AgentSystem()
        
    def test_llm_connection(self):
        """Test LLM connection"""
        logger.info("Testing LLM connection...")
        
        # Test English
        response = generate_response(
            system_prompt="You are a travel assistant for Saudi Arabia.",
            user_message="What are the best places to visit in Jeddah?",
            temperature=0.7
        )
        
        self.assertTrue(response["success"])
        self.assertIn("text", response)
        
        # Test Arabic
        response = generate_response(
            system_prompt="أنت مساعد رحلات في المملكة العربية السعودية.",
            user_message="ما هي أفضل الأماكن للزيارة في جدة؟",
            temperature=0.7
        )
        
        self.assertTrue(response["success"])
        self.assertIn("text", response)
        
        logger.info("LLM connection successful")
    
    def test_flight_booking(self):
        """Test flight booking functionality"""
        logger.info("Testing flight booking...")
        
        # Test English
        response = self.agent_system.process_message(
            self.session_id,
            "I want to fly from Riyadh to Jeddah next week.",
            "english"
        )
        
        self.assertEqual(response["intent"], "flight_booking")
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        self.assertIn("flight_options", response["mock_data"])
        
        # Test Arabic
        response = self.agent_system.process_message(
            self.session_id,
            "أريد السفر من الرياض إلى جدة الأسبوع القادم.",
            "arabic"
        )
        
        self.assertEqual(response["intent"], "flight_booking")
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        self.assertIn("flight_options", response["mock_data"])
        
        logger.info("Flight booking tests passed")
    
    def test_hotel_booking(self):
        """Test hotel booking functionality"""
        logger.info("Testing hotel booking...")
        
        # Test English
        response = self.agent_system.process_message(
            self.session_id,
            "I need a hotel in Riyadh for 3 nights.",
            "english"
        )
        
        self.assertEqual(response["intent"], "hotel_booking")
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        self.assertIn("hotel_options", response["mock_data"])
        
        # Test Arabic
        response = self.agent_system.process_message(
            self.session_id,
            "أحتاج فندق في الرياض لمدة 3 ليالٍ.",
            "arabic"
        )
        
        self.assertEqual(response["intent"], "hotel_booking")
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        self.assertIn("hotel_options", response["mock_data"])
        
        logger.info("Hotel booking tests passed")
    
    def test_trip_planning(self):
        """Test complete trip planning functionality"""
        logger.info("Testing trip planning...")
        
        # Test English
        response = self.agent_system.process_message(
            self.session_id,
            "I want to plan a trip to Riyadh for 5 days next month.",
            "english"
        )
        
        self.assertEqual(response["intent"], "trip_planning")
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        self.assertIn("flight", response["mock_data"])
        self.assertIn("hotel", response["mock_data"])
        self.assertIn("total_price", response["mock_data"])
        
        # Test Arabic
        response = self.agent_system.process_message(
            self.session_id,
            "أريد تخطيط رحلة إلى الرياض لمدة 5 أيام الشهر القادم.",
            "arabic"
        )
        
        self.assertEqual(response["intent"], "trip_planning")
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        self.assertIn("flight", response["mock_data"])
        self.assertIn("hotel", response["mock_data"])
        self.assertIn("total_price", response["mock_data"])
        
        logger.info("Trip planning tests passed")
    
    def test_error_handling(self):
        """Test error handling"""
        logger.info("Testing error handling...")
        
        # Test invalid input
        response = self.agent_system.process_message(
            self.session_id,
            "",  # Empty message
            "english"
        )
        
        self.assertFalse(response["success"])
        self.assertIn("error", response["intent"])
        
        # Test unsupported language
        response = self.agent_system.process_message(
            self.session_id,
            "I want to book a flight.",
            "french"  # Unsupported language
        )
        
        self.assertFalse(response["success"])
        self.assertIn("error", response["intent"])
        
        logger.info("Error handling tests passed")
    
    def test_session_management(self):
        """Test session management"""
        logger.info("Testing session management...")
        
        # First request - should create new session
        response = self.agent_system.process_message(
            self.session_id,
            "I want to book a flight to Riyadh.",
            "english"
        )
        
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        
        # Second request - should use existing session
        response = self.agent_system.process_message(
            self.session_id,
            "What are the hotel options in Riyadh?",
            "english"
        )
        
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        
        # Reset session
        self.agent_system.reset_session(self.session_id)
        
        # New request - should create new session
        response = self.agent_system.process_message(
            self.session_id,
            "I want to plan a trip to Jeddah.",
            "english"
        )
        
        self.assertTrue(response["success"])
        self.assertIn("mock_data", response)
        
        logger.info("Session management tests passed")

if __name__ == '__main__':
    unittest.main()

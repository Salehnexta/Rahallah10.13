"""
Comprehensive test for the Trip Planning Assistant Agent System
Tests integration between all agents
"""
import os
import json
import unittest
from dotenv import load_dotenv
from agents.agent_system import AgentSystem
from agents.conversation_lead_agent import ConversationLeadAgent
from agents.flight_booking_agent import FlightBookingAgent
from agents.hotel_booking_agent import HotelBookingAgent
from agents.trip_planning_agent import TripPlanningAgent

# Load environment variables
load_dotenv()

class TestAgentSystem(unittest.TestCase):
    """Test class for Agent System integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.session_id = "test_session_" + str(os.urandom(4).hex())
        self.agent_system = AgentSystem()
    
    def test_conversation_flow(self):
        """Test basic conversation flow"""
        print("\nTesting basic conversation flow...")
        # Simple greeting in English
        response = self.agent_system.process_message(
            self.session_id, 
            "Hello, I would like to plan a trip", 
            "english"
        )
        
        print(f"Response: {response['text'][:150]}...")
        self.assertTrue(response["success"])
        self.assertIn(response["intent"], ["general", "trip_planning"])
    
    def test_flight_booking_intent(self):
        """Test flight booking intent detection"""
        print("\nTesting flight booking intent...")
        # Flight booking request
        response = self.agent_system.process_message(
            self.session_id, 
            "I need to book a flight from Jeddah to Riyadh next week", 
            "english"
        )
        
        print(f"Response: {response['text'][:150]}...")
        self.assertTrue(response["success"])
        self.assertEqual(response["intent"], "flight_booking")
    
    def test_hotel_booking_intent(self):
        """Test hotel booking intent detection"""
        print("\nTesting hotel booking intent...")
        # Hotel booking request
        response = self.agent_system.process_message(
            self.session_id, 
            "I'm looking for a hotel in Riyadh for 3 nights", 
            "english"
        )
        
        print(f"Response: {response['text'][:150]}...")
        self.assertTrue(response["success"])
        self.assertEqual(response["intent"], "hotel_booking")
    
    def test_trip_planning_intent(self):
        """Test trip planning intent detection"""
        print("\nTesting trip planning intent...")
        # Trip planning request
        response = self.agent_system.process_message(
            self.session_id, 
            "I want to plan a complete trip to Jeddah including flights and hotel", 
            "english"
        )
        
        print(f"Response: {response['text'][:150]}...")
        self.assertTrue(response["success"])
        self.assertEqual(response["intent"], "trip_planning")
    
    def test_arabic_support(self):
        """Test Arabic language support"""
        print("\nTesting Arabic language support...")
        # Simple greeting in Arabic
        response = self.agent_system.process_message(
            self.session_id, 
            "مرحبا، أريد حجز رحلة من الرياض إلى جدة", 
            "arabic"
        )
        
        print(f"Response: {response['text'][:150]}...")
        self.assertTrue(response["success"])
        self.assertEqual(response["intent"], "flight_booking")

if __name__ == '__main__':
    unittest.main()

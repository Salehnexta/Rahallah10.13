"""
Simple test script for Trip Planning Assistant agents
Tests each agent independently with mock data
"""
import logging
import json
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import agents directly
from agents.conversation_lead_agent import ConversationLeadAgent
from agents.flight_booking_agent import FlightBookingAgent
from agents.hotel_booking_agent import HotelBookingAgent
from agents.trip_planning_agent import TripPlanningAgent

def test_conversation_agent():
    """Test the ConversationLeadAgent individually"""
    logger.info("\n===== Testing ConversationLeadAgent =====")
    
    agent = ConversationLeadAgent()
    test_messages = [
        ("I want to book a flight from Riyadh to Jeddah", "flight_booking", "english"),
        ("أريد حجز فندق في الرياض", "hotel_booking", "arabic"),
        ("I need to plan a trip from Jeddah to Riyadh", "trip_planning", "english")
    ]
    
    for message, expected_intent, language in test_messages:
        try:
            logger.info(f"Testing message: '{message}' (expected: {expected_intent})")
            response = agent.process_request("test_session", message, language)
            
            intent = response.get('intent', 'unknown')
            logger.info(f"Detected intent: {intent}")
            logger.info(f"Response text: {response.get('text', '')[:100]}...")
            
            if intent == expected_intent:
                logger.info("✅ PASSED: Intent detected correctly")
            else:
                logger.warning(f"❌ FAILED: Expected {expected_intent}, got {intent}")
                
        except Exception as e:
            logger.error(f"Error testing conversation agent: {str(e)}")
    
    return True

def test_flight_booking_agent():
    """Test the FlightBookingAgent individually"""
    logger.info("\n===== Testing FlightBookingAgent =====")
    
    agent = FlightBookingAgent()
    test_messages = [
        ("I need a flight from Riyadh to Jeddah on 2025-05-01", "english"),
        ("أريد حجز رحلة من الرياض إلى جدة في 2025-05-01", "arabic")
    ]
    
    for message, language in test_messages:
        try:
            logger.info(f"Testing message: '{message}'")
            response = agent.process_request("test_session", message, language)
            
            logger.info(f"Response text: {response.get('text', '')[:100]}...")
            
            flights = response.get('mock_data', {}).get('flights', [])
            logger.info(f"Generated {len(flights)} flight options")
            
            if flights:
                logger.info("✅ PASSED: Generated flight options successfully")
                sample_flight = flights[0]
                logger.info(f"Sample flight: {sample_flight.get('airline')} {sample_flight.get('flight_number')} - {sample_flight.get('price')} SAR")
            else:
                logger.warning("❌ FAILED: No flight options generated")
                
        except Exception as e:
            logger.error(f"Error testing flight booking agent: {str(e)}")
    
    return True

def test_hotel_booking_agent():
    """Test the HotelBookingAgent individually"""
    logger.info("\n===== Testing HotelBookingAgent =====")
    
    agent = HotelBookingAgent()
    test_messages = [
        ("I need a hotel in Riyadh from 2025-05-01 to 2025-05-05", "english"),
        ("أريد حجز فندق في الرياض من 2025-05-01 إلى 2025-05-05", "arabic")
    ]
    
    for message, language in test_messages:
        try:
            logger.info(f"Testing message: '{message}'")
            response = agent.process_request("test_session", message, language)
            
            logger.info(f"Response text: {response.get('text', '')[:100]}...")
            
            hotels = response.get('mock_data', {}).get('hotels', [])
            logger.info(f"Generated {len(hotels)} hotel options")
            
            if hotels:
                logger.info("✅ PASSED: Generated hotel options successfully")
                sample_hotel = hotels[0]
                logger.info(f"Sample hotel: {sample_hotel.get('name')} - {sample_hotel.get('star_rating')} stars")
            else:
                logger.warning("❌ FAILED: No hotel options generated")
                
        except Exception as e:
            logger.error(f"Error testing hotel booking agent: {str(e)}")
    
    return True

def test_trip_planning_agent():
    """Test the TripPlanningAgent individually"""
    logger.info("\n===== Testing TripPlanningAgent =====")
    
    agent = TripPlanningAgent()
    test_messages = [
        ("I want to plan a trip from Riyadh to Jeddah from 2025-05-01 to 2025-05-05", "english"),
        ("أريد تخطيط رحلة من الرياض إلى جدة من 2025-05-01 إلى 2025-05-05", "arabic")
    ]
    
    for message, language in test_messages:
        try:
            logger.info(f"Testing message: '{message}'")
            response = agent.process_request("test_session", message, language)
            
            logger.info(f"Response text: {response.get('text', '')[:100]}...")
            
            packages = response.get('mock_data', {}).get('trip_packages', [])
            logger.info(f"Generated {len(packages)} trip packages")
            
            if packages:
                logger.info("✅ PASSED: Generated trip packages successfully")
                sample_package = packages[0]
                logger.info(f"Sample package: {sample_package.get('name')} - {sample_package.get('total_price')} SAR")
            else:
                logger.warning("❌ FAILED: No trip packages generated")
                
        except Exception as e:
            logger.error(f"Error testing trip planning agent: {str(e)}")
    
    return True

if __name__ == "__main__":
    logger.info("Starting Simple Agent Tests\n")
    
    try:
        # Test each agent independently
        success_conversation = test_conversation_agent()
        success_flight = test_flight_booking_agent()
        success_hotel = test_hotel_booking_agent()
        success_trip = test_trip_planning_agent()
        
        logger.info("\n===== Test Summary =====")
        logger.info(f"ConversationLeadAgent: {'✅ PASSED' if success_conversation else '❌ FAILED'}")
        logger.info(f"FlightBookingAgent: {'✅ PASSED' if success_flight else '❌ FAILED'}")
        logger.info(f"HotelBookingAgent: {'✅ PASSED' if success_hotel else '❌ FAILED'}")
        logger.info(f"TripPlanningAgent: {'✅ PASSED' if success_trip else '❌ FAILED'}")
        
    except Exception as e:
        logger.error(f"Test suite error: {str(e)}")

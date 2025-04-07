"""
Basic test script for Trip Planning Assistant agents
Tests each agent independently without LangGraph integration
"""
import logging
import json
import random
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_conversation_agent():
    """Test the ConversationLeadAgent's basic functionalities"""
    logger.info("\n===== Testing ConversationLeadAgent =====")
    from agents.conversation_lead_agent import ConversationLeadAgent
    
    agent = ConversationLeadAgent()
    
    # Test English message for flight booking
    message = "I want to book a flight from Riyadh to Jeddah"
    language = "english"
    logger.info(f"Testing message: '{message}' (Expected: flight_booking)")
    
    try:
        result = agent.process_request("test_session", message, language)
        logger.info(f"Detected intent: {result.get('intent', 'unknown')}")
        logger.info(f"Response: {result.get('text', '')[:100]}...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
    
    # Test Arabic message for hotel booking
    message = "أريد حجز فندق في الرياض"
    language = "arabic"
    logger.info(f"Testing message: '{message}' (Expected: hotel_booking)")
    
    try:
        result = agent.process_request("test_session", message, language)
        logger.info(f"Detected intent: {result.get('intent', 'unknown')}")
        logger.info(f"Response: {result.get('text', '')[:100]}...")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

def test_flight_booking_agent():
    """Test the FlightBookingAgent's basic functionalities"""
    logger.info("\n===== Testing FlightBookingAgent =====")
    from agents.flight_booking_agent import FlightBookingAgent
    
    agent = FlightBookingAgent()
    
    # Test English message
    message = "I need a flight from Riyadh to Jeddah on 2023-12-01"
    language = "english"
    logger.info(f"Testing message: '{message}'")
    
    try:
        result = agent.process_request("test_session", message, language)
        logger.info(f"Response: {result.get('text', '')[:100]}...")
        
        flights = result.get('mock_data', {}).get('flights', [])
        logger.info(f"Generated {len(flights)} flight options")
        
        if flights:
            sample_flight = flights[0]
            logger.info(f"Sample flight: {sample_flight.get('airline')} {sample_flight.get('flight_number')} - {sample_flight.get('price')}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

def test_hotel_booking_agent():
    """Test the HotelBookingAgent's basic functionalities"""
    logger.info("\n===== Testing HotelBookingAgent =====")
    from agents.hotel_booking_agent import HotelBookingAgent
    
    agent = HotelBookingAgent()
    
    # Test English message
    message = "I need a hotel in Riyadh from 2023-12-01 to 2023-12-05"
    language = "english"
    logger.info(f"Testing message: '{message}'")
    
    try:
        result = agent.process_request("test_session", message, language)
        logger.info(f"Response: {result.get('text', '')[:100]}...")
        
        hotels = result.get('mock_data', {}).get('hotels', [])
        logger.info(f"Generated {len(hotels)} hotel options")
        
        if hotels:
            sample_hotel = hotels[0]
            logger.info(f"Sample hotel: {sample_hotel.get('name')} - {sample_hotel.get('star_rating')} stars")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

def test_trip_planning_agent():
    """Test the TripPlanningAgent's basic functionalities"""
    logger.info("\n===== Testing TripPlanningAgent =====")
    from agents.trip_planning_agent import TripPlanningAgent
    
    agent = TripPlanningAgent()
    
    # Test English message
    message = "I want to plan a trip from Riyadh to Jeddah from 2023-12-01 to 2023-12-05"
    language = "english"
    logger.info(f"Testing message: '{message}'")
    
    try:
        result = agent.process_request("test_session", message, language)
        logger.info(f"Response: {result.get('text', '')[:100]}...")
        
        packages = result.get('mock_data', {}).get('trip_packages', [])
        if packages:
            logger.info(f"Generated {len(packages)} trip packages")
            sample_package = packages[0]
            logger.info(f"Sample package: {sample_package.get('name')} - {sample_package.get('total_price')}")
        else:
            logger.info("No trip packages in response")
    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    logger.info("Starting Basic Agent Tests\n")
    
    try:
        # Test each agent independently
        test_conversation_agent()
        test_flight_booking_agent()
        test_hotel_booking_agent()
        test_trip_planning_agent()
        
        logger.info("\n===== All basic tests completed =====")
        
    except Exception as e:
        logger.error(f"Test suite error: {str(e)}")

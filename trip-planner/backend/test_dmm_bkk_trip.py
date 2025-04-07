"""
Test script to search for a trip from DMM (Dammam) to BKK (Bangkok) 3 months from now
"""
import os
import sys
from datetime import datetime, timedelta
from agents.agent_system import AgentSystem

def main():
    # Create a new instance of the agent system
    agent_system = AgentSystem()
    
    # Generate a session ID
    session_id = "dmm_bkk_test"
    
    # Get dates for a 7-day trip starting 3 months from now
    start_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=97)).strftime("%Y-%m-%d")
    
    # Create the search query
    query = f"Find me a trip to Bangkok (BKK) from Dammam (DMM) starting on {start_date} and returning on {end_date} for 2 people"
    print(f"\nQuery: {query}")
    
    # Process the message
    response = agent_system.process_message(session_id, query, "english")
    
    print("\n========== Trip Search Results ==========\n")
    print(response["text"])
    print("\n======================================\n")
    
    if response["success"]:
        print("✅ Trip search successful!")
        print(f"Intent detected: {response['intent']}")
        
        # Print number of trip package options if available
        if "mock_data" in response and "trip_packages" in response["mock_data"]:
            packages = response["mock_data"]["trip_packages"]
            print(f"Found {len(packages)} trip packages")
            
            # Print details of the first package
            if packages:
                first_package = packages[0]
                print("\nFirst Package Details:")
                print(f"Flight: {first_package.get('flight_info', {}).get('airline')} - {first_package.get('flight_info', {}).get('flight_number')}")
                print(f"Hotel: {first_package.get('hotel_info', {}).get('name')} - {first_package.get('hotel_info', {}).get('star_rating')} stars")
                print(f"Total Price: {first_package.get('total_price')} {first_package.get('currency', 'SAR')}")
        else:
            print("No trip package data available")
    else:
        print("❌ Trip search failed!")
    
if __name__ == "__main__":
    main()

"""
Test script to search for a hotel in Jeddah for a 3-night stay
"""
import os
import sys
from datetime import datetime, timedelta
from agents.agent_system import AgentSystem

def main():
    # Create a new instance of the agent system
    agent_system = AgentSystem()
    
    # Generate a session ID
    session_id = "hotel_jeddah_test"
    
    # Get dates for a 3-night stay starting tomorrow
    check_in = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    check_out = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d")
    
    # Create the search query
    query = f"Find me a hotel in Jeddah from {check_in} to {check_out} for 2 people"
    print(f"\nQuery: {query}")
    
    # Process the message
    response = agent_system.process_message(session_id, query, "english")
    
    print("\n========== Hotel Search Results ==========\n")
    print(response["text"])
    print("\n==========================================\n")
    
    if response["success"]:
        print("✅ Hotel search successful!")
        print(f"Intent detected: {response['intent']}")
        
        # Print number of hotel options
        if "mock_data" in response and "hotels" in response["mock_data"]:
            hotels = response["mock_data"]["hotels"]
            print(f"Found {len(hotels)} hotel options")
        else:
            print("No hotel data available")
    else:
        print("❌ Hotel search failed!")
    
if __name__ == "__main__":
    main()

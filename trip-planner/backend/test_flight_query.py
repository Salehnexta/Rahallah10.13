"""
Test script to search for a flight from DMM to RUH for tomorrow
"""
import os
import sys
from datetime import datetime, timedelta
from agents.agent_system import AgentSystem

def main():
    # Create a new instance of the agent system
    agent_system = AgentSystem()
    
    # Generate a session ID
    session_id = "flight_dmm_ruh_test"
    
    # Get tomorrow's date
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    # Create the search query
    query = f"Search for a flight from DMM to RUH on {tomorrow}"
    print(f"\nQuery: {query}")
    
    # Process the message
    response = agent_system.process_message(session_id, query, "english")
    
    print("\n========== Flight Search Results ==========\n")
    print(response["text"])
    print("\n==========================================\n")
    
    if response["success"]:
        print("✅ Flight search successful!")
        print(f"Intent detected: {response['intent']}")
        
        # Print number of flight options
        if "mock_data" in response and "flights" in response["mock_data"]:
            flights = response["mock_data"]["flights"]
            print(f"Found {len(flights)} flight options")
        else:
            print("No flight data available")
    else:
        print("❌ Flight search failed!")
    
if __name__ == "__main__":
    main()

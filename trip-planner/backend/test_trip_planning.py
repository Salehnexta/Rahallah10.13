"""
Test script to plan a complete trip from Riyadh to Jeddah
"""
import os
import sys
from datetime import datetime, timedelta
from agents.agent_system import AgentSystem

def main():
    # Create a new instance of the agent system
    agent_system = AgentSystem()
    
    # Generate a session ID
    session_id = "trip_riyadh_jeddah_test"
    
    # Get dates for a 3-night trip starting next week
    departure_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    return_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    
    # Create the search query
    query = f"Plan a complete trip from Riyadh to Jeddah from {departure_date} to {return_date} for 2 travelers"
    print(f"\nQuery: {query}")
    
    # Process the message
    response = agent_system.process_message(session_id, query, "english")
    
    print("\n========== Trip Planning Results ==========\n")
    print(response["text"])
    print("\n===========================================\n")
    
    if response["success"]:
        print("✅ Trip planning successful!")
        print(f"Intent detected: {response['intent']}")
        
        # Print number of trip package options
        if "mock_data" in response and "trip_packages" in response["mock_data"]:
            packages = response["mock_data"]["trip_packages"]
            print(f"Found {len(packages)} trip packages")
        else:
            print("No trip package data available")
    else:
        print("❌ Trip planning failed!")
    
if __name__ == "__main__":
    main()

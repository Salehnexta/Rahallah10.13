"""
Debug script to catch and display the full error from app.py
"""
import sys
import traceback

try:
    print("Attempting to import app.py...")
    from app import app
    print("Successfully imported app.py!")
except Exception as e:
    print(f"\n\nERROR IMPORTING APP: {e}\n")
    print("Full traceback:")
    traceback.print_exc()
    
    print("\nDependency chain:")
    module_name = str(e).split("'")[-2] if "'" in str(e) else None
    if module_name:
        print(f"Missing module: {module_name}")
        try:
            print(f"Trying to import {module_name} independently...")
            __import__(module_name)
            print(f"Module {module_name} can be imported separately, so the issue is in how app.py is using it.")
        except ImportError as ie:
            print(f"Confirmed: {module_name} is missing. Error: {ie}")

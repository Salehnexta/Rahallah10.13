"""
Simple diagnostic script to check what's breaking app.py
"""
import sys
import traceback

try:
    # Try importing the main app module to see where it fails
    print("Attempting to import app.py...")
    import app
    print("Successfully imported app.py!")
except Exception as e:
    print(f"Error importing app.py: {e}")
    print("\nDetailed traceback:")
    traceback.print_exc()
    
    # If it fails, try some troubleshooting
    print("\n--- Troubleshooting ---")
    
    try:
        from flask import Flask
        print("Flask imported successfully.")
    except ImportError:
        print("Failed to import Flask.")
        
    try:
        from flask_socketio import SocketIO
        print("Flask-SocketIO imported successfully.")
    except ImportError:
        print("Failed to import Flask-SocketIO.")
        
    try:
        import utils.persistence
        print("utils.persistence imported successfully.")
    except ImportError as ie:
        print(f"Failed to import utils.persistence: {ie}")
        
    try:
        print("Checking for other imports in app.py...")
        # Try importing some of the specific modules used in app.py
        import os
        import uuid
        import json
        import logging
        from datetime import datetime
        from flask import jsonify, request, render_template, url_for
        print("Basic modules imported successfully.")
    except ImportError as ie:
        print(f"Failed to import a basic module: {ie}")

print("\nDiagnosis complete.")

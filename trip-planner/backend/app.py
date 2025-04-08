"""
Trip Planning Assistant - Flask Backend
Main application file that sets up routes and handles API requests
"""
import os
import uuid
import json
from flask import Flask, request, jsonify, render_template, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
from dotenv import load_dotenv
import logging
import sys
import io
import time
from datetime import datetime
import structlog
from structlog import get_logger

# Configure logging
structlog.configure(
    processors=[
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO)
)

logger = get_logger()

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent') # Allow all for now, refine later

# Add request/response logging middleware
class RequestResponseLogger:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request_id = str(uuid.uuid4())
        environ['REQUEST_ID'] = request_id
        
        # Log request details
        logger.debug(
            f"[{request_id}] Request received: {environ['REQUEST_METHOD']} {environ['PATH_INFO']}"
        )
        
        # Log request body if present
        content_length = environ.get('CONTENT_LENGTH', '0')
        if int(content_length) > 0:
            body = environ['wsgi.input'].read(int(content_length))
            environ['wsgi.input'] = io.BytesIO(body)
            logger.debug(
                f"[{request_id}] Request body: {body.decode('utf-8')}"
            )
        
        def custom_start_response(status, headers, exc_info=None):
            # Log response details
            logger.debug(
                f"[{request_id}] Response sent: {status}"
            )
            return start_response(status, headers, exc_info)
        
        return self.app(environ, custom_start_response)

# Add the middleware after other middleware
app.wsgi_app = RequestResponseLogger(app.wsgi_app)

# Add request ID middleware
class RequestIDMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['REQUEST_ID'] = str(uuid.uuid4())
        return self.app(environ, start_response)

# Add request ID middleware
app.wsgi_app = RequestIDMiddleware(app.wsgi_app)

# Import agent system
from agents.agent_orchestrator import AgentOrchestrator

# Import utils for data persistence
from utils.persistence import (
    load_trip_data, 
    save_trip_data, 
    add_trip_item, 
    remove_trip_item, 
    set_trip_dates, 
    get_trip_duration,
    state_manager,
    SessionStateManager
)

# In-memory session storage for conversation history
# Format: {session_id: [{"role": "user/assistant", "content": "message"}]}
sessions = {}

# In-memory mapping of session_id to socketio sid
# In a real app, this might use Redis or another shared store
sid_session_map = {}
session_sid_map = {}

# Sample data for attractions
def get_sample_attractions():
    return [
        {
            "id": "attr1",
            "name": "Burj Khalifa",
            "description": "World's tallest building with observation decks offering panoramic views.",
            "category": "Landmark",
            "location": "Downtown Dubai",
            "rating": 4.7,
            "price_level": "$$$",
            "coordinates": {"lat": 25.197197, "lng": 55.274376}
        },
        {
            "id": "attr2",
            "name": "Dubai Mall",
            "description": "Massive shopping center with over 1,300 retail outlets, aquarium, and ice rink.",
            "category": "Shopping",
            "location": "Downtown Dubai",
            "rating": 4.6,
            "price_level": "$$",
            "coordinates": {"lat": 25.197525, "lng": 55.279614}
        },
        {
            "id": "attr3",
            "name": "Palm Jumeirah",
            "description": "Iconic artificial island with luxury hotels, waterparks, and beach clubs.",
            "category": "Landmark",
            "location": "Jumeirah",
            "rating": 4.5,
            "price_level": "$$$",
            "coordinates": {"lat": 25.112350, "lng": 55.138779}
        },
        {
            "id": "attr4",
            "name": "Dubai Creek",
            "description": "Historic waterway separating Deira from Bur Dubai with traditional abra boats.",
            "category": "Culture",
            "location": "Old Dubai",
            "rating": 4.4,
            "price_level": "$",
            "coordinates": {"lat": 25.246721, "lng": 55.329247}
        },
        {
            "id": "attr5",
            "name": "Dubai Miracle Garden",
            "description": "Seasonal outdoor garden with extraordinary floral displays and arrangements.",
            "category": "Nature",
            "location": "Dubailand",
            "rating": 4.3,
            "price_level": "$$",
            "coordinates": {"lat": 25.060944, "lng": 55.243961}
        }
    ]

# ---- Main Routes ----
@app.route('/')
def index():
    """Main application page route."""
    logger.info("Serving index page")
    return render_template('index.html', title='Home')

# ---- API Routes ----

@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    # Test LLM connection
    try:
        from agents.llm_utils import test_llm_connection
        llm_status, message = test_llm_connection()
        llm_health = "connected" if llm_status else "error"
    except Exception as e:
        llm_health = "error"
        message = str(e)
    
    return jsonify({
        "status": "healthy", 
        "version": "1.0.0",
        "llm_status": llm_health,
        "llm_message": message if llm_health == "error" else "LLM connection successful"
    })

@app.route('/api/languages', methods=['GET'])
def supported_languages():
    """Return supported languages"""
    return jsonify({
        "supported_languages": ["en", "ar"],
        "default_language": "en"
    })

# HTMX + Alpine.js Frontend Routes

@app.route('/explore')
def explore():
    """Explore page with attractions"""
    logger.info("Rendering explore page")
    attractions = get_sample_attractions()
    return render_template('explore.html', attractions=attractions)

@app.route('/chat')
def chat_page():
    """Chat page route."""
    logger.info("Rendering chat page")
    # The session_id is now managed client-side by Alpine.js initially
    # Messages are loaded dynamically via WebSocket connection
    return render_template('chat.html')

@app.route('/itinerary')
def itinerary():
    """Itinerary page"""
    logger.info("Rendering itinerary page")
    trip_data = load_trip_data()
    
    trip_details = {
        "start_date": trip_data.get("start_date"),
        "end_date": trip_data.get("end_date"),
        "duration": get_trip_duration()
    }
    
    return render_template('itinerary.html', 
        trip_details=trip_details,
        itinerary_items=trip_data.get("items", [])
    )

# HTMX API Endpoints

@app.route('/api/filter-attractions', methods=['GET'])
def filter_attractions():
    """Filter attractions based on query parameters"""
    query = request.args.get('query', '').lower()
    category = request.args.get('category', '')
    
    logger.info(f"Filtering attractions - query: {query}, category: {category}")
    
    attractions = get_sample_attractions()
    
    # Apply filters
    if query:
        attractions = [a for a in attractions if query in a['name'].lower() or query in a['description'].lower()]
    
    if category and category != 'all':
        attractions = [a for a in attractions if a['category'].lower() == category.lower()]
    
    return render_template('components/attraction_list.html', attractions=attractions)

@app.route('/api/view-details', methods=['GET'])
def view_attraction_details():
    """Get detailed view of an attraction"""
    attraction_id = request.args.get('id')
    
    logger.info(f"Viewing attraction details - id: {attraction_id}")
    
    attractions = get_sample_attractions()
    attraction = next((a for a in attractions if a['id'] == attraction_id), None)
    
    if not attraction:
        return "Attraction not found", 404
    
    return render_template('components/details_content.html', attraction=attraction)

@app.route('/api/close-modal', methods=['GET'])
def close_modal():
    """Close the modal (returns empty response)"""
    return ""

@app.route('/api/add-to-trip', methods=['POST'])
def add_to_trip():
    """Add an attraction to the trip"""
    attraction_id = request.form.get('id')
    
    logger.info(f"Adding attraction to trip - id: {attraction_id}")
    
    attractions = get_sample_attractions()
    attraction = next((a for a in attractions if a['id'] == attraction_id), None)
    
    if not attraction:
        return "Attraction not found", 404
    
    # Add to trip data
    add_trip_item(attraction)
    
    # Return updated trip items
    trip_data = load_trip_data()
    return render_template('components/trip_item_list.html', items=trip_data.get("items", []))

@app.route('/api/remove-from-trip', methods=['POST'])
def remove_from_trip():
    """Remove an attraction from the trip"""
    item_id = request.form.get('id')
    
    logger.info(f"Removing item from trip - id: {item_id}")
    
    # Remove from trip data
    success = remove_trip_item(item_id)
    
    if not success:
        return "Item not found", 404
    
    # Return empty string to allow removal from DOM
    return ""

@app.route('/api/set-trip-dates', methods=['POST'])
def api_set_trip_dates():
    """Set trip start and end dates"""
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    
    logger.info(f"Setting trip dates - start: {start_date}, end: {end_date}")
    
    # Set the dates
    set_trip_dates(start_date, end_date)
    
    # Get the updated trip data
    trip_data = load_trip_data()
    trip_duration = get_trip_duration()
    
    # Render the trip dates component
    return render_template('components/trip_dates.html', 
        trip_start_date=trip_data.get("start_date"),
        trip_end_date=trip_data.get("end_date"),
        trip_duration=trip_duration
    )

@app.route('/api/edit-trip-dates', methods=['GET'])
def edit_trip_dates():
    """Show form to edit trip dates"""
    return render_template('components/trip_dates.html')

# API endpoint to get trip items
@app.route('/api/get-trip-items', methods=['GET'])
def get_trip_items():
    """Get all items in the current trip"""
    try:
        trip_data = load_trip_data()
        items = trip_data.get('items', [])
        
        # Add formatted duration to each item
        for item in items:
            duration = get_trip_duration(item.get('start_date'), item.get('end_date'))
            item['duration'] = duration
        
        logger.info("Successfully retrieved trip items")
        return jsonify({
            'items': items,
            'start_date': trip_data.get('start_date'),
            'end_date': trip_data.get('end_date')
        })
    except Exception as e:
        logger.error(f"Error getting trip items: {str(e)}", exc_info=True)
        return jsonify({'error': 'Failed to retrieve trip items'}), 500

# Initialize LangGraph workflow and state manager
from agents.trip_workflow import create_trip_workflow

trip_workflow = create_trip_workflow()
# State manager for tracking conversation history per session
session_manager = SessionStateManager()

# WebSocket event handlers

@socketio.on('connect')
def handle_connect():
    """
    Handle WebSocket connection
    Client should emit 'join' with session_id after connection.
    """
    logger.info(f"Client connected: {request.sid}")
    # Optionally send a welcome message or wait for join event
    # emit('status', {'message': 'Connected! Please join with your session ID.'}, room=request.sid)

@socketio.on('join')
def handle_join(data):
    """
    Client joins a session room.
    Args:
        data: Dictionary containing {'session_id': 'client-generated-session-id'}
    """
    session_id = data.get('session_id')
    if not session_id:
        logger.warning(f"Client {request.sid} tried to join without session_id")
        emit('error', {'error': 'Session ID is required to join.'}, room=request.sid)
        return

    sid = request.sid
    # Store mapping
    sid_session_map[sid] = session_id
    session_sid_map[session_id] = sid

    # Join the room associated with the session_id
    join_room(session_id)

    logger.info(f"Client {sid} joined session: {session_id}")
    emit('status', {'message': f'Successfully joined session {session_id}.'}, room=sid)

    # Optional: Load history or send welcome message based on session_id
    # current_state = session_manager.get_state(session_id)
    # messages = session_manager.get_messages(session_id)
    # if messages:
    #     emit('history', {'messages': messages}, room=sid) # Client needs to handle 'history' event
    # else:
    #     emit('response', {'response': 'Welcome back!' if current_state else 'Welcome! How can I help?'}, room=sid)


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handle WebSocket disconnection
    """
    sid = request.sid
    logger.info(f"Client disconnected: {sid}")
    # Clean up mapping
    session_id = sid_session_map.pop(sid, None)
    if session_id:
        session_sid_map.pop(session_id, None)
        leave_room(session_id) # Leave the session-specific room
        logger.info(f"Client {sid} removed from session {session_id}")
    else:
        logger.warning(f"Disconnected client {sid} had no associated session_id")


@socketio.on('chat_message')
def handle_chat_message(data):
    """
    Handle WebSocket messages using LangGraph state management.
    Args:
        data: Dictionary containing message data, e.g.,
              {'session_id': 'session-id', 'message': 'User message'}
    """
    session_id = data.get('session_id')
    message = data.get('message')
    sid = request.sid # Use SID from the current connection

    if not session_id:
        logger.warning(f"Received message without session_id from {sid}")
        emit('error', {'error': 'Session ID missing in message.'}, room=sid)
        return
        
    # Verify SID matches the session ID map (security measure)
    if sid_session_map.get(sid) != session_id:
         logger.error(f"SID/Session mismatch! SID: {sid}, Mapped SID: {session_sid_map.get(session_id)}, Expected Session: {sid_session_map.get(sid)}, Received Session: {session_id}")
         emit('error', {'error': 'Session ID mismatch.'}, room=sid)
         # Optionally disconnect: disconnect(sid)
         return

    if not message:
        logger.warning(f"Received empty message from session {session_id} ({sid})")
        emit('error', {'error': 'Message cannot be empty.'}, room=sid)
        return

    logger.info(f"Received message via WebSocket for session {session_id} ({sid}): {message}")

    try:
        # Retrieve current state or initialize if new session
        # LangGraph manages state via config, SessionStateManager might be redundant here
        # if needed for other purposes
        # current_state = session_manager.get_state(session_id)
        # logger.debug(f"Current state for session {session_id}: {current_state}")

        # Invoke the workflow
        inputs = {"input": message}
        # Crucial: Pass session_id in config for LangGraph's persistence
        config = {"configurable": {"session_id": session_id}}

        logger.debug(f"Invoking workflow for session {session_id} with input: {message}")
        # Use stream for potential real-time updates, or invoke for single response
        # Using invoke for simplicity now:
        final_state = trip_workflow.invoke(inputs, config=config)
        logger.debug(f"Workflow final state for session {session_id}: {final_state}")

        # Extract the last assistant message from the final state
        # Adjust based on your specific LangGraph output structure
        assistant_response = ""
        if isinstance(final_state, dict) and "agent" in final_state:
            agent_state = final_state.get("agent", {})
            if isinstance(agent_state, dict) and "messages" in agent_state:
                 # Find the last AIMessage
                 for msg in reversed(agent_state["messages"]):
                     if hasattr(msg, 'type') and msg.type == 'ai':
                         assistant_response = msg.content
                         break

        if not assistant_response:
             # Fallback or check other parts of final_state if structure differs
             assistant_response = final_state.get("output", "Sorry, I couldn't process that.")
             if isinstance(assistant_response, list): # Handle list outputs if necessary
                 assistant_response = " ".join(map(str, assistant_response))


        logger.info(f"Sending response to session {session_id} ({sid}): {assistant_response}")

        # Send the response back to the specific client
        emit('response', {
            'response': assistant_response,
            'session_id': session_id # Echo session_id back if needed
        }, room=sid) # Target the specific client connection

    except Exception as e:
        logger.exception(f"Error processing WebSocket message for session {session_id} ({sid}): {e}")
        emit('error', {'error': f'An internal error occurred: {e}'}, room=sid)


@socketio.on('reset_session')
def handle_reset_session(data):
    """
    Handle session reset request via WebSocket
    Args:
        data: Dictionary containing {'session_id': 'session-id-to-reset'}
    """
    session_id = data.get('session_id')
    sid = request.sid

    if not session_id:
        logger.warning(f"Reset request without session_id from {sid}")
        emit('error', {'error': 'Session ID missing for reset.'}, room=sid)
        return
        
    # Verify SID matches the session ID map
    if sid_session_map.get(sid) != session_id:
         logger.error(f"SID/Session mismatch on reset! SID: {sid}, Expected Session: {sid_session_map.get(sid)}, Received Session: {session_id}")
         emit('error', {'error': 'Session ID mismatch for reset.'}, room=sid)
         return

    logger.info(f"Resetting session: {session_id} requested by client {sid}")

    try:
        # Clear state in LangGraph's persistence layer
        # This depends on how LangGraph persistence is configured (e.g., RedisCheckpointer)
        # Assuming a method exists or needs to be implemented in SessionStateManager
        # For RedisCheckpointer, deleting the checkpoint might be the way:
        if hasattr(trip_workflow.checkpointer, 'config_map') and session_id in trip_workflow.checkpointer.config_map:
             # This is hypothetical - check LangGraph RedisCheckpointer specifics
             # checkpoint_key = trip_workflow.checkpointer._get_key(config={"configurable": {"session_id": session_id}})
             # trip_workflow.checkpointer.redis_client.delete(checkpoint_key)
             # A simpler approach might be needed, or LangGraph might offer a reset API.
             # For now, just log the intent. Need to investigate LangGraph reset.
             logger.info(f"Attempting to reset LangGraph state for session {session_id} (Implementation needed)")
             # TODO: Implement actual LangGraph state reset based on checkpointer used.

        # Clear any local state if SessionStateManager is still used
        session_manager.clear_state(session_id)

        logger.info(f"Session {session_id} reset successfully.")
        emit('status', {'message': 'Session reset successfully.'}, room=sid)
        # Optionally emit a new welcome message
        emit('response', {'response': 'Session has been reset. How can I help you start a new plan?'}, room=sid)

    except Exception as e:
        logger.exception(f"Error resetting session {session_id}: {e}")
        emit('error', {'error': f'Failed to reset session: {e}'}, room=sid)


if __name__ == '__main__':
    logger.info("Starting Flask application with SocketIO")
    # Use eventlet or gevent for production SocketIO
    # socketio.run(app, debug=True, host='0.0.0.0', port=5000) # Example for running
    socketio.run(app, debug=True) # Default run for development

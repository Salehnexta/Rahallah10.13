"""
Agent System for Trip Planning Assistant
Orchestrates the different agents and manages the conversation flow
"""
import logging
import re
from .conversation_lead_agent import ConversationLeadAgent
from .flight_booking_agent import FlightBookingAgent
from .hotel_booking_agent import HotelBookingAgent
from .trip_planning_agent import TripPlanningAgent

# Configure logging
logger = logging.getLogger(__name__)

class AgentSystem:
    """Agent System class for orchestrating the different agents"""
    
    def __init__(self):
        """Initialize the Agent System with all the specialized agents"""
        self.conversation_lead = ConversationLeadAgent()
        self.flight_booking = FlightBookingAgent()
        self.hotel_booking = HotelBookingAgent()
        self.trip_planning = TripPlanningAgent()
        
        # Session state
        self.sessions = {}
        
        logger.info("Agent System initialized with all specialized agents")
    
    def process_message(self, session_id, message, language="english"):
        """
        Process a user message and generate a response using the appropriate agent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language of the conversation (english or arabic)
            
        Returns:
            dict: Response with text and metadata
        """
        try:
            # Initialize session if it doesn't exist
            if session_id not in self.sessions:
                self.sessions[session_id] = {
                    "conversation_history": [],
                    "flight_options": [],
                    "hotel_options": [],
                    "language": language
                }
            
            # Update session language if provided
            if language:
                self.sessions[session_id]["language"] = language
            else:
                language = self.sessions[session_id]["language"]
            
            # Add user message to conversation history
            self.sessions[session_id]["conversation_history"].append({
                "role": "user",
                "content": message
            })
            
            # Process message with Conversation Lead Agent to determine intent
            lead_response = self.conversation_lead.process_message(message, language)
            intent = lead_response["intent"]
            
            # Process based on intent
            if intent == "flight_booking":
                response = self._handle_flight_booking(session_id, message, language)
            elif intent == "hotel_booking":
                response = self._handle_hotel_booking(session_id, message, language)
            elif intent == "trip_planning":
                response = self._handle_trip_planning(session_id, message, language)
            else:
                # General conversation
                response = {
                    "text": lead_response["text"],
                    "intent": "general"
                }
            
            # Add assistant response to conversation history
            self.sessions[session_id]["conversation_history"].append({
                "role": "assistant",
                "content": response["text"]
            })
            
            return response
        except Exception as e:
            logger.error(f"Error in Agent System: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your request. Please try again.",
                "intent": "error"
            }
    
    def _handle_flight_booking(self, session_id, message, language):
        """
        Handle flight booking intent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language of the conversation
            
        Returns:
            dict: Response with flight options
        """
        try:
            # Extract flight parameters from the message
            params = self._extract_flight_params(message)
            
            if params["origin"] and params["destination"] and params["date"]:
                # Generate flight options
                flight_response = self.flight_booking.generate_flight_options(
                    origin=params["origin"],
                    destination=params["destination"],
                    date=params["date"],
                    passengers=params["passengers"],
                    class_type=params["class_type"],
                    language=language
                )
                
                # Store flight options in session
                self.sessions[session_id]["flight_options"] = flight_response["flight_options"]
                
                return {
                    "text": flight_response["text"],
                    "intent": "flight_booking",
                    "flight_options": flight_response["flight_options"]
                }
            else:
                # Not enough information, use conversation lead response
                lead_response = self.conversation_lead.process_message(
                    f"I need more information to book a flight. Please tell me your origin, destination, and travel date. {message}",
                    language
                )
                
                return {
                    "text": lead_response["text"],
                    "intent": "flight_booking_info_needed"
                }
        except Exception as e:
            logger.error(f"Error handling flight booking: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your flight booking request.",
                "intent": "error"
            }
    
    def _handle_hotel_booking(self, session_id, message, language):
        """
        Handle hotel booking intent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language of the conversation
            
        Returns:
            dict: Response with hotel options
        """
        try:
            # Extract hotel parameters from the message
            params = self._extract_hotel_params(message)
            
            if params["city"] and params["check_in"] and params["check_out"]:
                # Generate hotel options
                hotel_response = self.hotel_booking.generate_hotel_options(
                    city=params["city"],
                    check_in=params["check_in"],
                    check_out=params["check_out"],
                    guests=params["guests"],
                    rooms=params["rooms"],
                    language=language
                )
                
                # Store hotel options in session
                self.sessions[session_id]["hotel_options"] = hotel_response["hotel_options"]
                
                return {
                    "text": hotel_response["text"],
                    "intent": "hotel_booking",
                    "hotel_options": hotel_response["hotel_options"]
                }
            else:
                # Not enough information, use conversation lead response
                lead_response = self.conversation_lead.process_message(
                    f"I need more information to book a hotel. Please tell me the city, check-in date, and check-out date. {message}",
                    language
                )
                
                return {
                    "text": lead_response["text"],
                    "intent": "hotel_booking_info_needed"
                }
        except Exception as e:
            logger.error(f"Error handling hotel booking: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your hotel booking request.",
                "intent": "error"
            }
    
    def _handle_trip_planning(self, session_id, message, language):
        """
        Handle trip planning intent
        
        Args:
            session_id (str): Session identifier
            message (str): User message
            language (str): Language of the conversation
            
        Returns:
            dict: Response with trip plan
        """
        try:
            # Check if we have flight and hotel options
            flight_options = self.sessions[session_id].get("flight_options", [])
            hotel_options = self.sessions[session_id].get("hotel_options", [])
            
            # Extract trip parameters from the message
            params = self._extract_trip_params(message)
            
            # If we don't have flight or hotel options, try to extract them from the message
            if not flight_options:
                flight_params = self._extract_flight_params(message)
                if flight_params["origin"] and flight_params["destination"] and flight_params["date"]:
                    flight_response = self.flight_booking.generate_flight_options(
                        origin=flight_params["origin"],
                        destination=flight_params["destination"],
                        date=flight_params["date"],
                        passengers=flight_params["passengers"],
                        class_type=flight_params["class_type"],
                        language=language
                    )
                    flight_options = flight_response["flight_options"]
                    self.sessions[session_id]["flight_options"] = flight_options
            
            if not hotel_options:
                hotel_params = self._extract_hotel_params(message)
                if hotel_params["city"] and hotel_params["check_in"] and hotel_params["check_out"]:
                    hotel_response = self.hotel_booking.generate_hotel_options(
                        city=hotel_params["city"],
                        check_in=hotel_params["check_in"],
                        check_out=hotel_params["check_out"],
                        guests=hotel_params["guests"],
                        rooms=hotel_params["rooms"],
                        language=language
                    )
                    hotel_options = hotel_response["hotel_options"]
                    self.sessions[session_id]["hotel_options"] = hotel_options
            
            # If we have enough information, generate a trip plan
            if flight_options or hotel_options:
                trip_response = self.trip_planning.generate_trip_plan(
                    flight_options=flight_options,
                    hotel_options=hotel_options,
                    duration=params["duration"],
                    interests=params["interests"],
                    language=language
                )
                
                return {
                    "text": trip_response["text"],
                    "intent": "trip_planning",
                    "trip_plan": trip_response["trip_plan"]
                }
            else:
                # Not enough information, use conversation lead response
                lead_response = self.conversation_lead.process_message(
                    f"I need more information to plan your trip. Please tell me your destination, travel dates, and any specific interests. {message}",
                    language
                )
                
                return {
                    "text": lead_response["text"],
                    "intent": "trip_planning_info_needed"
                }
        except Exception as e:
            logger.error(f"Error handling trip planning: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error processing your trip planning request.",
                "intent": "error"
            }
    
    def _extract_flight_params(self, message):
        """
        Extract flight parameters from a message
        
        Args:
            message (str): User message
            
        Returns:
            dict: Flight parameters
        """
        # Default values
        params = {
            "origin": None,
            "destination": None,
            "date": None,
            "passengers": 1,
            "class_type": "economy"
        }
        
        # Extract origin
        origin_match = re.search(r'from\s+([A-Za-z\s]+?)(?:\s+to|\s+on|\s+for|\s+in|\s+with|\s+\d|\s*$)', message, re.IGNORECASE)
        if origin_match:
            params["origin"] = origin_match.group(1).strip()
        
        # Extract destination
        dest_match = re.search(r'to\s+([A-Za-z\s]+?)(?:\s+from|\s+on|\s+for|\s+in|\s+with|\s+\d|\s*$)', message, re.IGNORECASE)
        if dest_match:
            params["destination"] = dest_match.group(1).strip()
        
        # Extract date
        date_match = re.search(r'(?:on|for)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})', message, re.IGNORECASE)
        if date_match:
            params["date"] = date_match.group(1).strip()
        
        # Extract passengers
        passengers_match = re.search(r'(\d+)\s+(?:passenger|passengers|people|person|adult|adults)', message, re.IGNORECASE)
        if passengers_match:
            params["passengers"] = int(passengers_match.group(1))
        
        # Extract class
        if re.search(r'business\s+class', message, re.IGNORECASE):
            params["class_type"] = "business"
        elif re.search(r'first\s+class', message, re.IGNORECASE):
            params["class_type"] = "first"
        elif re.search(r'economy\s+class', message, re.IGNORECASE):
            params["class_type"] = "economy"
        
        return params
    
    def _extract_hotel_params(self, message):
        """
        Extract hotel parameters from a message
        
        Args:
            message (str): User message
            
        Returns:
            dict: Hotel parameters
        """
        # Default values
        params = {
            "city": None,
            "check_in": None,
            "check_out": None,
            "guests": 2,
            "rooms": 1
        }
        
        # Extract city
        city_match = re.search(r'(?:in|at|to)\s+([A-Za-z\s]+?)(?:\s+from|\s+on|\s+for|\s+with|\s+\d|\s*$)', message, re.IGNORECASE)
        if city_match:
            params["city"] = city_match.group(1).strip()
        
        # Extract check-in date
        check_in_match = re.search(r'(?:from|check[\s-]in)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})', message, re.IGNORECASE)
        if check_in_match:
            params["check_in"] = check_in_match.group(1).strip()
        
        # Extract check-out date
        check_out_match = re.search(r'(?:to|until|check[\s-]out)\s+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})', message, re.IGNORECASE)
        if check_out_match:
            params["check_out"] = check_out_match.group(1).strip()
        
        # Extract guests
        guests_match = re.search(r'(\d+)\s+(?:guest|guests|people|person|adult|adults)', message, re.IGNORECASE)
        if guests_match:
            params["guests"] = int(guests_match.group(1))
        
        # Extract rooms
        rooms_match = re.search(r'(\d+)\s+(?:room|rooms)', message, re.IGNORECASE)
        if rooms_match:
            params["rooms"] = int(rooms_match.group(1))
        
        return params
    
    def _extract_trip_params(self, message):
        """
        Extract trip parameters from a message
        
        Args:
            message (str): User message
            
        Returns:
            dict: Trip parameters
        """
        # Default values
        params = {
            "duration": 3,
            "interests": []
        }
        
        # Extract duration
        duration_match = re.search(r'(\d+)\s+(?:day|days|night|nights)', message, re.IGNORECASE)
        if duration_match:
            params["duration"] = int(duration_match.group(1))
        
        # Extract interests (simple keyword matching)
        interests_keywords = [
            "history", "culture", "museum", "art", "architecture", "food", "cuisine", 
            "shopping", "beach", "nature", "hiking", "adventure", "family", "luxury", 
            "budget", "religious", "sightseeing", "relaxation", "sports"
        ]
        
        for keyword in interests_keywords:
            if re.search(r'\b' + keyword + r'\b', message, re.IGNORECASE):
                params["interests"].append(keyword)
        
        return params

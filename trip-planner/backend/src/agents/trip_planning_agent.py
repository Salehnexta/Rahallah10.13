"""
Trip Planning Agent for Trip Planning Assistant
Combines flight and hotel information into complete travel packages
"""
import logging
import json
import random
from .langchain_utils import create_basic_chain

# Configure logging
logger = logging.getLogger(__name__)

# System prompt for the Trip Planning Agent
SYSTEM_PROMPT = """
You are the Trip Planning Agent for a Saudi-focused Trip Planning Assistant.
Your role is to combine flight and hotel information into complete travel packages.

When generating trip plans:
1. Create coherent travel packages that combine flights and hotels
2. Add suggestions for activities, attractions, and dining options
3. Focus on Saudi destinations and cultural experiences
4. Include practical travel tips specific to Saudi Arabia
5. Organize information in a clear, day-by-day itinerary format
6. Highlight cultural, historical, and natural attractions

Important guidelines:
- Ensure the flight and hotel details align (dates, destinations)
- Include both popular tourist sites and off-the-beaten-path experiences
- Provide realistic time estimates for activities and transportation
- Include cultural context and etiquette tips for Saudi Arabia
- Support both English and Arabic responses
- NEVER claim these are real bookable packages - they are fictional examples
- Include practical information about local transportation, weather, and customs

Format the response as a complete travel itinerary with clear sections for transportation,
accommodation, daily activities, and practical tips.
"""

# Popular attractions by city
ATTRACTIONS = {
    "Riyadh": [
        {"name": "Kingdom Centre Tower", "type": "Modern Architecture", "duration": "2 hours"},
        {"name": "National Museum of Saudi Arabia", "type": "Museum", "duration": "3 hours"},
        {"name": "Diriyah", "type": "Historical Site", "duration": "4 hours"},
        {"name": "Al Masmak Fortress", "type": "Historical Site", "duration": "2 hours"},
        {"name": "Riyadh Zoo", "type": "Family", "duration": "3 hours"},
        {"name": "Edge of the World", "type": "Natural", "duration": "6 hours"},
        {"name": "King Abdullah Park", "type": "Park", "duration": "2 hours"}
    ],
    "Jeddah": [
        {"name": "Al-Balad (Historic Jeddah)", "type": "Historical Site", "duration": "4 hours"},
        {"name": "King Fahd Fountain", "type": "Landmark", "duration": "1 hour"},
        {"name": "Jeddah Corniche", "type": "Waterfront", "duration": "3 hours"},
        {"name": "Fakieh Aquarium", "type": "Family", "duration": "2 hours"},
        {"name": "Floating Mosque", "type": "Religious Site", "duration": "1 hour"},
        {"name": "Red Sea Mall", "type": "Shopping", "duration": "3 hours"}
    ],
    "Dammam": [
        {"name": "King Abdulaziz Center for World Culture (Ithra)", "type": "Cultural", "duration": "4 hours"},
        {"name": "Dammam Corniche", "type": "Waterfront", "duration": "2 hours"},
        {"name": "Al Shatea Mall", "type": "Shopping", "duration": "3 hours"},
        {"name": "Heritage Village", "type": "Cultural", "duration": "2 hours"},
        {"name": "Half Moon Bay", "type": "Beach", "duration": "4 hours"}
    ],
    "Medina": [
        {"name": "Al-Masjid an-Nabawi (Prophet's Mosque)", "type": "Religious Site", "duration": "3 hours"},
        {"name": "Quba Mosque", "type": "Religious Site", "duration": "2 hours"},
        {"name": "Al-Baqi Cemetery", "type": "Historical Site", "duration": "1 hour"},
        {"name": "Mount Uhud", "type": "Historical Site", "duration": "3 hours"},
        {"name": "Masjid al-Qiblatain", "type": "Religious Site", "duration": "1 hour"}
    ],
    "Mecca": [
        {"name": "Masjid al-Haram (Grand Mosque)", "type": "Religious Site", "duration": "4 hours"},
        {"name": "Jabal al-Nour", "type": "Religious Site", "duration": "3 hours"},
        {"name": "Abraj Al-Bait (Makkah Clock Royal Tower)", "type": "Modern Architecture", "duration": "2 hours"},
        {"name": "Makkah Museum", "type": "Museum", "duration": "2 hours"}
    ],
    "Taif": [
        {"name": "Al Shafa Mountain", "type": "Natural", "duration": "4 hours"},
        {"name": "Taif Rose Farms", "type": "Cultural", "duration": "3 hours"},
        {"name": "Al Rudaf Park", "type": "Park", "duration": "2 hours"},
        {"name": "Shubra Palace", "type": "Historical Site", "duration": "2 hours"},
        {"name": "Al Hada Mountain", "type": "Natural", "duration": "3 hours"}
    ],
    "Abha": [
        {"name": "Abha Palace Park", "type": "Park", "duration": "2 hours"},
        {"name": "Green Mountain", "type": "Natural", "duration": "3 hours"},
        {"name": "Abha Dam Lake", "type": "Natural", "duration": "2 hours"},
        {"name": "Rijal Almaa Village", "type": "Cultural", "duration": "4 hours"},
        {"name": "Cable Car", "type": "Activity", "duration": "2 hours"}
    ]
}

# Restaurants by city
RESTAURANTS = {
    "Riyadh": [
        {"name": "Najd Village", "cuisine": "Saudi Traditional", "price_range": "$$"},
        {"name": "The Globe", "cuisine": "International", "price_range": "$$$"},
        {"name": "Lusin", "cuisine": "Armenian", "price_range": "$$$"},
        {"name": "Section-B", "cuisine": "Steakhouse", "price_range": "$$"},
        {"name": "Takya", "cuisine": "Modern Saudi", "price_range": "$$$"}
    ],
    "Jeddah": [
        {"name": "Al Nakheel", "cuisine": "Saudi Traditional", "price_range": "$$"},
        {"name": "Twina", "cuisine": "Seafood", "price_range": "$$$"},
        {"name": "Byblos", "cuisine": "Lebanese", "price_range": "$$"},
        {"name": "Mataam Al Sharq", "cuisine": "Saudi Traditional", "price_range": "$$"},
        {"name": "The Butcher Shop & Grill", "cuisine": "Steakhouse", "price_range": "$$$"}
    ],
    "Dammam": [
        {"name": "Café Bateel", "cuisine": "International", "price_range": "$$"},
        {"name": "Maharaja", "cuisine": "Indian", "price_range": "$$"},
        {"name": "Yildizlar", "cuisine": "Turkish", "price_range": "$$"},
        {"name": "Al Danah", "cuisine": "Seafood", "price_range": "$$$"},
        {"name": "Zaatar w Zeit", "cuisine": "Lebanese", "price_range": "$"}
    ]
}

# Travel tips for Saudi Arabia
TRAVEL_TIPS = [
    "Dress modestly in public places. Women should cover shoulders and knees, men should avoid shorts.",
    "Public displays of affection are not acceptable in Saudi culture.",
    "The weekend in Saudi Arabia is Friday and Saturday, with many businesses closed on Friday mornings.",
    "Prayer times occur five times daily, and many shops and restaurants close briefly during these times.",
    "Tipping (10-15%) is appreciated but not mandatory in restaurants and for services.",
    "Always carry some cash as not all places accept credit cards, especially in smaller establishments.",
    "Download the Absher app for government services and the Wasel app for navigation.",
    "Non-Muslims are not permitted to enter Mecca and parts of Medina.",
    "Alcohol is prohibited throughout Saudi Arabia.",
    "The best times to visit are October to April when temperatures are milder.",
    "Arabic is the official language, but English is widely spoken in tourist areas and major cities.",
    "Saudi Arabia uses the Hijri (Islamic) calendar for official purposes, which is different from the Gregorian calendar."
]

class TripPlanningAgent:
    """Trip Planning Agent class"""
    
    def __init__(self):
        """Initialize the Trip Planning Agent"""
        self.chain = create_basic_chain(SYSTEM_PROMPT)
        logger.info("Trip Planning Agent initialized")
    
    def generate_trip_plan(self, flight_options, hotel_options, duration, interests=None, language="english"):
        """
        Generate a complete trip plan based on flight and hotel options
        
        Args:
            flight_options (list): List of flight options
            hotel_options (list): List of hotel options
            duration (int): Trip duration in days
            interests (list): User interests (optional)
            language (str): Language for the response (english, arabic)
            
        Returns:
            dict: Response with trip plan
        """
        try:
            # Select a flight and hotel option
            selected_flight = flight_options[0] if flight_options else None
            selected_hotel = hotel_options[0] if hotel_options else None
            
            # Generate itinerary
            itinerary = self._generate_itinerary(selected_flight, selected_hotel, duration, interests)
            
            # Format the prompt for the LLM
            prompt = f"""
            Generate a complete trip plan based on the following information:
            
            Flight: {json.dumps(selected_flight, indent=2) if selected_flight else "No flight information provided"}
            
            Hotel: {json.dumps(selected_hotel, indent=2) if selected_hotel else "No hotel information provided"}
            
            Itinerary: {json.dumps(itinerary, indent=2)}
            
            Duration: {duration} days
            
            Interests: {', '.join(interests) if interests else "General tourism"}
            
            Include practical travel tips specific to Saudi Arabia.
            
            Respond in {language}.
            """
            
            # Process through LangChain
            response_text = self.chain.invoke({"input": prompt})
            
            return {
                "text": response_text,
                "trip_plan": {
                    "flight": selected_flight,
                    "hotel": selected_hotel,
                    "itinerary": itinerary
                }
            }
        except Exception as e:
            logger.error(f"Error in Trip Planning Agent: {str(e)}")
            return {
                "text": "I'm sorry, I encountered an error generating a trip plan.",
                "trip_plan": {}
            }
    
    def _generate_itinerary(self, flight, hotel, duration, interests=None):
        """
        Generate a day-by-day itinerary
        
        Args:
            flight (dict): Selected flight option
            hotel (dict): Selected hotel option
            duration (int): Trip duration in days
            interests (list): User interests (optional)
            
        Returns:
            dict: Itinerary with daily activities
        """
        # Determine destination city
        if flight and "destination" in flight and "city" in flight["destination"]:
            city = flight["destination"]["city"]
        elif hotel and "location" in hotel:
            city = hotel["location"].split()[-1]  # Extract city from location
        else:
            city = random.choice(list(ATTRACTIONS.keys()))
        
        # Get attractions for the city or use Riyadh as default
        city_attractions = ATTRACTIONS.get(city, ATTRACTIONS["Riyadh"])
        
        # Get restaurants for the city or use Riyadh as default
        city_restaurants = RESTAURANTS.get(city, RESTAURANTS["Riyadh"])
        
        # Filter attractions based on interests if provided
        if interests:
            # Simple keyword matching for interests
            filtered_attractions = []
            for attraction in city_attractions:
                if any(interest.lower() in attraction["name"].lower() or 
                       interest.lower() in attraction["type"].lower() 
                       for interest in interests):
                    filtered_attractions.append(attraction)
            
            # If we have enough filtered attractions, use them
            if len(filtered_attractions) >= duration * 2:
                city_attractions = filtered_attractions
        
        # Shuffle attractions and restaurants for variety
        random.shuffle(city_attractions)
        random.shuffle(city_restaurants)
        
        # Select travel tips
        selected_tips = random.sample(TRAVEL_TIPS, min(4, len(TRAVEL_TIPS)))
        
        # Generate daily itinerary
        days = []
        for day in range(1, duration + 1):
            # For first day, include arrival if flight is provided
            if day == 1 and flight:
                morning_activity = {
                    "time": "Morning",
                    "activity": f"Arrival at {flight['destination']['airport']} ({flight['destination']['code']})",
                    "description": f"Arrive on flight {flight['flight_number']} at {flight['arrival'].split()[1]}. Transfer to hotel and check-in."
                }
            else:
                # Get a morning attraction
                attraction_index = (day - 1) * 3 % len(city_attractions)
                morning_activity = {
                    "time": "Morning",
                    "activity": city_attractions[attraction_index]["name"],
                    "description": f"Visit {city_attractions[attraction_index]['name']} ({city_attractions[attraction_index]['type']}). Estimated duration: {city_attractions[attraction_index]['duration']}."
                }
            
            # Get an afternoon attraction
            attraction_index = (day - 1) * 3 + 1 % len(city_attractions)
            afternoon_activity = {
                "time": "Afternoon",
                "activity": city_attractions[attraction_index]["name"],
                "description": f"Explore {city_attractions[attraction_index]['name']} ({city_attractions[attraction_index]['type']}). Estimated duration: {city_attractions[attraction_index]['duration']}."
            }
            
            # Get a restaurant for dinner
            restaurant_index = (day - 1) % len(city_restaurants)
            evening_activity = {
                "time": "Evening",
                "activity": f"Dinner at {city_restaurants[restaurant_index]['name']}",
                "description": f"Enjoy {city_restaurants[restaurant_index]['cuisine']} cuisine at {city_restaurants[restaurant_index]['name']} (Price range: {city_restaurants[restaurant_index]['price_range']})."
            }
            
            # For last day, include departure if flight is provided
            if day == duration and flight:
                # Replace afternoon or evening activity with departure
                if random.random() > 0.5:
                    afternoon_activity = {
                        "time": "Afternoon",
                        "activity": f"Departure from {flight['origin']['airport']} ({flight['origin']['code']})",
                        "description": f"Check-out from hotel. Transfer to airport for return flight."
                    }
                else:
                    evening_activity = {
                        "time": "Evening",
                        "activity": f"Departure from {flight['origin']['airport']} ({flight['origin']['code']})",
                        "description": f"Check-out from hotel. Transfer to airport for return flight."
                    }
            
            # Create day itinerary
            day_itinerary = {
                "day": day,
                "activities": [morning_activity, afternoon_activity, evening_activity]
            }
            
            days.append(day_itinerary)
        
        # Create complete itinerary
        itinerary = {
            "destination": city,
            "duration": duration,
            "days": days,
            "travel_tips": selected_tips
        }
        
        return itinerary

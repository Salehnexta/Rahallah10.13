"""
Trip Planning Assistant - Persistence Utilities
Handles session state and caching
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
import uuid

# Try importing Redis, but don't make it a hard requirement if not configured
try:
    from redis import Redis
    from redis.exceptions import ConnectionError
    REDIS_AVAILABLE = True
except ImportError:
    Redis = None # type: ignore
    ConnectionError = None # type: ignore
    REDIS_AVAILABLE = False 

logger = logging.getLogger(__name__)

# Initialize the state manager as a global instance
# This needs to be before the function definitions that reference it
state_manager = None  # Will be initialized after class definitions

# --- Trip Data Functions ---

def load_trip_data() -> Dict[str, Any]:
    """
    Load the trip data from a persistent store.
    Returns an empty dict if no data exists.
    """
    try:
        # First check if we have trip data in state manager
        if state_manager:
            trip_state = state_manager.get_state("trip_data")
            if trip_state:
                logger.info("Loaded trip data from state manager")
                return trip_state

        # Fall back to JSON file if needed
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'trip.json')
        if os.path.exists(data_path):
            with open(data_path, 'r') as f:
                data = json.load(f)
                logger.info(f"Loaded trip data from file: {data_path}")
                return data
    except Exception as e:
        logger.error(f"Error loading trip data: {e}")
    
    # Return default data if nothing exists
    logger.info("No existing trip data found, using defaults")
    return {
        "start_date": None,
        "end_date": None,
        "items": []
    }

def save_trip_data(trip_data: Dict[str, Any]) -> bool:
    """
    Save the trip data to a persistent store.
    Returns True if successful, False otherwise.
    """
    try:
        # First save to state manager if available
        if state_manager:
            state_manager.set_state("trip_data", trip_data)
            logger.info("Saved trip data to state manager")
        
        # Also save to JSON file for backup/persistence
        data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'trip.json')
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(data_path), exist_ok=True)
        
        with open(data_path, 'w') as f:
            json.dump(trip_data, f, indent=2)
            logger.info(f"Saved trip data to file: {data_path}")
        
        return True
    except Exception as e:
        logger.error(f"Error saving trip data: {e}")
        return False

def add_trip_item(item: Dict[str, Any]) -> str:
    """
    Add an item to the trip plan.
    Returns the ID of the added item.
    """
    try:
        trip_data = load_trip_data()
        
        # Generate a unique ID if one doesn't exist
        if "id" not in item:
            item["id"] = str(uuid.uuid4())
        
        # Add timestamp
        item["added_at"] = datetime.now().isoformat()
        
        # Add to items list
        if "items" not in trip_data:
            trip_data["items"] = []
        
        trip_data["items"].append(item)
        
        # Save updated data
        save_trip_data(trip_data)
        
        logger.info(f"Added item to trip: {item['id']}")
        return item["id"]
    except Exception as e:
        logger.error(f"Error adding trip item: {e}")
        return ""

def remove_trip_item(item_id: str) -> bool:
    """
    Remove an item from the trip plan.
    Returns True if successful, False otherwise.
    """
    try:
        trip_data = load_trip_data()
        
        # Find the item with the given ID
        if "items" in trip_data:
            initial_count = len(trip_data["items"])
            trip_data["items"] = [item for item in trip_data["items"] if item.get("id") != item_id]
            
            # If an item was removed, save the updated data
            if len(trip_data["items"]) < initial_count:
                save_trip_data(trip_data)
                logger.info(f"Removed item from trip: {item_id}")
                return True
        
        logger.warning(f"Item not found in trip: {item_id}")
        return False
    except Exception as e:
        logger.error(f"Error removing trip item: {e}")
        return False

def set_trip_dates(start_date: str, end_date: str) -> bool:
    """
    Set the start and end dates for the trip.
    Returns True if successful, False otherwise.
    """
    try:
        trip_data = load_trip_data()
        
        # Update dates
        trip_data["start_date"] = start_date
        trip_data["end_date"] = end_date
        
        # Save updated data
        save_trip_data(trip_data)
        
        logger.info(f"Set trip dates: {start_date} to {end_date}")
        return True
    except Exception as e:
        logger.error(f"Error setting trip dates: {e}")
        return False

def get_trip_duration() -> int:
    """
    Calculate the trip duration in days.
    Returns 0 if dates are not set or invalid.
    """
    try:
        trip_data = load_trip_data()
        
        start_date = trip_data.get("start_date")
        end_date = trip_data.get("end_date")
        
        if not start_date or not end_date:
            return 0
        
        # Parse dates
        try:
            # Try ISO format first (2023-04-15)
            start = datetime.fromisoformat(start_date)
        except ValueError:
            # Fall back to other formats like MM/DD/YYYY
            start = datetime.strptime(start_date, "%m/%d/%Y")
            
        try:
            end = datetime.fromisoformat(end_date)
        except ValueError:
            end = datetime.strptime(end_date, "%m/%d/%Y")
        
        # Calculate duration
        duration = (end - start).days + 1  # +1 to include the end date
        return max(0, duration)  # Ensure non-negative
    except Exception as e:
        logger.error(f"Error calculating trip duration: {e}")
        return 0

class SessionStore:
    """
    Session store with Redis backend
    Handles session state persistence and caching
    """
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the session store
        
        Args:
            redis_url: Optional Redis URL (defaults to local)
        """
        self.redis: Optional[Redis] = None
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        self._use_redis = False
        
        if redis_url and REDIS_AVAILABLE and Redis:
            try:
                self.redis = Redis.from_url(redis_url, decode_responses=True)
                self.redis.ping() # Test connection
                self._use_redis = True
                logger.info(f"SessionStore connected to Redis: {redis_url}")
            except ConnectionError as e:
                 logger.warning(f"SessionStore Redis connection failed: {e}. Falling back to in-memory storage.")
                 self.redis = None # Ensure redis is None
            except Exception as e:
                logger.error(f"Error initializing SessionStore Redis connection: {e}. Falling back to in-memory storage.")
                self.redis = None
        
        # Fallback to in-memory if Redis isn't configured or fails
        if not self._use_redis:
             logger.info("SessionStore using in-memory storage.")

    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Get session data from Redis or in-memory
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary containing session data
        """
        try:
            if self._use_redis and self.redis:
                data = self.redis.get(f"session:{session_id}")
                return json.loads(data) if data else {}
            else:
                return self.memory_store.get(session_id, {}).copy()
            
        except Exception as e:
            logger.error(f"Error getting session {session_id}: {e}")
            return {}
            
    def set_session(self, session_id: str, data: Dict[str, Any], 
                   expire_seconds: int = 86400) -> None:
        """
        Set session data in Redis or in-memory
        
        Args:
            session_id: Unique session identifier
            data: Dictionary containing session data
            expire_seconds: Time to live in seconds (default: 1 day)
        """
        try:
            if self._use_redis and self.redis:
                self.redis.setex(
                    f"session:{session_id}",
                    expire_seconds,
                    json.dumps(data)
                )
            else:
                self.memory_store[session_id] = data
                
        except Exception as e:
            logger.error(f"Error setting session {session_id}: {e}")
            
    def delete_session(self, session_id: str) -> None:
        """
        Delete session data
        
        Args:
            session_id: Unique session identifier
        """
        try:
            if self._use_redis and self.redis:
                self.redis.delete(f"session:{session_id}")
            else:
                self.memory_store.pop(session_id, None)
                
        except Exception as e:
            logger.error(f"Error deleting session {session_id}: {e}")
            
    def _get_from_memory(self, session_id: str) -> Dict[str, Any]:
        """Get session from in-memory storage"""
        # In-memory storage implementation
        return self.memory_store.get(session_id, {}).copy()
        
    def _set_in_memory(self, session_id: str, data: Dict[str, Any], 
                      expire_seconds: int) -> None:
        """Set session in in-memory storage"""
        # In-memory storage implementation
        self.memory_store[session_id] = data
        
    def _delete_from_memory(self, session_id: str) -> None:
        """Delete session from in-memory storage"""
        # In-memory storage implementation
        self.memory_store.pop(session_id, None)

class CacheStore:
    """
    Cache store with Redis backend
    Handles caching of API responses and frequently accessed data
    """
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the cache store
        
        Args:
            redis_url: Optional Redis URL (defaults to local)
        """
        self.redis: Optional[Redis] = None
        self.memory_store: Dict[str, Dict[str, Any]] = {}
        self._use_redis = False
        
        if redis_url and REDIS_AVAILABLE and Redis:
            try:
                self.redis = Redis.from_url(redis_url, decode_responses=True)
                self.redis.ping() # Test connection
                self._use_redis = True
                logger.info(f"CacheStore connected to Redis: {redis_url}")
            except ConnectionError as e:
                 logger.warning(f"CacheStore Redis connection failed: {e}. Falling back to in-memory storage.")
                 self.redis = None # Ensure redis is None
            except Exception as e:
                logger.error(f"Error initializing CacheStore Redis connection: {e}. Falling back to in-memory storage.")
                self.redis = None
        
        # Fallback to in-memory if Redis isn't configured or fails
        if not self._use_redis:
             logger.info("CacheStore using in-memory storage.")

    def get(self, key: str, cache_type: str = "data") -> Optional[Any]:
        """
        Get cached data
        
        Args:
            key: Cache key
            cache_type: Type of cache (data, api, etc.)
            
        Returns:
            Cached data or None if not found
        """
        try:
            if self._use_redis and self.redis:
                full_key = f"cache:{cache_type}:{key}"
                data = self.redis.get(full_key)
                return json.loads(data) if data else None
            else:
                return self.memory_store.get(key, {}).copy()
            
        except Exception as e:
            logger.error(f"Error getting cache {key}: {e}")
            return None
            
    def set(self, key: str, value: Any, 
           cache_type: str = "data", expire_seconds: int = 3600) -> None:
        """
        Set cached data
        
        Args:
            key: Cache key
            value: Data to cache
            cache_type: Type of cache
            expire_seconds: Time to live in seconds
        """
        try:
            if self._use_redis and self.redis:
                full_key = f"cache:{cache_type}:{key}"
                self.redis.setex(
                    full_key,
                    expire_seconds,
                    json.dumps(value)
                )
            else:
                self.memory_store[key] = value
                
        except Exception as e:
            logger.error(f"Error setting cache {key}: {e}")
            
    def delete(self, key: str, cache_type: str = "data") -> None:
        """
        Delete cached data
        
        Args:
            key: Cache key
            cache_type: Type of cache
        """
        try:
            if self._use_redis and self.redis:
                full_key = f"cache:{cache_type}:{key}"
                self.redis.delete(full_key)
            else:
                self.memory_store.pop(key, None)
                
        except Exception as e:
            logger.error(f"Error deleting cache {key}: {e}")

class StateManager:
    """
    State manager that combines session and cache stores
    Handles state persistence and caching with fallbacks
    """
    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize the state manager
        
        Args:
            redis_url: Optional Redis URL
        """
        self.session_store = SessionStore(redis_url)
        self.cache_store = CacheStore(redis_url)
        
    def get_user_state(self, user_id: str) -> Dict[str, Any]:
        """
        Get user's complete state including session and cached data
        
        Args:
            user_id: Unique user identifier
            
        Returns:
            Dictionary containing user state
        """
        try:
            session_data = self.session_store.get_session(user_id)
            cached_data = self._get_cached_state(user_id)
            
            return {
                "session": session_data,
                "cache": cached_data
            }
            
        except Exception as e:
            logger.error(f"Error getting user state for {user_id}: {e}")
            return {}
            
    def set_user_state(self, user_id: str, data: Dict[str, Any], 
                      expire_seconds: int = 86400) -> None:
        """
        Set user's state with proper caching
        
        Args:
            user_id: Unique user identifier
            data: User state data
            expire_seconds: Time to live
        """
        try:
            # Split data into session and cache
            session_data = data.get("session", {})
            cache_data = data.get("cache", {})
            
            # Store session data
            self.session_store.set_session(user_id, session_data, expire_seconds)
            
            # Cache data
            for key, value in cache_data.items():
                self.cache_store.set(key, value, "user", expire_seconds)
            
        except Exception as e:
            logger.error(f"Error setting user state for {user_id}: {e}")
            
    def _get_cached_state(self, user_id: str) -> Dict[str, Any]:
        """Get cached state for a user"""
        try:
            # Get all user-related cache keys
            keys = self.cache_store.redis.keys(f"cache:user:{user_id}:*")
            
            # Get all cached values
            cached_data = {}
            for key in keys:
                value = self.cache_store.get(key.decode(), "user")
                if value:
                    cached_data[key.decode()] = value
            
            return cached_data
            
        except Exception as e:
            logger.error(f"Error getting cached state for {user_id}: {e}")
            return {}
            
    def clear_user_state(self, user_id: str) -> None:
        """
        Clear all state for a user
        
        Args:
            user_id: Unique user identifier
        """
        try:
            # Clear session
            self.session_store.delete_session(user_id)
            
            # Clear cache
            self.cache_store.delete(f"user:{user_id}", "user")
            
        except Exception as e:
            logger.error(f"Error clearing user state for {user_id}: {e}")

# Create global instances
session_store = SessionStore()
cache_store = CacheStore()
state_manager = StateManager()

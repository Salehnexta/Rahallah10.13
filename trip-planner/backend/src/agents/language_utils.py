"""
Language Utilities for Trip Planning Assistant
Handles language detection and related functionality
"""
import re
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Arabic character range in Unicode
ARABIC_UNICODE_RANGE = re.compile(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]+')

def detect_language(text):
    """
    Detect if text is in Arabic or English
    
    Args:
        text (str): Text to analyze
        
    Returns:
        str: 'ar' for Arabic, 'en' for English
    """
    # Check if text contains Arabic characters
    if ARABIC_UNICODE_RANGE.search(text):
        logger.info("Detected Arabic text")
        return 'ar'
    else:
        logger.info("Detected English text (or non-Arabic)")
        return 'en'

def get_direction(language):
    """
    Get text direction based on language
    
    Args:
        language (str): Language code ('ar' or 'en')
        
    Returns:
        str: 'rtl' for Arabic, 'ltr' for English
    """
    return 'rtl' if language == 'ar' else 'ltr'

def format_response_for_language(response, language):
    """
    Apply any language-specific formatting to the response
    
    Args:
        response (str): The text response
        language (str): Language code ('ar' or 'en')
        
    Returns:
        str: Formatted response
    """
    # Currently no special formatting needed, but this function
    # can be expanded later if needed
    return response

# TODO.md: Build the Trip Planning Assistant

## Overview
- **Goal:** Create a Saudi-focused travel planning assistant with a conversational interface
- **Features:** Flight booking, hotel booking, and complete trip planning in both English and Arabic
- **Architecture:** ChatGPT-style interface with a conversation-led approach using entirely mock data
- **Technology:** Flask + React + LangChain + DeepSeek

---

## Step 1: Set Up Development Environment
- **Task:** Create project structure and install dependencies
- **Details:**
  - Install Python 3.10.12
  - Install Node.js 18.18.0 LTS and npm
  - Create folder structure:
    ```
    trip-planner/
    ├── backend/
    │   ├── app.py
    │   ├── requirements.txt
    │   └── agents/
    ├── frontend/
    └── README.md
    ```
  - Install backend dependencies:
    ```
    flask==2.3.3
    flask-cors==4.0.0
    python-dotenv==1.0.0
    langchain==0.1.0
    openai==1.3.5
    ```
  - Create `.env` file for API keys:
    ```
    DEEPSEEK_API_KEY=your_api_key_here
    ```

---

## Step 2: Build Flask Backend
- **Task:** Create the backend server with routes and session management
- **Details:**
  - Create a basic Flask app with CORS support
  - Add `/api/chat` POST endpoint for handling messages
  - Implement in-memory session storage for conversation history
  - Set up error handling and logging
  - Configure environment variables for API keys

---

## Step 3: Implement LangChain With DeepSeek
- **Task:** Set up the LLM connection via OpenAI SDK
- **Details:**
  - Connect to DeepSeek using the OpenAI compatibility layer
  - Configure LLM settings (temperature, etc.)
  - Create utility functions for generating responses
  - Test LLM connection with a simple prompt
  - Document: https://platform.deepseek.com/api-documentation

---

## Step 4: Create Agent System
- **Task:** Implement the four agent types with LangChain
- **Details:**
  - Create the Conversation Lead Agent with this prompt:
    ```
    You are a friendly travel assistant that helps users book flights, hotels, or plan trips.
    You engage in casual, natural conversation like ChatGPT. Your job is to:

    1. Make the conversation feel natural and friendly
    2. Determine what the user needs (flight booking, hotel booking, or trip planning)
    3. Extract only the essential information needed through casual conversation
    4. When you have enough information, pass the request to a specialized agent
    5. If the user speaks Arabic, respond in Arabic with the same natural, conversational style

    Important: Keep responses short and conversational. Don't ask multiple questions at once.
    Don't use forms or lengthy questions. Just have a natural chat until you understand what they need.

    For Arabic users, be sure to maintain the same casual, helpful tone. Use common Saudi travel terms when appropriate.

    Current conversation:
    {history}
    Human: {input}
    AI:
    ```

  - Create the Flight Agent with this prompt:
    ```
    You are a flight booking assistant. Generate completely fictional but realistic-sounding flight options.
    DO NOT use real flight data - create mock flight information that seems plausible.
    Include airlines, prices, times, and flight numbers. If the user speaks Arabic,
    respond in Arabic. Format your response like a real booking assistant.

    Include only one fictional flight option with:
    - Airline (prefer Saudi airlines like Saudia, flynas, flyadeal)
    - Departure and arrival times
    - Flight duration
    - Price in SAR (use realistic price ranges for the route)
    - Flight number (fictional)
    - A mock booking link (not a real URL)

    Remember, all data should be completely made-up but realistic seeming.

    Current conversation:
    {history}
    Human: {input}
    AI:
    ```

  - Create the Hotel Agent with this prompt:
    ```
    You are a hotel booking assistant. Generate completely fictional but realistic-sounding hotel options.
    DO NOT use real hotel data - create mock hotel information that seems plausible for the location.
    Include hotel names, prices, amenities, and locations. If the user speaks Arabic,
    respond in Arabic. Format your response like a real booking assistant.

    Include only one fictional hotel option with:
    - Hotel name (realistic for the location but invented)
    - Star rating (3-5 stars)
    - Location description (plausible but fictional)
    - 2-3 key amenities
    - Price per night in SAR (use realistic price ranges for the location)
    - A mock booking link (not a real URL)

    Remember, all data should be completely made-up but realistic seeming.

    Current conversation:
    {history}
    Human: {input}
    AI:
    ```

  - Create the Trip Planning Agent with this prompt:
    ```
    You are a trip planning assistant. Generate completely fictional but realistic-sounding travel packages.
    DO NOT use real travel data - create mock flight and hotel information that seems plausible.
    If the user speaks Arabic, respond in Arabic. Format your response like a real travel agent.

    Include:
    - One fictional flight option with airline, times, and price
    - One fictional hotel option with name, rating, and price
    - Total package price in SAR
    - Brief 1-2 sentence suggestion about the destination
    - Mock booking links for both flight and hotel (not real URLs)

    Remember, all data should be completely made-up but realistic seeming.

    Current conversation:
    {history}
    Human: {input}
    AI:
    ```

  - Create the Intent Recognition system with this prompt:
    ```
    Analyze the following conversation and determine if there's enough information to proceed with one of these actions:
    1. Book a flight
    2. Book a hotel
    3. Plan a trip (combining flight and hotel)
    4. None yet - need more information

    Only respond with one of these exact values: "flight", "hotel", "trip", or "continue_conversation"

    If it's a flight booking, there should be information about destination and approximate dates.
    If it's a hotel booking, there should be information about location and approximate dates.
    If it's trip planning, there should be information about destination and approximate duration.

    If any essential information is missing, respond with "continue_conversation".

    User's message: {user_input}
    Previous conversation: {conversation_history}

    Intent:
    ```

  - Implement language detection to support Arabic conversations
  - Document: https://python.langchain.com/docs/get_started/introduction

---

## Step 5: Build Conversation Flow Logic
- **Task:** Create the conversation orchestration system
- **Details:**
  - Implement the intent detection workflow
  - Create the conversation memory system
  - Build the agent selection logic based on intent
  - Set up the language detection and response formatting
  - Add system to track user preferences from conversation

---

## Step 6: Create React Frontend
- **Task:** Build a ChatGPT-style interface
- **Details:**
  - Create a new React app
  - Build components:
    - Chat container
    - Message bubbles with avatar icons
    - Input form with send button
    - Typing indicator animation
    - Sample prompt buttons
  - Implement styling:
    - Clean, minimalist design
    - Light/dark mode
    - Responsive layout
    - RTL support for Arabic
  - Add conversation features:
    - Message history display
    - Welcome message
    - Sample prompts for new users
  - Document: https://react.dev/learn

---

## Step 7: Implement Arabic Support
- **Task:** Ensure full bilingual functionality
- **Details:**
  - Test Arabic input handling
  - Verify RTL text display
  - Ensure Arabic responses are properly formatted
  - Test Arabic sample prompts
  - Verify agent responses switch languages correctly

---

## Step 8: Test All Conversation Flows
- **Task:** Verify the system works end-to-end
- **Details:**
  - Test flight booking conversations in English and Arabic
  - Test hotel booking conversations in English and Arabic
  - Test trip planning conversations in English and Arabic
  - Test mixed conversations with switching intents
  - Verify mock data generation is realistic but fictional
  - Test conversation continuity and memory

---

## Step 9: Optimize and Polish
- **Task:** Finalize the application for demo
- **Details:**
  - Improve response times
  - Add loading states and error handling
  - Polish UI animations and transitions
  - Ensure mobile responsiveness
  - Create example conversation scripts for demo
  - Document limitations and future enhancements

---

## Step 10: Documentation
- **Task:** Create developer documentation
- **Details:**
  - Document API endpoints
  - Create setup instructions
  - Add sample prompts and example flow diagrams
  - Document agent prompt design
  - Create demo script for investor presentation

---

## Documentation Resources
- **LangChain**: https://python.langchain.com/docs/get_started/introduction
- **Flask**: https://flask.palletsprojects.com/en/2.3.x/
- **React**: https://react.dev/learn
- **DeepSeek**: https://platform.deepseek.com/api-documentation

---

## Notes
- All travel data must be fictional but realistic - the LLM generates mock data
- Conversation should feel natural, not like filling out a form
- Focus on the three distinct functions: flight booking, hotel booking, and trip planning
- Arabic support is essential for Saudi market
- The interface should closely resemble ChatGPT's clean, simple design

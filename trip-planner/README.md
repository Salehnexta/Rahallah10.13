# Saudi Trip Planning Assistant (v1.0.6)

A conversational travel planning assistant focused on the Saudi market, supporting both English and Arabic languages.

## Features

- **Flight Booking**: Search and book flights with mock data
- **Hotel Booking**: Find and book hotels with mock data
- **Trip Planning**: Complete travel packages combining flights and hotels
- **Itinerary Generation**: Day-by-day activity planning for Saudi destinations
- **Bilingual Support**: Full functionality in both English and Arabic
- **Conversational Interface**: Natural chat experience similar to ChatGPT
- **Multi-turn Conversations**: Maintains context across conversation turns

## Technology Stack

- **Backend**: Flask (Python 3.10.12)
- **Frontend**: React
- **AI**: LangChain with DeepSeek LLM
- **Language Support**: English and Arabic

## Project Structure

```bash
trip-planner/
├── backend/
│   ├── app.py              # Main Flask application
│   ├── requirements.txt    # Python dependencies
│   └── agents/             # LangChain agents for different tasks
├── frontend/               # React application
└── README.md               # This file
```

## Setup Instructions

### Backend Setup

1. Install Python 3.10.12
2. Navigate to the backend directory
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file with your API keys
5. Run the server: `python app.py`

### Frontend Setup

1. Install Node.js 18.18.0 LTS and npm
2. Navigate to the frontend directory
3. Install dependencies: `npm install`
4. Start the development server: `npm start`

## API Documentation

See the `/docs` directory for detailed API documentation.

## Changelog

### Version 1.0.6 (April 2025)

- **Enhanced Itinerary Generation**: Added detailed day-by-day activity planning for Saudi destinations
- **Improved Context Handling**: Better maintenance of conversation context across multiple turns
- **Enhanced Intent Detection**: More accurate detection of user intents for smoother conversations
- **DeepSeek API Integration**: Updated to use the latest DeepSeek API for improved responses
- **Dependency Updates**: Upgraded to OpenAI SDK >=1.12.0 and latest LangChain/LangGraph packages
- **Bug Fixes**: Resolved issues with intent transitions in multi-turn conversations
- **End-to-End Testing**: Added comprehensive tests for conversations and language switching

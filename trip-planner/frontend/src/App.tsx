import React from 'react';
import ChatContainer from './components/ChatContainer';
import './styles/App.css';
import './styles/components.css';
import './styles/ItineraryDisplay.css';

/**
 * Main App component that serves as the entry point for the Trip Planning Assistant
 * Includes the chat interface with support for both English and Arabic languages
 */
const App: React.FC = () => {
  return (
    <div className="app">
      <header className="app-header">
        <h1>Saudi Trip Planning Assistant</h1>
        <h2 className="app-subtitle">v.f10.8</h2>
      </header>
      <main className="app-main">
        <ChatContainer />
      </main>
      <footer className="app-footer">
        <p>&copy; {new Date().getFullYear()} Saudi Trip Planning Assistant</p>
      </footer>
    </div>
  );
};

export default App;

import React from 'react';
import { Message } from '../types';
import ItineraryDisplay from './ItineraryDisplay';
import '../styles/ItineraryDisplay.css';

interface ChatMessageProps {
  message: Message;
  language: 'en' | 'ar';
}

/**
 * Component for rendering a single chat message with avatar
 */
const ChatMessage: React.FC<ChatMessageProps> = ({ message, language }) => {
  const isUser = message.role === 'user';
  const messageClass = isUser ? 'message-user' : 'message-assistant';
  const avatarClass = isUser ? 'avatar-user' : 'avatar-assistant';
  const avatarText = isUser ? 'U' : 'A';
  
  // Set text direction based on language
  const textDirection = language === 'ar' ? 'rtl' : 'ltr';

  return (
    <div className={`message ${messageClass}`}>
      {!isUser && (
        <div className={`avatar ${avatarClass}`}>
          {avatarText}
        </div>
      )}
      <div 
        className="message-content"
        dir={textDirection}
      >
        {isUser ? (
          <p className="message-text">{message.content}</p>
        ) : (
          <ItineraryDisplay content={message.content} language={language} />
        )}
      </div>
      {isUser && (
        <div className={`avatar ${avatarClass}`}>
          {avatarText}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;

import React, { useState } from 'react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading: boolean;
  language: 'en' | 'ar';
  disabled?: boolean;
}

/**
 * Component for the chat input form with send button
 */
const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, isLoading, language, disabled = false }) => {
  const [message, setMessage] = useState('');
  
  // Set text direction and placeholders based on language
  const textDirection = language === 'ar' ? 'rtl' : 'ltr';
  const placeholder = language === 'ar' 
    ? 'اكتب رسالتك هنا...' 
    : 'Type your message here...';
  const sendButtonText = language === 'ar' ? 'إرسال' : 'Send';

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  return (
    <div className="chat-input-container">
      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder={placeholder}
          dir={textDirection}
          disabled={isLoading || disabled}
        />
        <button 
          type="submit" 
          className="send-button"
          disabled={isLoading || disabled || !message.trim()}
        >
          {sendButtonText}
        </button>
      </form>
    </div>
  );
};

export default ChatInput;

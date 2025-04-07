import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatHeader from './ChatHeader';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import TypingIndicator from './TypingIndicator';
import SamplePrompts from './SamplePrompts';
import { Message, SamplePrompt } from '../types';
import { sendChatMessage, resetChatSession } from '../utils/api';

/**
 * Main chat container component that manages the conversation state
 */
const ChatContainer: React.FC = () => {
  // State for messages, loading, theme, language
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string>('');
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [language, setLanguage] = useState<'en' | 'ar'>('en');
  
  // Reference to message container for scrolling
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Sample prompts in both languages
  const samplePrompts: SamplePrompt[] = [
    { id: '1', text: 'I want to book a flight to Riyadh', language: 'en' },
    { id: '2', text: 'Find me a hotel in Jeddah', language: 'en' },
    { id: '3', text: 'Plan a trip to AlUla for next weekend', language: 'en' },
    { id: '4', text: 'أريد حجز رحلة إلى الرياض', language: 'ar' },
    { id: '5', text: 'ابحث لي عن فندق في جدة', language: 'ar' },
    { id: '6', text: 'خطط لي رحلة إلى العلا في عطلة نهاية الأسبوع القادم', language: 'ar' },
  ];

  // Welcome message based on language
  useEffect(() => {
    if (messages.length === 0) {
      const welcomeMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: language === 'en' 
          ? 'Welcome to Saudi Trip Planner! How can I help you today? I can assist with flight bookings, hotel reservations, or complete trip planning.'
          : 'مرحبًا بك في مخطط رحلات السعودية! كيف يمكنني مساعدتك اليوم؟ يمكنني المساعدة في حجز الرحلات الجوية أو حجوزات الفنادق أو تخطيط الرحلات الكاملة.',
        timestamp: new Date(),
      };
      setMessages([welcomeMessage]);
    }
  }, [language, messages.length]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Set theme on body element
  useEffect(() => {
    document.body.setAttribute('data-theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  // Set direction on body element
  useEffect(() => {
    document.body.setAttribute('dir', language === 'ar' ? 'rtl' : 'ltr');
  }, [language]);

  // Function to scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Toggle theme between light and dark
  const toggleTheme = () => {
    setIsDarkMode(prev => !prev);
  };

  // Toggle language between English and Arabic
  const toggleLanguage = () => {
    setLanguage(prev => prev === 'en' ? 'ar' : 'en');
  };

  // Handle sending a message
  const handleSendMessage = async (content: string) => {
    // Create new user message
    const userMessage: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    
    // Add user message to state
    setMessages(prev => [...prev, userMessage]);
    
    // Set loading state
    setIsLoading(true);
    
    try {
      // Send message to API
      const response = await sendChatMessage(content, sessionId);
      
      // Save session ID if this is first message
      if (!sessionId) {
        setSessionId(response.session_id);
      }
      
      // Create assistant message from response
      const assistantMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date(),
      };
      
      // Add assistant message to state
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update language if it changed
      if (response.language !== language) {
        setLanguage(response.language as 'en' | 'ar');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: Message = {
        id: uuidv4(),
        role: 'assistant',
        content: language === 'en'
          ? 'Sorry, there was an error processing your request. Please try again.'
          : 'عذرًا، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى.',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle selecting a sample prompt
  const handleSelectPrompt = (prompt: string) => {
    handleSendMessage(prompt);
  };

  // Handle resetting the conversation
  const handleResetConversation = async () => {
    if (sessionId) {
      try {
        await resetChatSession(sessionId);
        setMessages([]);
        setSessionId('');
      } catch (error) {
        console.error('Error resetting conversation:', error);
      }
    } else {
      setMessages([]);
    }
  };

  return (
    <div className="chat-container">
      <ChatHeader 
        onToggleTheme={toggleTheme}
        onToggleLanguage={toggleLanguage}
        isDarkMode={isDarkMode}
        language={language}
      />
      
      <div className="chat-messages">
        {messages.map(message => (
          <ChatMessage 
            key={message.id} 
            message={message} 
            language={language}
          />
        ))}
        
        {isLoading && <TypingIndicator />}
        
        <div ref={messagesEndRef} />
      </div>
      
      {messages.length === 1 && (
        <SamplePrompts 
          prompts={samplePrompts}
          onSelectPrompt={handleSelectPrompt}
          language={language}
        />
      )}
      
      <ChatInput 
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
        language={language}
      />
    </div>
  );
};

export default ChatContainer;

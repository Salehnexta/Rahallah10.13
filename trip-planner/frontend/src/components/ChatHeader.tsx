import React from 'react';

interface ChatHeaderProps {
  onToggleTheme: () => void;
  onToggleLanguage: () => void;
  isDarkMode: boolean;
  language: 'en' | 'ar';
}

/**
 * Component for the chat header with theme and language toggles
 */
const ChatHeader: React.FC<ChatHeaderProps> = ({ 
  onToggleTheme, 
  onToggleLanguage, 
  isDarkMode,
  language 
}) => {
  const themeIcon = isDarkMode ? '☀️' : '🌙';
  const languageText = language === 'en' ? 'العربية' : 'English';
  const title = language === 'en' ? 'Saudi Trip Planner' : 'مخطط رحلات السعودية';
  
  // Set text direction based on language
  const textDirection = language === 'ar' ? 'rtl' : 'ltr';

  return (
    <div className="chat-header" dir={textDirection}>
      <h1>{title}</h1>
      <div className="header-controls">
        <button className="language-toggle" onClick={onToggleLanguage}>
          {languageText}
        </button>
        <button className="theme-toggle" onClick={onToggleTheme}>
          {themeIcon}
        </button>
      </div>
    </div>
  );
};

export default ChatHeader;

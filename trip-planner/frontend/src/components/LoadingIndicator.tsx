import React from 'react';
import TypingIndicator from './TypingIndicator';

interface LoadingIndicatorProps {
  language: 'en' | 'ar';
  type?: 'minimal' | 'full';
}

/**
 * Component for displaying loading state with customizable appearance
 */
const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({ 
  language, 
  type = 'full' 
}) => {
  const loadingText = language === 'en'
    ? 'Processing your request...'
    : 'جاري معالجة طلبك...';

  if (type === 'minimal') {
    return <TypingIndicator />;
  }

  return (
    <div className={`loading-container ${language === 'ar' ? 'rtl' : 'ltr'}`}>
      <TypingIndicator />
      <p className="loading-text">{loadingText}</p>
    </div>
  );
};

export default LoadingIndicator;

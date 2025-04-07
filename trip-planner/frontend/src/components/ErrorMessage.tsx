import React from 'react';

interface ErrorMessageProps {
  message: string;
  onRetry?: () => void;
  language: 'en' | 'ar';
}

/**
 * Component for displaying error messages with retry functionality
 */
const ErrorMessage: React.FC<ErrorMessageProps> = ({ message, onRetry, language }) => {
  const defaultErrorMessage = language === 'en'
    ? 'Something went wrong. Please try again.'
    : 'حدث خطأ ما. يرجى المحاولة مرة أخرى.';

  return (
    <div className={`error-container ${language === 'ar' ? 'rtl' : 'ltr'}`}>
      <div className="error-icon">⚠️</div>
      <div className="error-content">
        <p className="error-text">{message || defaultErrorMessage}</p>
        {onRetry && (
          <button
            className="retry-button"
            onClick={onRetry}
            aria-label={language === 'en' ? 'Try again' : 'حاول مرة أخرى'}
          >
            {language === 'en' ? 'Try again' : 'حاول مرة أخرى'}
          </button>
        )}
      </div>
    </div>
  );
};

export default ErrorMessage;

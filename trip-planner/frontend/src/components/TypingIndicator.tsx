import React from 'react';

/**
 * Component for showing a typing animation when the assistant is "thinking"
 */
const TypingIndicator: React.FC = () => {
  return (
    <div className="typing-indicator">
      <span></span>
      <span></span>
      <span></span>
    </div>
  );
};

export default TypingIndicator;

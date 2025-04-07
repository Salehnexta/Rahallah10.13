import React from 'react';

interface LanguageSwitcherProps {
  language: 'en' | 'ar';
  onToggle: () => void;
}

/**
 * Component for switching between English and Arabic languages
 */
const LanguageSwitcher: React.FC<LanguageSwitcherProps> = ({ language, onToggle }) => {
  return (
    <button
      className="language-switcher"
      onClick={onToggle}
      aria-label={language === 'en' ? 'Switch to Arabic' : 'Switch to English'}
    >
      <span className="language-icon">🌐</span>
      <span className="language-text">
        {language === 'en' ? 'العربية' : 'English'}
      </span>
    </button>
  );
};

export default LanguageSwitcher;

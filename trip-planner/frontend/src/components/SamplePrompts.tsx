import React from 'react';
import { SamplePrompt } from '../types';

interface SamplePromptsProps {
  prompts: SamplePrompt[];
  onSelectPrompt: (prompt: string) => void;
  language: 'en' | 'ar';
}

/**
 * Component for displaying sample prompt buttons
 */
const SamplePrompts: React.FC<SamplePromptsProps> = ({ prompts, onSelectPrompt, language }) => {
  // Filter prompts by language
  const filteredPrompts = prompts.filter(prompt => prompt.language === language);
  
  // Set text direction based on language
  const textDirection = language === 'ar' ? 'rtl' : 'ltr';

  return (
    <div className="sample-prompts" dir={textDirection}>
      {filteredPrompts.map((prompt) => (
        <button
          key={prompt.id}
          className="sample-prompt-button"
          onClick={() => onSelectPrompt(prompt.text)}
        >
          {prompt.text}
        </button>
      ))}
    </div>
  );
};

export default SamplePrompts;

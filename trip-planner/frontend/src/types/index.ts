// Message type for chat conversations
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

// Chat session type
export interface ChatSession {
  id: string;
  messages: Message[];
  language: 'en' | 'ar';
}

// API response type for chat
export interface ChatResponse {
  session_id: string;
  response: string;
  language: 'en' | 'ar';
  intent: 'flight' | 'hotel' | 'trip' | 'continue_conversation';
}

// Sample prompt type
export interface SamplePrompt {
  id: string;
  text: string;
  language: 'en' | 'ar';
}

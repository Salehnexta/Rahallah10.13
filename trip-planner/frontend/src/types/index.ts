// Message type for chat conversations
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  intent?: string;
  isError?: boolean;
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
  intent: 'flight_booking' | 'hotel_booking' | 'trip_planning' | 'general' | string;
  error?: string;
  success: boolean;
}

// Sample prompt type
export interface SamplePrompt {
  id: string;
  text: string;
  language: 'en' | 'ar';
}

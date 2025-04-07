import axios from 'axios';
import { ChatResponse } from '../types';

// API base URL - change this to match your backend server
const API_BASE_URL = 'http://localhost:5000/api';

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Send a chat message to the backend
 * @param message User's message
 * @param sessionId Optional session ID for continuing a conversation
 * @returns Promise with the chat response
 */
export const sendChatMessage = async (
  message: string,
  sessionId?: string
): Promise<ChatResponse> => {
  try {
    const response = await api.post('/chat', {
      message,
      session_id: sessionId,
    });
    return response.data;
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

/**
 * Reset a chat session
 * @param sessionId Session ID to reset
 * @returns Promise with the reset confirmation
 */
export const resetChatSession = async (sessionId: string): Promise<{ status: string; message: string }> => {
  try {
    const response = await api.post('/reset', {
      session_id: sessionId,
    });
    return response.data;
  } catch (error) {
    console.error('Error resetting chat session:', error);
    throw error;
  }
};

/**
 * Check API health status
 * @returns Promise with health status
 */
export const checkApiHealth = async (): Promise<{ status: string; version: string; llm_status: string }> => {
  try {
    const response = await api.get('/health');
    return response.data;
  } catch (error) {
    console.error('Error checking API health:', error);
    throw error;
  }
};

/**
 * Get supported languages
 * @returns Promise with supported languages
 */
export const getSupportedLanguages = async (): Promise<{ supported_languages: string[]; default_language: string }> => {
  try {
    const response = await api.get('/languages');
    return response.data;
  } catch (error) {
    console.error('Error getting supported languages:', error);
    throw error;
  }
};

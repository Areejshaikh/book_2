import { authService } from '../services/authService';

const getBaseURL = () => {
  const envUrl = import.meta.env?.VITE_API_URL || process.env?.REACT_APP_API_BASE_URL;
  return envUrl || 'https://marvelous-delight-production.up.railway.app';
};

export const chatAPI = {
  sendMessage: async (query, bookId = 'default-book', sessionId = null) => {
    const backendUrl = getBaseURL();
    const finalSessionId = sessionId || `session_${Date.now()}`;

    try {
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json', // Ye line add karein
        },
        // Credentials wali line maine hata di hai security ke liye
        body: JSON.stringify({
          query: query.trim(),
          book_id: bookId,
          session_id: finalSessionId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server Error: ${response.status} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Fetch error details:", error);
      throw new Error('Backend connection failed. Please check if Railway is awake.');
    }
  },

  getConversationHistory: async (userId) => {
    const backendUrl = getBaseURL();
    try {
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'GET',
        headers: { 'Accept': 'application/json' }
      });
      return await response.json();
    } catch (error) {
      throw new Error('Could not fetch history');
    }
  },
};
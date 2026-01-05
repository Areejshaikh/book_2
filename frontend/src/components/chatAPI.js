import { authService } from '../services/authService';

// ✅ Fixed: Vite friendly URL fetching
const getBaseURL = () => {
  // Vite projects mein 'import.meta.env' use hota hai
  const envUrl = import.meta.env?.VITE_API_URL;

  if (envUrl) {
    return envUrl;
  }

  // Agar variable nahi milta toh direct Railway link (Default)
  return 'https://marvelous-delight-production.up.railway.app';
};

export const chatAPI = {
  sendMessage: async (query, book_id = 'default-book', sessionId = null) => {
    const backendUrl = getBaseURL();
    const finalSessionId = sessionId || `session_${Date.now()}`;

    try {
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          query: query.trim(),
          book_id: book_id,
          session_id: finalSessionId,
        }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Server Error: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Fetch error:", error);
      throw error;
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
      throw new Error('Network error');
    }
  },
};
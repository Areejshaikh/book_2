import { authService } from '../services/authService';

// ✅ Fixed: Direct link to Railway
const getBaseURL = () => {
  // Pehle check karein ke environment variable hai ya nahi
  // Agar Vite use kar rahe hain toh: import.meta.env.VITE_API_URL
  // Agar Create React App hai toh: process.env.REACT_APP_API_BASE_URL
  
  const envUrl = import.meta.env?.VITE_API_URL || process.env?.REACT_APP_API_BASE_URL;

  if (envUrl) {
    return envUrl;
  }

  // Agar koi variable nahi mila, toh default Railway link use karein
  return 'https://marvelous-delight-production.up.railway.app';
};

export const chatAPI = {
  sendMessage: async (
    query,
    bookId = 'default-book',
    sessionId = null,
    backendUrlOverride = null
  ) => {
    // Railway ka sahi URL yahan set ho jayega
    const backendUrl = backendUrlOverride || getBaseURL();

    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    if (!query || query.trim().length === 0) {
      throw new Error('Query cannot be empty');
    }

    try {
      // Is line mein ab localhost nahi, Railway link jayega
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        // 'include' credentials tabhi use karein agar aap Cookies use kar rahe hain
        // Varna isay hata dena behtar hai
        body: JSON.stringify({
          query: query.trim(),
          book_id: bookId,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `HTTP Error ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError') {
        throw new Error('Network error: Backend not reachable at ' + backendUrl);
      }
      throw error;
    }
  },

  getConversationHistory: async (userId, backendUrlOverride = null) => {
    const backendUrl = backendUrlOverride || getBaseURL();
    if (!userId) throw new Error('User ID is required');

    try {
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'GET',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || errorData.error || `HTTP Error ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      throw new Error('Network error: Backend not reachable');
    }
  },
};
import { authService } from '../services/authService';

// ✅ Correct backend base URL for browser environment
const getBaseURL = () => {
  // Check if we're in a browser environment and the variable is set via client module
  if (typeof window !== 'undefined' && window.REACT_APP_API_BASE_URL) {
    return window.REACT_APP_API_BASE_URL;
  }
  // Check for environment variable in different possible locations
  if (typeof window !== 'undefined' && window.ENV?.REACT_APP_API_BASE_URL) {
    return window.ENV.REACT_APP_API_BASE_URL;
  }
  // Default fallback
  return 'http://localhost:8000';
};

export const chatAPI = {
  /**
   * Send message to chat backend
   */
  sendMessage: async (
    query,
    bookId = 'default-book',
    sessionId = null,
    backendUrlOverride = null
  ) => {
    const backendUrl = backendUrlOverride || getBaseURL();

    // Generate session ID if not provided
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random()
        .toString(36)
        .substr(2, 9)}`;
    }

    if (!query || query.trim().length === 0) {
      throw new Error('Query cannot be empty');
    }

    if (query.length > 1000) {
      throw new Error('Query is too long (max 1000 characters)');
    }

    try {
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          query: query.trim(),
          book_id: bookId,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
            errorData.error ||
            `HTTP Error ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError') {
        throw new Error('Network error: Backend not reachable');
      }
      throw error;
    }
  },

  /**
   * Get conversation history
   */
  getConversationHistory: async (userId, backendUrlOverride = null) => {
    const backendUrl = backendUrlOverride || getBaseURL();

    if (!userId) {
      throw new Error('User ID is required');
    }

    try {
      const response = await fetch(`${backendUrl}/api/v1/chat`, {
        method: 'GET',
        credentials: 'include',
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
            errorData.error ||
            `HTTP Error ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      if (error.name === 'TypeError') {
        throw new Error('Network error: Backend not reachable');
      }
      throw error;
    }
  },
};

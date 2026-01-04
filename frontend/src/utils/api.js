// frontend/src/utils/api.js
// API client utilities for the textbook platform

import { authService } from '../services/authService';

// ✅ Correct & safe base URL handling for browser environment
const getAPIBaseUrl = () => {
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

// ✅ Backend API prefix (IMPORTANT)
const API_PREFIX = '/api/v1';

class ApiClient {
  constructor() {
    this.baseURL = getAPIBaseUrl();
  }

  // ===============================
  // Generic request method
  // ===============================
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${API_PREFIX}${endpoint}`;

    const config = {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
      credentials: 'include', // ✅ allow cookies / sessions
      ...options,
    };

    // ✅ Attach JWT token if available
    const token = await this.getToken();
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, config);

      if (!response.ok) {
        // 🔐 Handle auth errors
        if (response.status === 401 || response.status === 403) {
          localStorage.removeItem('jwt_token');
          localStorage.removeItem('access_token');
        }

        const errorData = await response.json().catch(() => ({}));
        throw new Error(
          errorData.detail ||
            errorData.error ||
            `HTTP Error ${response.status}`
        );
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${url}`, error);
      throw error;
    }
  }

  // ===============================
  // Auth helpers
  // ===============================
  async getToken() {
    return await authService.getAuthToken();
  }

  async signup(userData) {
    return authService.signUp(userData);
  }

  async signin(credentials) {
    return authService.signIn('email', credentials);
  }

  // ===============================
  // Chapter APIs
  // ===============================
  async personalizeChapter(chapterData) {
    return this.request('/chapter/personalize', {
      method: 'POST',
      body: JSON.stringify(chapterData),
    });
  }

  async translateChapter(chapterData) {
    return this.request('/chapter/translate', {
      method: 'POST',
      body: JSON.stringify(chapterData),
    });
  }

  // ===============================
  // User APIs
  // ===============================
  async getUserProfile() {
    return this.request('/user/profile');
  }

  async updateUserProfile(profileData) {
    return this.request('/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData),
    });
  }

  // ===============================
  // Chat API (IMPORTANT FOR YOUR ISSUE)
  // ===============================
  async chat(payload) {
    return this.request('/chat', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }
}

// ✅ Singleton instance
const apiClient = new ApiClient();
export default apiClient;

// ✅ Named exports
export const {
  signup,
  signin,
  personalizeChapter,
  translateChapter,
  getUserProfile,
  updateUserProfile
} = apiClient;

export { apiClient };

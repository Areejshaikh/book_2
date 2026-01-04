import axios from 'axios';

// Get the base URL from environment or default
const getAPIBaseUrl = () => {
  // Check if we're in a browser environment and the variable is set via client module
  if (typeof window !== 'undefined' && window.NEXT_PUBLIC_API_URL) {
    return window.NEXT_PUBLIC_API_URL;
  }
  // Check for environment variable in different possible locations
  if (typeof window !== 'undefined' && window.ENV?.NEXT_PUBLIC_API_URL) {
    return window.ENV.NEXT_PUBLIC_API_URL;
  }
  // Default fallback
  return 'http://localhost:8000/api/v1';
};

const API_BASE_URL = getAPIBaseUrl();

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token if available
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export default apiClient;
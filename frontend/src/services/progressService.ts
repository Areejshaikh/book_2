import { ProgressRecord } from '../types/progress';

const getAPIBaseUrl = () => {
  // Check if we're in a browser environment and the variable is set via client module
  if (typeof window !== 'undefined' && window.NEXT_PUBLIC_API_BASE_URL) {
    return window.NEXT_PUBLIC_API_BASE_URL;
  }
  // Check for environment variable in different possible locations
  if (typeof window !== 'undefined' && window.ENV?.NEXT_PUBLIC_API_BASE_URL) {
    return window.ENV.NEXT_PUBLIC_API_BASE_URL;
  }
  // Default fallback
  return 'http://localhost:8000';
};

const API_BASE_URL = getAPIBaseUrl();

export const getProgressForUser = async (
  userId: number
): Promise<ProgressRecord[]> => {
  try {
    const url = `${API_BASE_URL}/progress/?user_id=${encodeURIComponent(userId)}`;

    const response = await fetch(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include', // ✅ send cookies/session if backend uses auth
    });

    if (!response.ok) {
      // Try to get backend error message
      let errorMessage = `HTTP error! status: ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData?.detail || errorData?.error) {
          errorMessage = errorData.detail || errorData.error;
        }
      } catch {
        // ignore JSON parse errors
      }
      throw new Error(errorMessage);
    }

    return await response.json();
  } catch (error) {
    console.error(`Error fetching progress for user ${userId}:`, error);
    throw error;
  }
};

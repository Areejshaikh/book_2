import { Chapter } from '../types/chapter';

const getAPIBaseUrl = () => {
  // Check if we're in a browser environment and the variable is set via client modul
  // Default fallback
  return 'http://localhost:8000';
};

const API_BASE_URL = getAPIBaseUrl();

// -----------------------------
// Get all chapters
// -----------------------------
export const getAllChapters = async (): Promise<Chapter[]> => {
  try {
    const response = await fetch(`${API_BASE_URL}/chapters/`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include', // ✅ send cookies/session if needed
    });

    if (!response.ok) {
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
    console.error('Error fetching chapters:', error);
    throw error;
  }
};

// -----------------------------
// Get chapter by ID
// -----------------------------
export const getChapterById = async (id: number): Promise<Chapter> => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/chapters/${encodeURIComponent(id)}`,
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
      }
    );

    if (!response.ok) {
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
    console.error(`Error fetching chapter with id ${id}:`, error);
    throw error;
  }
};

import React from 'react';
import { AuthProvider } from '../contexts/AuthContext';
import ChatbotButton from './ChatbotButton';

// Root component that wraps the entire app
const Root = ({ children }) => {
  // Get backend URL from environment or default
  let backendUrl = 'http://localhost:8000';

  if (typeof window !== 'undefined') {
    // Check for environment variable in different possible locations in the browser
    backendUrl = (window as any).BACKEND_URL ||
                 (window as any).REACT_APP_API_BASE_URL ||
                 (window as any).ENV?.REACT_APP_API_BASE_URL ||
                 'http://localhost:8000';
  }

  return (
    <AuthProvider>
      {children}
      <ChatbotButton backendUrl={backendUrl} />
    </AuthProvider>
  );
};

export default Root;
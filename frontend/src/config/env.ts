// Environment Configuration for Frontend

// Default values that can be overridden by environment variables
const config = {
  BACKEND_API_URL: typeof window !== 'undefined'
    ? (window as any).ENV?.BACKEND_API_URL || (window as any).BACKEND_API_URL || 'http://localhost:8000'
    : (process.env && process.env.BACKEND_API_URL) || 'http://localhost:8000',
  CONTEXT7_API_URL: typeof window !== 'undefined'
    ? (window as any).ENV?.CONTEXT7_API_URL || (window as any).CONTEXT7_API_URL || 'https://api.context7.com'
    : (process.env && process.env.CONTEXT7_API_URL) || 'https://api.context7.com',
  APP_NAME: typeof window !== 'undefined'
    ? (window as any).ENV?.APP_NAME || (window as any).APP_NAME || 'Textbook Generator'
    : (process.env && process.env.APP_NAME) || 'Textbook Generator',
  APP_DESCRIPTION: typeof window !== 'undefined'
    ? (window as any).ENV?.APP_DESCRIPTION || (window as any).APP_DESCRIPTION || 'An AI-powered textbook generation platform'
    : (process.env && process.env.APP_DESCRIPTION) || 'An AI-powered textbook generation platform'
};

export default config;
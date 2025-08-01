// Test API connectivity
import { api } from './api';

export const testAPI = async () => {
  try {
    console.log('🧪 Testing API connection...');
    console.log('API Base URL:', process.env.REACT_APP_API_URL);
    
    // Test health endpoint (without /api prefix since it's not a blueprint route)
    const healthUrl = process.env.REACT_APP_API_URL.replace('/api', '') + '/health';
    const response = await fetch(healthUrl);
    const data = await response.json();
    console.log('✅ API Health Check:', data);
    return { success: true, data };
    
  } catch (error) {
    console.error('❌ API Test Failed:', error);
    
    if (error.code === 'ECONNREFUSED') {
      console.error('Backend server is not running on port 5000');
    } else if (error.response?.status === 404) {
      console.error('API endpoint not found - check backend routes');
    } else if (error.message.includes('CORS')) {
      console.error('CORS error - check backend CORS configuration');
    }
    
    return { success: false, error: error.message };
  }
};

// Auto-test on import (for debugging)
if (process.env.NODE_ENV === 'development') {
  setTimeout(() => {
    testAPI();
  }, 2000);
}

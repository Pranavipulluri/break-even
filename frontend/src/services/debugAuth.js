// Debug authentication state
import { api } from './api';

export const debugAuth = () => {
  console.log('🔍 Debug Authentication State');
  console.log('Token in localStorage:', localStorage.getItem('token'));
  console.log('API Base URL:', api.defaults.baseURL);
  
  // Test authenticated request
  const testAuth = async () => {
    try {
      console.log('🧪 Testing authentication...');
      const response = await api.get('/website-builder/test-auth');
      console.log('✅ Auth test successful:', response.data);
      
      // Now test the my-website endpoint
      console.log('🧪 Testing my-website endpoint...');
      const websiteResponse = await api.get('/website-builder/my-website');
      console.log('✅ Website endpoint successful:', websiteResponse.data);
    } catch (error) {
      console.error('❌ Test failed:', error.response?.status, error.response?.data);
      
      if (error.response?.status === 401) {
        console.log('🚨 Token is invalid or expired');
        console.log('Current token:', localStorage.getItem('token'));
      } else if (error.response?.status === 404) {
        console.log('📭 User has no website yet (this is normal for new users)');
      }
    }
  };
  
  testAuth();
};

// Auto-run debug in development
if (process.env.NODE_ENV === 'development') {
  setTimeout(debugAuth, 3000);
}

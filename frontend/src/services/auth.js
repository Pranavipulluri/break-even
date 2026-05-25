import { api } from './api';

export const authService = {
  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },

  verifyToken: async (token) => {
    const response = await api.get('/auth/verify', {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  },

  forgotPassword: async (email) => {
    const response = await api.post('/auth/forgot-password', { email });
    return response.data;
  },

  resetPassword: async (token, newPassword) => {
    const response = await api.post('/auth/reset-password', { token, newPassword });
    return response.data;
  },

  googleLogin: async (idToken) => {
    const response = await api.post('/auth/google', { id_token: idToken });
    return response.data;
  },

  microsoftLogin: async (accessToken) => {
    const response = await api.post('/auth/microsoft', { access_token: accessToken });
    return response.data;
  }
};

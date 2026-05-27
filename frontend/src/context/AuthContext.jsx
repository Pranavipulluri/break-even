import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../services/auth';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        try {
          const userData = await authService.verifyToken(token);
          setUser(userData.user || userData);
        } catch (error) {
          localStorage.removeItem('token');
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const response = await authService.login(email, password);
    setUser(response.user);
    localStorage.setItem('token', response.token);
    return response;
  };

  const register = async (userData) => {
    const response = await authService.register(userData);
    setUser(response.user);
    localStorage.setItem('token', response.token);
    return response;
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  const googleLogin = async (idToken) => {
    const response = await authService.googleLogin(idToken);
    setUser(response.user);
    localStorage.setItem('token', response.token);
    return response;
  };

  const microsoftLogin = async (accessToken) => {
    const response = await authService.microsoftLogin(accessToken);
    setUser(response.user);
    localStorage.setItem('token', response.token);
    return response;
  };

  const value = {
    user,
    login,
    register,
    googleLogin,
    microsoftLogin,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

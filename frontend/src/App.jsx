import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import { AppProvider } from './context/AppContext';
import Layout from './components/common/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';
import Messages from './pages/Messages';
import Analytics from './pages/Analytics';
import QRCode from './pages/QRCode';
import AITools from './pages/AITools';
import Settings from './pages/Settings';
import WebsiteBuilder from './pages/WebsiteBuilder';
import AITestPage from './pages/AITestPage';
import ProtectedRoute from './components/common/ProtectedRoute';

function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <div className="App">
            <Toaster position="top-right" />
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/register" element={<Register />} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              
              <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                <Route path="dashboard" element={<Dashboard />} />
                <Route path="products" element={<Products />} />
                <Route path="messages" element={<Messages />} />
                <Route path="analytics" element={<Analytics />} />
                <Route path="qr-code" element={<QRCode />} />
                <Route path="ai-tools" element={<AITools />} />
                <Route path="settings" element={<Settings />} />
                <Route path="website-builder" element={<WebsiteBuilder />} />
                <Route path="ai-test" element={<AITestPage />} />
              </Route>
            </Routes>
          </div>
        </Router>
      </AppProvider>
    </AuthProvider>
  );
}

export default App;
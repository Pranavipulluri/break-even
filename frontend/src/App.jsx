import { Toaster } from 'react-hot-toast';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Layout from './components/common/Layout';
import ProtectedRoute from './components/common/ProtectedRoute';
import AICopilotDrawer from './components/AICopilotDrawer';
import { AppProvider } from './context/AppContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { TranslationProvider } from './contexts/TranslationContext';
import AITestPage from './pages/AITestPage';
import AITools from './pages/AITools';
import Analytics from './pages/Analytics';
import Dashboard from './pages/Dashboard';
import Discover from './pages/Discover';
import Login from './pages/Login';
import Messages from './pages/Messages';
import Products from './pages/Products';
import QRCode from './pages/QRCode';
import Register from './pages/Register';
import Settings from './pages/Settings';
import WebsiteAnalytics from './pages/WebsiteAnalytics';
import WebsiteBuilder from './pages/WebsiteBuilder';

/**
 * Renders the AI Copilot Drawer only for authenticated users.
 * Uses the logged-in user's ID as the business_id for the copilot.
 */
function CopilotLayer() {
  const { user } = useAuth();
  if (!user) return null;
  const businessId = user._id || user.id || user.business_id || '';
  return <AICopilotDrawer businessId={businessId} />;
}

function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <TranslationProvider>
          <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <div className="App">
              <Toaster position="top-right" />
              <Routes>
                <Route path="/login" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/discover" element={<Discover />} />
                <Route path="/explore" element={<Discover />} />
                <Route path="/" element={<Navigate to="/dashboard" replace />} />
                
                <Route path="/" element={<ProtectedRoute><Layout /></ProtectedRoute>}>
                  <Route path="dashboard" element={<Dashboard />} />
                  <Route path="products" element={<Products />} />
                  <Route path="messages" element={<Messages />} />
                  <Route path="analytics" element={<Analytics />} />
                  <Route path="website-analytics" element={<WebsiteAnalytics />} />
                  <Route path="qr-code" element={<QRCode />} />
                  <Route path="ai-tools" element={<AITools />} />
                  <Route path="settings" element={<Settings />} />
                  <Route path="website-builder" element={<WebsiteBuilder />} />
                  <Route path="ai-test" element={<AITestPage />} />
                </Route>
              </Routes>
              {/* Global AI Copilot Drawer — accessible from every page */}
              <CopilotLayer />
            </div>
          </Router>
        </TranslationProvider>
      </AppProvider>
    </AuthProvider>
  );
}

export default App;
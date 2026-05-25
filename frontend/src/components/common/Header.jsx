import { Bell, LogOut, MessageCircle, User } from 'lucide-react';
import { useState } from 'react';
import { useAuth } from '../../context/AuthContext';
import { useTranslation } from '../../contexts/TranslationContext';
import AIBusinessChatbot from '../AIBusinessChatbot';
import LanguageSelector from '../LanguageSelector';

const Header = () => {
  const { user, logout } = useAuth();
  const { currentLanguage, changeLanguage } = useTranslation();
  const [showChatbot, setShowChatbot] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
      <div className="flex items-center justify-between px-6 py-4">
        <div className="flex items-center space-x-4">
          <h1 className="text-2xl font-bold text-primary-600">Break-even</h1>
          {/* Language Selector */}
          <LanguageSelector
            currentLanguage={currentLanguage}
            onLanguageChange={changeLanguage}
            position="inline"
            compact={true}
          />
        </div>
        
        <div className="flex items-center space-x-4">
          {/* AI Business Chatbot Icon */}
          <button 
            onClick={() => setShowChatbot(!showChatbot)}
            className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors relative"
            title="AI Business Assistant"
          >
            <MessageCircle size={20} />
            <span className="absolute -top-1 -right-1 w-2 h-2 bg-green-500 rounded-full"></span>
          </button>
          
          <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors">
            <Bell size={20} />
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
              <User size={16} className="text-white" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-800">{user?.name}</p>
              <p className="text-xs text-gray-600">{user?.email}</p>
            </div>
          </div>
          
          <button 
            onClick={logout}
            className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut size={20} />
          </button>
        </div>
      </div>
      
      {/* AI Business Chatbot Modal */}
      {showChatbot && (
        <AIBusinessChatbot 
          isOpen={showChatbot} 
          onClose={() => setShowChatbot(false)} 
        />
      )}
    </header>
  );
};

export default Header;
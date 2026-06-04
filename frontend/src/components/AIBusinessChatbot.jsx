import { Bot, Maximize2, Minimize2, Send, User, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTranslation } from '../context/TranslationContext';
import { api } from '../services/api';

const AIBusinessChatbot = ({ isOpen, onClose }) => {
  const { t: translate, currentLanguage } = useTranslation();
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Welcome message when chatbot opens
      const welcomeMessage = {
        id: Date.now(),
        type: 'bot',
        content: translate('Hello! I\'m your AI business co-partner. I\'m here to help you grow your business, analyze performance, provide insights, and answer any questions you might have. How can I assist you today?'),
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
  }, [isOpen, translate]);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setLoading(true);

    try {
      // Call Gemini API for business co-partner response via Axios
      const response = await api.post('/ai/business-chat', {
        message: inputMessage,
        language: currentLanguage,
        user_context: {
          name: user?.name,
          business_type: user?.business_category,
          business_name: user?.business_name || user?.name
        },
        conversation_history: messages.slice(-5) // Last 5 messages for context
      });

      const data = response.data;
      const botMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: data.response,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: translate('Sorry, I encountered an error. Please try again.'),
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const quickActions = [
    translate('Analyze my business performance'),
    translate('How can I increase sales?'),
    translate('Marketing strategy ideas'),
    translate('Customer retention tips'),
    translate('Financial insights'),
    translate('Help with website content')
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      <div className={`bg-white rounded-xl shadow-2xl border border-gray-200 transition-all duration-300 ${
        isMinimized ? 'w-80 h-16' : 'w-96 h-[500px]'
      }`}>
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-t-xl">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-white/20 rounded-full flex items-center justify-center">
              <Bot size={18} className="text-white" />
            </div>
            <div className="text-white">
              <h3 className="font-semibold text-sm">{translate('AI Business Partner')}</h3>
              <p className="text-xs text-white/80">{translate('Your smart business assistant')}</p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setIsMinimized(!isMinimized)}
              className="p-1 text-white/80 hover:text-white hover:bg-white/20 rounded transition-colors"
            >
              {isMinimized ? <Maximize2 size={14} /> : <Minimize2 size={14} />}
            </button>
            <button
              onClick={onClose}
              className="p-1 text-white/80 hover:text-white hover:bg-white/20 rounded transition-colors"
            >
              <X size={14} />
            </button>
          </div>
        </div>

        {!isMinimized && (
          <>
            {/* Messages */}
            <div className="flex-1 p-4 h-80 overflow-y-auto space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`flex items-start space-x-2 max-w-[80%] ${
                    message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                  }`}>
                    <div className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${
                      message.type === 'user' 
                        ? 'bg-primary-500' 
                        : 'bg-gradient-to-r from-secondary-500 to-primary-500'
                    }`}>
                      {message.type === 'user' ? (
                        <User size={12} className="text-white" />
                      ) : (
                        <Bot size={12} className="text-white" />
                      )}
                    </div>
                    <div className={`px-3 py-2 rounded-lg text-sm ${
                      message.type === 'user'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {message.content}
                    </div>
                  </div>
                </div>
              ))}
              
              {loading && (
                <div className="flex justify-start">
                  <div className="flex items-start space-x-2">
                    <div className="w-6 h-6 bg-gradient-to-r from-secondary-500 to-primary-500 rounded-full flex items-center justify-center">
                      <Bot size={12} className="text-white" />
                    </div>
                    <div className="bg-gray-100 px-3 py-2 rounded-lg text-sm">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Quick Actions */}
            {messages.length <= 1 && (
              <div className="p-4 border-t border-gray-100">
                <p className="text-xs text-gray-600 mb-2">{translate('Quick actions:')}</p>
                <div className="flex flex-wrap gap-1">
                  {quickActions.slice(0, 3).map((action, index) => (
                    <button
                      key={index}
                      onClick={() => setInputMessage(action)}
                      className="text-xs px-2 py-1 bg-gray-100 hover:bg-gray-200 rounded-full transition-colors"
                    >
                      {action}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-4 border-t border-gray-200">
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={translate('Ask me anything about your business...')}
                  className="flex-1 px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                  disabled={loading}
                />
                <button
                  onClick={sendMessage}
                  disabled={loading || !inputMessage.trim()}
                  className="p-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Send size={16} />
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default AIBusinessChatbot;
import React, { useState, useEffect } from 'react';
import { Sparkles, Image as ImageIcon, MessageSquare, Lightbulb, Download, Copy, Wand2 } from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';
import Modal from '../components/common/Modal';

const AITools = () => {
  const [activeTab, setActiveTab] = useState('content');
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  const [generatedImage, setGeneratedImage] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [conversationId, setConversationId] = useState(null);

  const generateContent = async (contentType, prompt, businessContext = '') => {
    try {
      setLoading(true);
      const response = await api.post('/ai-tools/generate-content', {
        content_type: contentType,
        prompt,
        business_context: businessContext
      });
      
      setGeneratedContent(response.data.content);
      toast.success('Content generated successfully!');
    } catch (error) {
      toast.error('Failed to generate content');
    } finally {
      setLoading(false);
    }
  };

  const generateImage = async (prompt, imageType = 'poster', style = 'modern') => {
    try {
      setLoading(true);
      const response = await api.post('/ai-tools/generate-image', {
        prompt,
        image_type: imageType,
        style
      });
      
      setGeneratedImage(response.data.image_data);
      toast.success('Image generated successfully!');
    } catch (error) {
      toast.error('Failed to generate image');
    } finally {
      setLoading(false);
    }
  };

  const getBusinessSuggestions = async (suggestionType = 'general') => {
    try {
      setLoading(true);
      const response = await api.post('/ai-tools/business-suggestions', {
        type: suggestionType
      });
      
      setSuggestions(response.data.suggestions.suggestions);
      toast.success('Suggestions generated!');
    } catch (error) {
      toast.error('Failed to get suggestions');
    } finally {
      setLoading(false);
    }
  };

  const sendChatMessage = async (message) => {
    try {
      const response = await api.post('/ai-tools/chatbot', {
        message,
        conversation_id: conversationId
      });
      
      const newMessages = [
        ...chatMessages,
        { type: 'user', content: message, timestamp: new Date() },
        { type: 'bot', content: response.data.response, timestamp: new Date() }
      ];
      
      setChatMessages(newMessages);
      setConversationId(response.data.conversation_id);
      setChatInput('');
    } catch (error) {
      toast.error('Failed to send message');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const ContentGenerator = () => {
    const [contentType, setContentType] = useState('product_description');
    const [prompt, setPrompt] = useState('');
    const [businessContext, setBusinessContext] = useState('');

    return (
      <div className="space-y-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate Content</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Content Type
              </label>
              <select
                value={contentType}
                onChange={(e) => setContentType(e.target.value)}
                className="input-field"
              >
                <option value="product_description">Product Description</option>
                <option value="marketing_copy">Marketing Copy</option>
                <option value="social_media">Social Media Post</option>
                <option value="email_campaign">Email Campaign</option>
                <option value="blog_post">Blog Post</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                What do you want to create? *
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows="3"
                className="input-field"
                placeholder="Describe what you want to create..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Context (Optional)
              </label>
              <input
                type="text"
                value={businessContext}
                onChange={(e) => setBusinessContext(e.target.value)}
                className="input-field"
                placeholder="Additional context about your business..."
              />
            </div>

            <button
              onClick={() => generateContent(contentType, prompt, businessContext)}
              disabled={!prompt || loading}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Wand2 size={16} />
              )}
              <span>{loading ? 'Generating...' : 'Generate Content'}</span>
            </button>
          </div>
        </div>

        {generatedContent && (
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Generated Content</h3>
              <button
                onClick={() => copyToClipboard(generatedContent)}
                className="btn-secondary flex items-center space-x-2"
              >
                <Copy size={16} />
                <span>Copy</span>
              </button>
            </div>
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="whitespace-pre-wrap text-gray-800">{generatedContent}</p>
            </div>
          </div>
        )}
      </div>
    );
  };

  const ImageGenerator = () => {
    const [prompt, setPrompt] = useState('');
    const [imageType, setImageType] = useState('poster');
    const [style, setStyle] = useState('modern');

    return (
      <div className="space-y-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Generate Images</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Image Type
              </label>
              <select
                value={imageType}
                onChange={(e) => setImageType(e.target.value)}
                className="input-field"
              >
                <option value="poster">Marketing Poster</option>
                <option value="logo">Business Logo</option>
                <option value="product_image">Product Image</option>
                <option value="social_media">Social Media Graphics</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Style
              </label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value)}
                className="input-field"
              >
                <option value="modern">Modern</option>
                <option value="classic">Classic</option>
                <option value="minimalist">Minimalist</option>
                <option value="vibrant">Vibrant</option>
                <option value="professional">Professional</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Describe your image *
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows="3"
                className="input-field"
                placeholder="Describe the image you want to create..."
              />
            </div>

            <button
              onClick={() => generateImage(prompt, imageType, style)}
              disabled={!prompt || loading}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <ImageIcon size={16} />
              )}
              <span>{loading ? 'Generating...' : 'Generate Image'}</span>
            </button>
          </div>
        </div>

        {generatedImage && (
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Generated Image</h3>
              <a
                href={generatedImage}
                download="generated-image.png"
                className="btn-secondary flex items-center space-x-2"
              >
                <Download size={16} />
                <span>Download</span>
              </a>
            </div>
            <div className="text-center">
              <img
                src={generatedImage}
                alt="Generated"
                className="max-w-full h-auto rounded-lg shadow-md mx-auto"
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  const BusinessSuggestions = () => {
    const [suggestionType, setSuggestionType] = useState('general');

    const getPriorityColor = (priority) => {
      switch (priority) {
        case 'high': return 'bg-red-100 text-red-800';
        case 'medium': return 'bg-yellow-100 text-yellow-800';
        case 'low': return 'bg-green-100 text-green-800';
        default: return 'bg-gray-100 text-gray-800';
      }
    };

    return (
      <div className="space-y-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Get Business Suggestions</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Suggestion Type
              </label>
              <select
                value={suggestionType}
                onChange={(e) => setSuggestionType(e.target.value)}
                className="input-field"
              >
                <option value="general">General Business</option>
                <option value="marketing">Marketing</option>
                <option value="products">Products</option>
                <option value="website">Website</option>
              </select>
            </div>

            <button
              onClick={() => getBusinessSuggestions(suggestionType)}
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center space-x-2"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Lightbulb size={16} />
              )}
              <span>{loading ? 'Generating...' : 'Get Suggestions'}</span>
            </button>
          </div>
        </div>

        {suggestions.length > 0 && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Suggestions</h3>
            <div className="space-y-4">
              {suggestions.map((suggestion, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-medium text-gray-900">{suggestion.title}</h4>
                    <div className="flex space-x-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${getPriorityColor(suggestion.priority)}`}>
                        {suggestion.priority}
                      </span>
                      <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                        {suggestion.category}
                      </span>
                    </div>
                  </div>
                  <p className="text-gray-600 text-sm mb-2">{suggestion.description}</p>
                  <div className="flex justify-between items-center text-xs text-gray-500">
                    <span>Effort: {suggestion.effort}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const AIChat = () => {
    const handleSubmit = (e) => {
      e.preventDefault();
      if (chatInput.trim()) {
        sendChatMessage(chatInput.trim());
      }
    };

    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Business Assistant</h3>
        
        <div className="h-96 border border-gray-200 rounded-lg flex flex-col">
          <div className="flex-1 p-4 overflow-y-auto space-y-4">
            {chatMessages.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
                <MessageSquare size={48} className="mx-auto mb-4 text-gray-300" />
                <p>Ask me anything about your business!</p>
                <p className="text-sm">I can help with marketing, products, customers, and more.</p>
              </div>
            ) : (
              chatMessages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      message.type === 'user'
                        ? 'bg-primary-500 text-white'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    <p className="text-sm">{message.content}</p>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <form onSubmit={handleSubmit} className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Type your message..."
                className="flex-1 input-field"
              />
              <button
                type="submit"
                disabled={!chatInput.trim()}
                className="btn-primary"
              >
                Send
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Tools</h1>
        <p className="text-gray-600 mt-2">Powered by artificial intelligence to help grow your business</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'content', name: 'Content Generator', icon: Wand2 },
            { id: 'images', name: 'Image Generator', icon: ImageIcon },
            { id: 'suggestions', name: 'Business Suggestions', icon: Lightbulb },
            { id: 'chat', name: 'AI Assistant', icon: MessageSquare },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon size={16} />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'content' && <ContentGenerator />}
      {activeTab === 'images' && <ImageGenerator />}
      {activeTab === 'suggestions' && <BusinessSuggestions />}
      {activeTab === 'chat' && <AIChat />}
    </div>
  );
};

export default AITools;
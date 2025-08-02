import React, { useState, useEffect } from 'react';
import { Sparkles, Image as ImageIcon, MessageSquare, Lightbulb, Download, Copy, Wand2, Zap, Brain, Palette, FileText, Camera } from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const AITools = () => {
  const [activeTab, setActiveTab] = useState('content');
  const [loading, setLoading] = useState(false);
  const [generatedContent, setGeneratedContent] = useState('');
  const [generatedImage, setGeneratedImage] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [conversationId, setConversationId] = useState(null);
  const [emailCampaignResults, setEmailCampaignResults] = useState(null);
  const [sendingEmails, setSendingEmails] = useState(false);
  const [showEmailConfirmation, setShowEmailConfirmation] = useState(false);
  const [currentGenerationId, setCurrentGenerationId] = useState(null);
  const [emailSubject, setEmailSubject] = useState('Marketing Campaign Email');

  const tabs = [
    { 
      id: 'content', 
      name: 'Content Generator', 
      icon: FileText, 
      description: 'Create engaging content with AI',
      gradient: 'from-blue-500 to-indigo-600'
    },
    { 
      id: 'images', 
      name: 'Image Generator', 
      icon: Camera, 
      description: 'Generate stunning visuals',
      gradient: 'from-purple-500 to-pink-600'
    },
    { 
      id: 'suggestions', 
      name: 'Business Coach', 
      icon: Brain, 
      description: 'Get AI-powered business advice',
      gradient: 'from-green-500 to-emerald-600'
    },
    { 
      id: 'chat', 
      name: 'AI Assistant', 
      icon: MessageSquare, 
      description: '24/7 business support chat',
      gradient: 'from-orange-500 to-red-600'
    },
  ];

  const generateContent = async (contentType, prompt, businessContext = '') => {
    try {
      setLoading(true);
      const response = await api.post('/ai-tools/generate-content', {
        content_type: contentType,
        prompt,
        business_context: businessContext
      });
      
      setGeneratedContent(response.data.content);
      
      // Check if email campaign requires confirmation
      if (response.data.requires_confirmation && response.data.generation_id) {
        setCurrentGenerationId(response.data.generation_id);
        setShowEmailConfirmation(true);
        toast.success('Email content generated! Please confirm to send to customers.');
      } else {
        toast.success('Content generated successfully!');
      }
      if (response.data.mock_email_results) {
        setEmailCampaignResults(response.data.mock_email_results);
        if (response.data.mock_email_results.success) {
          toast.success(`Content generated and mock email campaign sent to ${response.data.mock_email_results.summary.successful_sends} recipients!`);
        } else {
          toast.success('Content generated successfully!');
          toast.error('Mock email sending failed');
        }
      } else {
        toast.success('Content generated successfully!');
      }
    } catch (error) {
      toast.error('Failed to generate content');
    } finally {
      setLoading(false);
    }
  };

  const generateImage = async (prompt, imageType = 'poster', style = 'modern') => {
    try {
      setLoading(true);
      const response = await api.post('/ai-tools/dev/generate-image', {
        prompt,
        image_type: imageType,
        style
      });
      
      if (response.data.success) {
        setGeneratedImage(response.data.image_data);
        setGeneratedContent(response.data.concept || ''); // Store the AI concept
        toast.success('Image concept generated successfully!');
      } else {
        toast.error(response.data.error || 'Failed to generate image');
      }
    } catch (error) {
      toast.error('Failed to generate image');
    } finally {
      setLoading(false);
    }
  };

  const sendMockEmails = async (emailContent, emailSubject = 'Marketing Campaign Email') => {
    try {
      setSendingEmails(true);
      setEmailCampaignResults(null);
      
      const response = await api.post('/ai-tools/mock-email-send', {
        email_content: emailContent,
        email_subject: emailSubject
      });
      
      if (response.data.success) {
        setEmailCampaignResults(response.data);
        toast.success(`Mock email campaign sent! ${response.data.summary.successful_sends} emails delivered successfully!`);
      } else {
        toast.error(response.data.error || 'Failed to send mock emails');
      }
    } catch (error) {
      toast.error('Failed to send mock emails');
    } finally {
      setSendingEmails(false);
    }
  };

  const confirmEmailCampaign = async (confirmed) => {
    if (!confirmed) {
      setShowEmailConfirmation(false);
      setCurrentGenerationId(null);
      toast.info('Email campaign cancelled.');
      return;
    }

    try {
      setSendingEmails(true);
      setEmailCampaignResults(null);
      
      const response = await api.post('/ai-tools/confirm-email-campaign', {
        generation_id: currentGenerationId,
        email_subject: emailSubject,
        confirmed: true
      });
      
      if (response.data.success) {
        setEmailCampaignResults(response.data);
        setShowEmailConfirmation(false);
        setCurrentGenerationId(null);
        toast.success(`Email campaign sent! ${response.data.summary.successful_sends} emails delivered successfully!`);
      } else {
        toast.error(response.data.error || 'Failed to send email campaign');
      }
    } catch (error) {
      toast.error('Failed to send email campaign');
    } finally {
      setSendingEmails(false);
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
      
      // Add bot response to chat
      const botMessage = { 
        type: 'bot', 
        content: response.data.response, 
        timestamp: new Date() 
      };
      setChatMessages(prev => [...prev, botMessage]);
      setConversationId(response.data.conversation_id);
      
      return response.data;
    } catch (error) {
      console.error('Chat error:', error);
      toast.error('Failed to send message');
      throw error;
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

    const contentTypes = [
      { value: 'product_description', label: 'Product Description', icon: '📦' },
      { value: 'marketing_copy', label: 'Marketing Copy', icon: '📢' },
      { value: 'social_media', label: 'Social Media Post', icon: '📱' },
      { value: 'email_campaign', label: 'Email Campaign', icon: '📧' },
      { value: 'blog_post', label: 'Blog Post', icon: '📝' },
    ];

    return (
      <div className="space-y-8">
        {/* Content Type Selection */}
        <div className="card">
          <h3 className="heading-3 text-gray-900 mb-6">Choose Content Type</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {contentTypes.map((type) => (
              <button
                key={type.value}
                onClick={() => setContentType(type.value)}
                className={`p-4 rounded-xl border-2 transition-all duration-200 text-center hover:scale-105 ${
                  contentType === type.value
                    ? 'border-primary-500 bg-primary-50 text-primary-700 shadow-lg'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="text-2xl mb-2">{type.icon}</div>
                <div className="font-medium text-sm">{type.label}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Input Form */}
        <div className="card">
          <h3 className="heading-3 text-gray-900 mb-6">Generate Content</h3>
          
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                What would you like to create? *
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows="4"
                className="input-field resize-none"
                placeholder="Describe what you want to create in detail..."
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
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
              className="btn-primary w-full btn-lg relative overflow-hidden group"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-primary-600 to-primary-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <div className="relative flex items-center justify-center space-x-2">
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Wand2 size={18} />
                    <span>Generate Content</span>
                  </>
                )}
              </div>
            </button>
          </div>
        </div>

        {/* Generated Content */}
        {generatedContent && (
          <div className="card border border-green-200 bg-gradient-to-br from-green-50 to-emerald-50">
            <div className="flex items-center justify-between mb-6">
              <h3 className="heading-3 text-green-900 flex items-center space-x-2">
                <Sparkles className="text-green-600" size={20} />
                <span>Generated Content</span>
              </h3>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(generatedContent);
                  toast.success('Copied to clipboard!');
                }}
                className="btn-secondary flex items-center space-x-2"
              >
                <Copy size={16} />
                <span>Copy</span>
              </button>
            </div>
            
            <div className="bg-white/80 backdrop-blur-sm border border-green-200 rounded-xl p-6">
              <pre className="whitespace-pre-wrap text-gray-800 font-sans leading-relaxed">
                {generatedContent}
              </pre>
            </div>

            {/* Auto Email Campaign Notification for Email Content */}
            {contentType === 'email_campaign' && (
              <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-xl">
                <div className="flex items-center mb-4">
                  <h4 className="text-lg font-semibold text-green-900 flex items-center space-x-2">
                    <span>✅</span>
                    <span>Email Campaign Auto-Sent!</span>
                  </h4>
                </div>
                <p className="text-green-700 text-sm">
                  Your email campaign has been automatically sent to 20 mock recipients including:
                  <br />
                  <strong>pulluripranavi@gmail.com</strong> and <strong>visesh.bappana@gmail.com</strong>
                  <br />
                  Check the results below for delivery details.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Mock Email Campaign Results */}
        {emailCampaignResults && (
          <div className="card border border-blue-200 bg-gradient-to-br from-blue-50 to-cyan-50">
            <div className="flex items-center justify-between mb-6">
              <h3 className="heading-3 text-blue-900 flex items-center space-x-2">
                <span>📊</span>
                <span>Mock Email Campaign Results</span>
              </h3>
            </div>
            
            <div className="bg-white/80 backdrop-blur-sm border border-blue-200 rounded-xl p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="text-center p-4 bg-green-100 rounded-lg">
                  <div className="text-2xl font-bold text-green-800">{emailCampaignResults.summary.total_recipients}</div>
                  <div className="text-sm text-green-600">Total Recipients</div>
                </div>
                <div className="text-center p-4 bg-blue-100 rounded-lg">
                  <div className="text-2xl font-bold text-blue-800">{emailCampaignResults.summary.successful_sends}</div>
                  <div className="text-sm text-blue-600">Successfully Sent</div>
                </div>
                <div className="text-center p-4 bg-red-100 rounded-lg">
                  <div className="text-2xl font-bold text-red-800">{emailCampaignResults.summary.failed_sends}</div>
                  <div className="text-sm text-red-600">Failed</div>
                </div>
                <div className="text-center p-4 bg-yellow-100 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-800">{emailCampaignResults.summary.success_rate}</div>
                  <div className="text-sm text-yellow-600">Success Rate</div>
                </div>
              </div>

              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold text-green-800 mb-2">✅ Successfully Sent ({emailCampaignResults.sent_emails.length})</h4>
                  <div className="max-h-40 overflow-y-auto bg-green-50 p-3 rounded border">
                    {emailCampaignResults.sent_emails.slice(0, 10).map((email, index) => (
                      <div key={index} className="text-sm text-green-700 py-1 border-b border-green-200 last:border-b-0">
                        📧 {email.email} - {email.status} (ID: {email.message_id})
                      </div>
                    ))}
                    {emailCampaignResults.sent_emails.length > 10 && (
                      <div className="text-sm text-green-600 pt-2 font-medium">
                        ... and {emailCampaignResults.sent_emails.length - 10} more
                      </div>
                    )}
                  </div>
                </div>

                {emailCampaignResults.failed_emails.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-red-800 mb-2">❌ Failed Sends ({emailCampaignResults.failed_emails.length})</h4>
                    <div className="max-h-32 overflow-y-auto bg-red-50 p-3 rounded border">
                      {emailCampaignResults.failed_emails.map((email, index) => (
                        <div key={index} className="text-sm text-red-700 py-1 border-b border-red-200 last:border-b-0">
                          ❌ {email.email} - {email.error}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
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

    const imageTypes = [
      { value: 'poster', label: 'Marketing Poster', icon: '🎨' },
      { value: 'logo', label: 'Business Logo', icon: '🏷' },
      { value: 'product_image', label: 'Product Image', icon: '📸' },
      { value: 'social_media', label: 'Social Media', icon: '📱' },
    ];

    const styles = [
      { value: 'modern', label: 'Modern', preview: '🎯' },
      { value: 'classic', label: 'Classic', preview: '🏛' },
      { value: 'minimalist', label: 'Minimalist', preview: '⚪' },
      { value: 'vibrant', label: 'Vibrant', preview: '🌈' },
      { value: 'professional', label: 'Professional', preview: '💼' },
    ];

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
                <option value="poster">Business Poster</option>
                <option value="product">Product Image</option>
                <option value="banner">Marketing Banner</option>
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
                <option value="professional">Professional</option>
                <option value="modern">Modern</option>
                <option value="creative">Creative</option>
                <option value="minimal">Minimal</option>
                <option value="vintage">Vintage</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                rows="3"
                className="input-field"
                placeholder="Describe the image you want to generate..."
              />
            </div>

            <button
              onClick={() => generateImage(prompt, imageType, style)}
              disabled={!prompt || loading}
              className="btn-primary w-full"
            >
              {loading ? 'Generating...' : 'Generate Image'}
            </button>
          </div>
        </div>

        {/* Image Preview */}
        {generatedImage && (
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Generated Image Concept</h3>
              <a
                href={generatedImage}
                download="generated-image.png"
                className="btn-secondary flex items-center space-x-2"
              >
                <Download size={16} />
                <span>Download</span>
              </a>
            </div>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="text-md font-medium text-gray-800 mb-2">Visual Mockup</h4>
                <img
                  src={generatedImage}
                  alt="Generated"
                  className="max-w-full h-auto rounded-lg shadow-md"
                />
              </div>
              
              {generatedContent && (
                <div>
                  <h4 className="text-md font-medium text-gray-800 mb-2">AI Design Concept</h4>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <p className="text-gray-700 text-sm leading-relaxed">{generatedContent}</p>
                  </div>
                  <div className="mt-3">
                    <button
                      onClick={() => navigator.clipboard.writeText(generatedContent)}
                      className="btn-secondary flex items-center space-x-2 text-sm"
                    >
                      <Copy size={14} />
                      <span>Copy Concept</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  const AIAssistant = () => {
    const [chatLoading, setChatLoading] = useState(false);

    const handleSendMessage = async (e) => {
      e.preventDefault();
      if (!chatInput.trim() || chatLoading) return;

      const message = chatInput.trim();
      setChatInput('');
      setChatLoading(true);

      // Add user message immediately
      const userMessage = { type: 'user', content: message, timestamp: new Date() };
      setChatMessages(prev => [...prev, userMessage]);

      try {
        const response = await sendChatMessage(message);
        // sendChatMessage already updates the chat messages
      } catch (error) {
        // Add error message if needed
        const errorMessage = { 
          type: 'bot', 
          content: 'Sorry, I encountered an error. Please try again.', 
          timestamp: new Date() 
        };
        setChatMessages(prev => [...prev, errorMessage]);
      } finally {
        setChatLoading(false);
      }
    };

    return (
      <div className="space-y-6">
        <div className="card">
          <div className="flex items-center justify-between mb-6">
            <h3 className="heading-3 text-gray-900 flex items-center space-x-2">
              <MessageSquare className="text-orange-500" size={20} />
              <span>AI Business Assistant</span>
            </h3>
            <div className="flex items-center space-x-2 text-sm text-gray-500">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span>Powered by Gemini AI</span>
            </div>
          </div>

          {/* Chat Messages */}
          <div className="bg-gray-50 rounded-xl p-4 h-96 overflow-y-auto mb-4 space-y-4">
            {chatMessages.length === 0 ? (
              <div className="text-center text-gray-500 mt-20">
                <MessageSquare size={48} className="mx-auto mb-4 text-gray-300" />
                <h4 className="font-medium mb-2">Start a conversation!</h4>
                <p className="text-sm">Ask me anything about your business - marketing, operations, growth strategies, and more.</p>
                <div className="mt-4 flex flex-wrap gap-2 justify-center">
                  <button
                    onClick={() => setChatInput("How can I improve my business marketing?")}
                    className="px-3 py-1 bg-white text-gray-600 rounded-full text-xs hover:bg-gray-100 transition-colors"
                  >
                    Marketing tips
                  </button>
                  <button
                    onClick={() => setChatInput("What are some cost-effective business strategies?")}
                    className="px-3 py-1 bg-white text-gray-600 rounded-full text-xs hover:bg-gray-100 transition-colors"
                  >
                    Cost strategies
                  </button>
                  <button
                    onClick={() => setChatInput("How can I increase customer retention?")}
                    className="px-3 py-1 bg-white text-gray-600 rounded-full text-xs hover:bg-gray-100 transition-colors"
                  >
                    Customer retention
                  </button>
                </div>
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
                        : 'bg-white text-gray-800 shadow-sm border'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <div className={`text-xs mt-1 ${
                      message.type === 'user' ? 'text-primary-100' : 'text-gray-500'
                    }`}>
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {chatLoading && (
              <div className="flex justify-start">
                <div className="bg-white text-gray-800 shadow-sm border px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-500"></div>
                    <span className="text-sm">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Message Input */}
          <form onSubmit={handleSendMessage} className="flex space-x-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              placeholder="Ask me anything about your business..."
              className="flex-1 input-field"
              disabled={chatLoading}
            />
            <button
              type="submit"
              disabled={!chatInput.trim() || chatLoading}
              className="btn-primary px-6 flex items-center space-x-2"
            >
              {chatLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <>
                  <MessageSquare size={16} />
                  <span>Send</span>
                </>
              )}
            </button>
          </form>
        </div>

        {/* Business Context Info */}
        <div className="card bg-gradient-to-br from-orange-50 to-red-50 border border-orange-200">
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <Lightbulb className="text-orange-500" size={20} />
            </div>
            <div>
              <h4 className="font-semibold text-orange-900 mb-1">Smart Business Assistant</h4>
              <p className="text-orange-700 text-sm">
                This AI assistant understands your business context and provides personalized advice. 
                Ask about marketing strategies, operational improvements, customer engagement, financial planning, and more!
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="heading-1 mb-4">AI-Powered Tools</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Leverage the power of artificial intelligence to create content, generate images, 
          and get business insights that help your business grow.
        </p>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`card-hover text-left p-6 transition-all duration-300 relative overflow-hidden ${
              activeTab === tab.id 
                ? `bg-gradient-to-br ${tab.gradient} text-white shadow-colored` 
                : 'hover:shadow-medium'
            }`}
          >
            <div className="relative z-10">
              <tab.icon size={24} className={`mb-3 ${activeTab === tab.id ? 'text-white' : 'text-gray-600'}`} />
              <h3 className={`font-semibold mb-2 ${activeTab === tab.id ? 'text-white' : 'text-gray-900'}`}>
                {tab.name}
              </h3>
              <p className={`text-sm ${activeTab === tab.id ? 'text-white/80' : 'text-gray-600'}`}>
                {tab.description}
              </p>
            </div>
            
            {activeTab === tab.id && (
              <div className="absolute top-2 right-2">
                <div className="w-3 h-3 bg-white/30 rounded-full animate-pulse"></div>
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="min-h-[600px]">
        {activeTab === 'content' && <ContentGenerator />}
        {activeTab === 'images' && <ImageGenerator />}
        {activeTab === 'suggestions' && (
          <div className="card text-center py-16">
            <Brain size={48} className="text-green-500 mx-auto mb-4" />
            <h3 className="heading-3 text-gray-900 mb-2">Business Coach Coming Soon</h3>
            <p className="text-gray-600">AI-powered business suggestions and coaching features are in development.</p>
          </div>
        )}
        {activeTab === 'chat' && <AIAssistant />}
      </div>
    </div>
  );
};

export default AITools;
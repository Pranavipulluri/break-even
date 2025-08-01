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
      toast.success('Content generated successfully!');
    } catch (error) {
      toast.error('Failed to generate content');
    } finally {
      setLoading(false);
    }
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
      <div className="space-y-8">
        {/* Image Type & Style Selection */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="card">
            <h3 className="heading-3 text-gray-900 mb-6">Image Type</h3>
            <div className="grid grid-cols-2 gap-3">
              {imageTypes.map((type) => (
                <button
                  key={type.value}
                  onClick={() => setImageType(type.value)}
                  className={`p-4 rounded-xl border-2 transition-all text-center hover:scale-105 ${
                    imageType === type.value
                      ? 'border-purple-500 bg-purple-50 text-purple-700 shadow-lg'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="text-xl mb-2">{type.icon}</div>
                  <div className="font-medium text-xs">{type.label}</div>
                </button>
              ))}
            </div>
          </div>

          <div className="card">
            <h3 className="heading-3 text-gray-900 mb-6">Style</h3>
            <div className="grid grid-cols-2 gap-3">
              {styles.map((styleOption) => (
                <button
                  key={styleOption.value}
                  onClick={() => setStyle(styleOption.value)}
                  className={`p-4 rounded-xl border-2 transition-all text-center hover:scale-105 ${
                    style === styleOption.value
                      ? 'border-pink-500 bg-pink-50 text-pink-700 shadow-lg'
                      : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                  }`}
                >
                  <div className="text-xl mb-2">{styleOption.preview}</div>
                  <div className="font-medium text-xs">{styleOption.label}</div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Prompt Input */}
        <div className="card">
          <h3 className="heading-3 text-gray-900 mb-6 flex items-center space-x-2">
            <Palette className="text-purple-600" />
            <span>Describe Your Image</span>
          </h3>
          
          <div className="space-y-6">
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows="4"
              className="input-field resize-none"
              placeholder="Describe the image you want to create in detail..."
            />

            <button
              onClick={() => {
                // generateImage(prompt, imageType, style);
                toast.success('Image generation feature coming soon!');
              }}
              disabled={!prompt || loading}
              className="btn-primary w-full btn-lg bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700"
            >
              {loading ? (
                <div className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Generating...</span>
                </div>
              ) : (
                <div className="flex items-center justify-center space-x-2">
                  <ImageIcon size={18} />
                  <span>Generate Image</span>
                </div>
              )}
            </button>
          </div>
        </div>

        {/* Image Preview */}
        {generatedImage && (
          <div className="card border border-purple-200 bg-gradient-to-br from-purple-50 to-pink-50">
            <div className="flex items-center justify-between mb-6">
              <h3 className="heading-3 text-purple-900">Generated Image</h3>
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
                className="max-w-full h-auto rounded-xl shadow-large mx-auto"
              />
            </div>
          </div>
        )}
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
        {activeTab === 'chat' && (
          <div className="card text-center py-16">
            <MessageSquare size={48} className="text-orange-500 mx-auto mb-4" />
            <h3 className="heading-3 text-gray-900 mb-2">AI Assistant Coming Soon</h3>
            <p className="text-gray-600">24/7 AI business assistant is being developed for you.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AITools;

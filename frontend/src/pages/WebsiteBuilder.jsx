import React, { useState, useEffect } from 'react';
import { Globe, Palette, Settings, Eye, Edit, Save, Bot, Rocket } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { api } from '../services/api';
import { aiServices } from '../services/aiServices';
import WebsitePreview from '../components/website/WebsitePreview';
import toast from 'react-hot-toast';

// Debug auth in development
if (process.env.NODE_ENV === 'development') {
  import('../services/debugAuth');
}

const WebsiteBuilder = () => {
  const [currentWebsite, setCurrentWebsite] = useState(null);
  const [themes, setThemes] = useState({});
  const [colorSchemes, setColorSchemes] = useState({});
  const [loading, setLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [deployedUrl, setDeployedUrl] = useState(null);
  
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm();

  const selectedBusinessType = watch('business_type');
  const selectedColorTheme = watch('color_theme');

  useEffect(() => {
    fetchThemes();
    fetchCurrentWebsite();
  }, []);

  const fetchThemes = async () => {
    try {
      const response = await api.get('/website-builder/themes');
      setThemes(response.data.themes);
      setColorSchemes(response.data.colorSchemes);
    } catch (error) {
      toast.error('Failed to fetch themes');
    }
  };

  const fetchCurrentWebsite = async () => {
    try {
      const response = await api.get('/website-builder/my-website');
      if (response.data.website) {
        setCurrentWebsite(response.data.website);
        reset(response.data.website);
      } else {
        console.log('No existing website found - user can create a new one');
        setCurrentWebsite(null);
      }
    } catch (error) {
      console.error('Error fetching website:', error);
      if (error.response?.status === 401) {
        toast.error('Please log in to access website builder');
      } else {
        console.log('No existing website found');
      }
    }
  };

  const createAIWebsite = async (platform = 'netlify') => {
    try {
      setAiLoading(true);
      
      const formData = watch();
      if (!formData.website_name) {
        toast.error('Please enter a website name first');
        return;
      }

      // Step 1: Generate AI content using development endpoint
      toast.loading('🤖 Generating AI content for your website...', { duration: 3000 });
      
      const businessInfo = {
        hero_title: formData.website_name || 'My Business',
        hero_subtitle: formData.business_type ? `Professional ${formData.business_type} services` : 'Your trusted business partner',
        about_us: `Welcome to ${formData.website_name}. We provide excellent ${formData.business_type || 'business'} services in ${formData.area || 'your area'}.`,
        contact_cta: 'Contact us today for more information!'
      };

      // Use development endpoint that doesn't require authentication
      const contentResponse = await fetch('http://localhost:5000/api/ai-tools/dev/gemini-test', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: `Create engaging website content for "${formData.website_name}" - a ${formData.business_type || 'business'} in ${formData.area || 'local area'}. Make it professional and appealing.`
        })
      });
      
      const contentResult = await contentResponse.json();
      
      if (!contentResult.success) {
        throw new Error('Failed to generate website content: ' + (contentResult.error || 'AI service unavailable'));
      }

      // Step 2: Deploy to selected platform using development endpoint
      toast.loading(`🚀 Deploying to ${platform}...`, { duration: 5000 });
      
      let deployResult;
      if (platform === 'netlify') {
        const deployResponse = await fetch('http://localhost:5000/api/ai-tools/dev/netlify-deploy', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            site_name: formData.website_name,
            business_info: businessInfo
          })
        });
        deployResult = await deployResponse.json();
      } else if (platform === 'github') {
        const deployResponse = await fetch('http://localhost:5000/api/ai-tools/dev/github-deploy', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            site_name: formData.website_name,
            business_info: businessInfo
          })
        });
        deployResult = await deployResponse.json();
      }

      if (!deployResult || !deployResult.success) {
        // Handle specific Netlify uniqueness errors
        if (deployResult?.error?.includes('must be unique') || deployResult?.error?.includes('already exists')) {
          throw new Error(`Website name "${formData.website_name}" is already taken. The system will automatically try alternative names, but you can also try changing the website name and deploying again.`);
        }
        throw new Error(`Deployment failed: ${deployResult?.error || 'Unknown deployment error'}`);
      }

      // Step 3: Success!
      setDeployedUrl(deployResult.website_url);
      toast.success(`🎉 Website deployed successfully to ${platform.charAt(0).toUpperCase() + platform.slice(1)}!`);
      
      // Update current website state
      setCurrentWebsite({
        ...formData,
        website_url: deployResult.website_url,
        platform: platform,
        deployment_info: deployResult,
        ai_generated: true
      });

    } catch (error) {
      console.error('AI Website Creation Error:', error);
      toast.error(error.message || 'Failed to create AI website');
    } finally {
      setAiLoading(false);
    }
  };

  const createDataCollectionWebsite = async () => {
    try {
      setAiLoading(true);
      
      const formData = watch();
      if (!formData.website_name) {
        toast.error('Please enter a website name first');
        return;
      }

      toast.loading('🚀 Creating data collection website...', { duration: 3000 });
      
      const websiteData = {
        title: formData.website_name,
        description: `Join the ${formData.website_name} community and share your valuable feedback with us.`,
        content: `Welcome to ${formData.website_name}! We're building something amazing and we'd love to have you as part of our journey. Sign up to stay updated and let us know what you think.`,
        business_id: formData.business_id || null
      };

      // Use development endpoint for data collection website
      const response = await fetch('http://localhost:5000/api/ai-tools/dev/create-data-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(websiteData)
      });
      
      const result = await response.json();
      
      if (result.success && result.website_url) {
        setCurrentWebsite({
          ...formData,
          website_url: result.website_url,
          netlify_url: result.netlify_url,
          has_data_collection: true,
          features: ['user_registration', 'feedback_collection', 'sentiment_analysis'],
          created_at: new Date().toISOString()
        });
        
        toast.success('✅ Data collection website created successfully!');
        toast.success(`🌐 Website URL: ${result.website_url}`, { duration: 8000 });
      } else {
        throw new Error(result.error || 'Failed to create data collection website');
      }

    } catch (error) {
      console.error('Data Collection Website Creation Error:', error);
      toast.error(error.message || 'Failed to create data collection website');
    } finally {
      setAiLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      // Use development endpoint that doesn't require authentication
      const response = await fetch('http://localhost:5000/api/website-builder/dev-create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });
      
      const result = await response.json();
      
      if (result.success) {
        toast.success(result.message || 'Website created successfully!');
        if (result.website) {
          setCurrentWebsite(result.website);
        }
      } else {
        throw new Error(result.error || 'Failed to create website');
      }
      
    } catch (error) {
      console.error('Website creation error:', error);
      toast.error(error.message || 'Failed to save website');
    } finally {
      setLoading(false);
    }
  };

  const getThemePreview = (themeKey) => {
    const theme = themes[themeKey];
    if (!theme) return null;

    return (
      <div className="border-2 border-gray-200 rounded-lg p-4 hover:border-primary-500 transition-colors cursor-pointer">
        <div className="mb-3">
          <h4 className="font-medium text-gray-900">{theme.name}</h4>
          <p className="text-sm text-gray-600">{theme.description}</p>
        </div>
        
        <div className="grid grid-cols-3 gap-2 mb-3">
          {theme.color_schemes.map((scheme) => {
            const colors = colorSchemes[scheme];
            if (!colors) return null;
            
            return (
              <div key={scheme} className="flex space-x-1">
                <div 
                  className="w-4 h-4 rounded-full border"
                  style={{ backgroundColor: colors.primary }}
                />
                <div 
                  className="w-4 h-4 rounded-full border"
                  style={{ backgroundColor: colors.secondary }}
                />
                <div 
                  className="w-4 h-4 rounded-full border"
                  style={{ backgroundColor: colors.background }}
                />
              </div>
            );
          })}
        </div>
        
        <div className="text-xs text-gray-500">
          Features: {theme.features.join(', ')}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Website Builder</h1>
          <p className="text-gray-600 mt-2">
            {currentWebsite ? 'Update your business website' : 'Create your business website'}
          </p>
        </div>
        
        {currentWebsite && (
          <div className="flex space-x-3">
            <a
              href={currentWebsite.website_url || '#'}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-secondary flex items-center space-x-2"
            >
              <Eye size={16} />
              <span>Preview</span>
            </a>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Basic Information */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Settings size={20} />
            <span>Basic Information</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Website Name *
              </label>
              <input
                {...register('website_name', { required: 'Website name is required' })}
                className="input-field"
                placeholder="Your Business Name"
              />
              {errors.website_name && (
                <p className="text-red-500 text-sm mt-1">{errors.website_name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Type *
              </label>
              <select
                {...register('business_type', { required: 'Business type is required' })}
                className="input-field"
              >
                <option value="">Select Business Type</option>
                {Object.entries(themes).map(([key, theme]) => (
                  <option key={key} value={key}>{theme.name}</option>
                ))}
              </select>
              {errors.business_type && (
                <p className="text-red-500 text-sm mt-1">{errors.business_type.message}</p>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Description
              </label>
              <textarea
                {...register('description')}
                rows="3"
                className="input-field"
                placeholder="Describe your business, products, or services..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Area/Location *
              </label>
              <input
                {...register('area', { required: 'Area is required' })}
                className="input-field"
                placeholder="City, State or Region"
              />
              {errors.area && (
                <p className="text-red-500 text-sm mt-1">{errors.area.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Logo URL (Optional)
              </label>
              <input
                {...register('logo_url')}
                className="input-field"
                placeholder="https://example.com/logo.png"
              />
            </div>
          </div>
        </div>

        {/* Theme Selection */}
        {selectedBusinessType && themes[selectedBusinessType] && (
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <Palette size={20} />
              <span>Theme & Colors</span>
            </h3>
            
            <div className="mb-6">
              <h4 className="font-medium text-gray-900 mb-3">Selected Theme: {themes[selectedBusinessType].name}</h4>
              {getThemePreview(selectedBusinessType)}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-3">
                Color Scheme *
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {themes[selectedBusinessType].color_schemes.map((scheme) => {
                  const colors = colorSchemes[scheme];
                  if (!colors) return null;

                  return (
                    <label key={scheme} className="cursor-pointer">
                      <input
                        type="radio"
                        {...register('color_theme', { required: 'Color theme is required' })}
                        value={scheme}
                        className="sr-only"
                      />
                      <div className={`p-4 border-2 rounded-lg transition-colors ${
                        selectedColorTheme === scheme 
                          ? 'border-primary-500 bg-primary-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}>
                        <div className="flex space-x-2 mb-2">
                          <div 
                            className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                            style={{ backgroundColor: colors.primary }}
                          />
                          <div 
                            className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                            style={{ backgroundColor: colors.secondary }}
                          />
                          <div 
                            className="w-6 h-6 rounded-full border-2 border-white shadow-sm"
                            style={{ backgroundColor: colors.background }}
                          />
                        </div>
                        <p className="text-sm font-medium text-gray-900 capitalize">{scheme}</p>
                      </div>
                    </label>
                  );
                })}
              </div>
              {errors.color_theme && (
                <p className="text-red-500 text-sm mt-1">{errors.color_theme.message}</p>
              )}
            </div>
          </div>
        )}

        {/* Contact Information */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact Information</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address *
              </label>
              <input
                {...register('contact_info.email', { 
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid email address"
                  }
                })}
                className="input-field"
                placeholder="business@example.com"
              />
              {errors.contact_info?.email && (
                <p className="text-red-500 text-sm mt-1">{errors.contact_info.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                {...register('contact_info.phone')}
                className="input-field"
                placeholder="(555) 123-4567"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Address
              </label>
              <textarea
                {...register('contact_info.address')}
                rows="2"
                className="input-field"
                placeholder="123 Main St, City, State 12345"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Hours
              </label>
              <input
                {...register('contact_info.hours')}
                className="input-field"
                placeholder="Mon-Fri 9AM-5PM"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Website URL (Optional)
              </label>
              <input
                {...register('contact_info.website')}
                className="input-field"
                placeholder="https://yourbusiness.com"
              />
            </div>
          </div>
        </div>

        {/* Advanced Settings */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Advanced Settings</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Custom Domain (Optional)
              </label>
              <input
                {...register('custom_domain')}
                className="input-field"
                placeholder="yourbusiness.com"
              />
              <p className="text-xs text-gray-500 mt-1">
                Point your custom domain to our servers to use your own URL
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Custom CSS (Optional)
              </label>
              <textarea
                {...register('custom_css')}
                rows="4"
                className="input-field font-mono text-sm"
                placeholder="/* Add your custom CSS styles here */"
              />
              <p className="text-xs text-gray-500 mt-1">
                Advanced users can add custom CSS to further customize their website
              </p>
            </div>
          </div>
        </div>

        {/* Current Website Info */}
        {currentWebsite && (
          <div className="card bg-blue-50 border-blue-200">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">Current Website</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-blue-800 mb-2">
                  <strong>Website URL:</strong>
                </p>
                <a
                  href={currentWebsite.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 underline text-sm break-all"
                >
                  {currentWebsite.website_url}
                </a>
              </div>
              
              {currentWebsite.analytics && (
                <div>
                  <p className="text-sm text-blue-800 mb-2">
                    <strong>Analytics:</strong>
                  </p>
                  <div className="text-sm text-blue-700 space-y-1">
                    <p>Total Visits: {currentWebsite.analytics.total_visits}</p>
                    <p>Unique Visitors: {currentWebsite.analytics.unique_visitors}</p>
                    {currentWebsite.analytics.last_visit && (
                      <p>Last Visit: {new Date(currentWebsite.analytics.last_visit).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* AI Website Creation */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200 mb-6">
          <div className="flex items-center mb-4">
            <Bot className="text-purple-600 mr-2" size={24} />
            <h3 className="text-lg font-semibold text-gray-900">AI-Powered Website Creation</h3>
          </div>
          <p className="text-gray-600 mb-4">
            Create and deploy a professional website instantly using AI. Just fill in your business details above!
          </p>
          
          <div className="flex flex-wrap gap-3">
            <button
              type="button"
              onClick={() => createAIWebsite('netlify')}
              disabled={aiLoading}
              className="btn-primary flex items-center space-x-2 bg-teal-600 hover:bg-teal-700"
            >
              {aiLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Rocket size={16} />
              )}
              <span>Deploy to Netlify</span>
            </button>
            
            <button
              type="button"
              onClick={() => createAIWebsite('github')}
              disabled={aiLoading}
              className="btn-primary flex items-center space-x-2 bg-gray-800 hover:bg-gray-900"
            >
              {aiLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Rocket size={16} />
              )}
              <span>Deploy to GitHub Pages</span>
            </button>
            
            <button
              type="button"
              onClick={createDataCollectionWebsite}
              disabled={aiLoading}
              className="btn-primary flex items-center space-x-2 bg-purple-600 hover:bg-purple-700"
            >
              {aiLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Bot size={16} />
              )}
              <span>Create Data Collection Site</span>
            </button>
          </div>
          
          {deployedUrl && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-green-800 font-medium">🎉 Website deployed successfully!</p>
                  <a 
                    href={deployedUrl} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-green-600 hover:text-green-800 underline break-all"
                  >
                    {deployedUrl}
                  </a>
                </div>
                <button
                  onClick={() => window.open(deployedUrl, '_blank')}
                  className="btn-secondary text-sm"
                >
                  View Website
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex justify-between items-center">
          <button
            type="button"
            onClick={() => setPreviewMode(!previewMode)}
            className="btn-secondary flex items-center space-x-2"
          >
            <Eye size={16} />
            <span>{previewMode ? 'Hide Preview' : 'Show Preview'}</span>
          </button>
          
          <div className="flex space-x-3">
            <button
              type="button"
              onClick={() => reset()}
              className="btn-secondary"
            >
              Reset
            </button>
          
          <button
            type="submit"
            disabled={loading}
            className="btn-primary flex items-center space-x-2"
          >
            {loading ? (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            ) : (
              <Save size={16} />
            )}
            <span>
              {loading 
                ? 'Saving...' 
                : currentWebsite 
                  ? 'Update Website' 
                  : 'Create Website'
              }
            </span>
          </button>
          </div>
        </div>
      </form>

      {/* Website Preview */}
      <div className="mt-8">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center space-x-2">
            <Eye size={20} />
            <span>Website Preview</span>
          </h3>
        </div>
        
        <WebsitePreview
          websiteData={{
            ...watch(),
            website_url: currentWebsite?.website_url || deployedUrl
          }}
          isVisible={previewMode}
          onToggle={() => setPreviewMode(!previewMode)}
        />
      </div>
    </div>
  );
};

export default WebsiteBuilder;

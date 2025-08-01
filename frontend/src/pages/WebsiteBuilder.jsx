import React, { useState, useEffect } from 'react';
import { Globe, Palette, Settings, Eye, Edit, Save } from 'lucide-react';
import { useForm } from 'react-hook-form';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const WebsiteBuilder = () => {
  const [currentWebsite, setCurrentWebsite] = useState(null);
  const [themes, setThemes] = useState({});
  const [colorSchemes, setColorSchemes] = useState({});
  const [loading, setLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  
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
      setCurrentWebsite(response.data.website);
      reset(response.data.website);
    } catch (error) {
      // No existing website, which is fine
      console.log('No existing website found');
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      let response;
      if (currentWebsite) {
        response = await api.put('/website-builder/update', data);
        toast.success('Website updated successfully!');
      } else {
        response = await api.post('/website-builder/create', data);
        toast.success('Website created successfully!');
      }
      
      if (response.data.website) {
        setCurrentWebsite(response.data.website);
      }
      
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to save website');
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

        {/* Submit Button */}
        <div className="flex justify-end space-x-3">
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
      </form>
    </div>
  );
};

export default WebsiteBuilder;

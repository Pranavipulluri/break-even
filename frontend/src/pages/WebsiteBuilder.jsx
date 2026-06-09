import { Bot, CreditCard, Download, Eye, Globe, Palette, Rocket, Save, Settings } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import WebsitePreview from '../components/website/WebsitePreview';
import { useTranslation } from '../context/TranslationContext';
import { api } from '../services/api';

// Development initialization

const WebsiteBuilder = () => {
  const { currentLanguage, changeLanguage, translateWebsiteContent, t } = useTranslation();
  const [currentWebsite, setCurrentWebsite] = useState(null);
  const [themes, setThemes] = useState({});
  const [colorSchemes, setColorSchemes] = useState({});
  const [loading, setLoading] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);
  const [deployedUrl, setDeployedUrl] = useState(null);
  const [previewHtml, setPreviewHtml] = useState(null);
  const [previewPlatform, setPreviewPlatform] = useState(null);
  
  const { register, handleSubmit, reset, watch, formState: { errors } } = useForm({
    defaultValues: {
      business_type: '',
      color_theme: 'blue',
      practice_areas: [],
      business_card_design: 'modern',
      attorney_name: '',
      attorney_bio: '',
      years_experience: '',
      other_practice_areas: ''
    }
  });

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

  // Preview website before deploying (Issue #13)
  const handlePreview = async () => {
    try {
      setAiLoading(true);
      const formData = watch();
      if (!formData.website_name) {
        toast.error('Please enter a website name first');
        return;
      }

      toast.loading('🔍 Generating preview...', { duration: 2000 });

      const businessInfo = {
        website_name: formData.website_name,
        business_type: formData.business_type,
        description: formData.description,
        area: formData.area,
        services_products: formData.services_products || '',
        phone: formData.phone || '',
        email: formData.email || '',
        address: formData.address || formData.area || '',
        color_theme: formData.color_theme,
        unique_selling_points: formData.unique_selling_points || '',
        contact_cta: formData.contact_cta || 'Contact us today!',
      };

      const res = await api.post('/ai-tools/preview', {
        site_name: formData.website_name,
        business_info: businessInfo,
      });

      if (res.data?.success) {
        setPreviewHtml(res.data.html);
        toast.success('Preview ready!');
      } else {
        toast.error(res.data?.error || 'Preview generation failed');
      }
    } catch (err) {
      console.error('Preview error:', err);
      toast.error('Failed to generate preview');
    } finally {
      setAiLoading(false);
    }
  };

  // Deploy with optional preview confirmation
  const handlePreviewThenDeploy = (platform) => {
    setPreviewPlatform(platform);
    handlePreview();
  };

  const confirmDeploy = () => {
    setPreviewHtml(null);
    createAIWebsite(previewPlatform || 'netlify');
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
      
        // Prepare enhanced business information for better AI generation
        const businessInfo = {
          website_name: formData.website_name,
          business_type: formData.business_type,
          description: formData.description,
          area: formData.area,
          target_audience: formData.target_audience || 'local customers',
          unique_selling_points: formData.unique_selling_points || '',
          services_products: formData.services_products || '',
          contact_info: {
            phone: formData.phone || '',
            email: formData.email || '',
            address: formData.address || formData.area || ''
          },
          business_goals: formData.business_goals || 'grow customer base',
          hero_title: formData.website_name,
          hero_subtitle: formData.business_type ? `Professional ${formData.business_type} services in ${formData.area}` : 'Your trusted business partner',
          about_us: formData.description || `Welcome to ${formData.website_name}. We provide excellent ${formData.business_type || 'business'} services in ${formData.area || 'your area'}.`,
          contact_cta: formData.contact_cta || 'Contact us today!',
          theme: formData.business_type,
          color_scheme: formData.color_theme,
          logo_url: formData.logo_url
        };      // Use development endpoint that doesn't require authentication
      const contentResponse = await api.post('/ai-tools/dev/gemini-test', {
        prompt: `Create comprehensive, professional website content for "${formData.website_name}" - a ${formData.business_type || 'business'} in ${formData.area || 'local area'}. 

BUSINESS PROFILE:
- Business Name: ${formData.website_name}
- Type: ${formData.business_type}
- Location: ${formData.area}
- Description: ${formData.description}
- Main Products/Services: ${formData.services_products || 'various services'}
- Target Customers: ${formData.target_audience || 'local customers'}
- Unique Selling Points: ${formData.unique_selling_points || 'quality service'}
- Business Goals: ${formData.business_goals || 'attract more customers'}
- Contact: ${formData.phone || ''} ${formData.email || ''}
- Call-to-Action: ${formData.contact_cta || 'Contact us today!'}

CONTENT REQUIREMENTS:
Generate authentic, engaging website content including:
1. Hero Section: Compelling headline and subtitle that captures attention
2. About Us: Professional story highlighting experience and expertise
3. Services/Products: Clear descriptions with customer benefits
4. Why Choose Us: Emphasize unique selling points and local presence
5. Customer Testimonials: 2-3 realistic testimonials for this business type
6. Contact Section: Clear contact information and call-to-action

Make it sound authentic, locally-focused, and specific to small businesses in ${formData.business_type}. Use professional but approachable tone.`
      });
      
      const contentResult = contentResponse.data;
      
      if (!contentResult.success) {
        throw new Error('Failed to generate website content: ' + (contentResult.error || 'AI service unavailable'));
      }

      // Step 2: Deploy to selected platform using development endpoint
      toast.loading(`🚀 Deploying to ${platform}...`, { duration: 5000 });
      
      let deployResult;
      if (platform === 'netlify') {
        const deployResponse = await api.post('/ai-tools/dev/netlify-deploy', {
          site_name: formData.website_name,
          business_info: businessInfo
        });
        deployResult = deployResponse.data;
      } else if (platform === 'github') {
        const deployResponse = await api.post('/ai-tools/dev/github-deploy', {
          site_name: formData.website_name,
          business_info: businessInfo
        });
        deployResult = deployResponse.data;
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
      const response = await api.post('/ai-tools/dev/create-data-website', websiteData);
      const result = response.data;
      
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

  const createProfessionalLawFirmWebsite = async () => {
    try {
      setAiLoading(true);
      
      const formData = watch();
      if (!formData.website_name || !formData.contact_info?.email) {
        toast.error('Please enter website name and business email first');
        return;
      }

      toast.loading('⚖️ Creating professional law firm website...', { duration: 4000 });
      
      const lawFirmData = {
        // Basic info (what the endpoint expects)
        website_name: formData.website_name,
        business_email: formData.contact_info?.email,
        business_phone: formData.contact_info?.phone || '',
        business_address: formData.contact_info?.address || '',
        description: formData.description || `Professional legal services from ${formData.website_name}`,
        
        // Practice areas
        practice_areas: formData.practice_areas || ['General Practice', 'Civil Law', 'Business Law'],
        
        // Attorney info
        attorney_name: formData.attorney_name || 'Attorney Name',
        attorney_bio: formData.attorney_bio || 'Experienced legal professional dedicated to serving clients with integrity and expertise.',
        years_experience: formData.years_experience ? parseInt(formData.years_experience) || 5 : 5,
        
        // Business card design
        business_card_design: formData.business_card_design || 'modern',
        
        // Language preference
        target_language: currentLanguage,
        
        // Optional
        business_id: formData.business_id || null
      };

      console.log('Sending law firm data:', lawFirmData);

      // Use law firm integration service
      const response = await api.post('/law-firm/create-website', lawFirmData);
      const result = response.data;
      
      console.log('Backend response:', result);
      console.log('Response status:', response.status);
      
      if (result.success && result.website_url) {
        let websiteData = {
          ...formData,
          website_url: result.website_url,
          netlify_url: result.netlify_url,
          law_firm_features: true,
          business_card_url: result.business_card_url,
          business_card_front_url: result.business_card_url, // Map to front_url
          business_card_back_url: result.business_card_back_url,
          business_card_design: result.business_card_design,
          attorney_profile: result.attorney_profile,
          practice_areas: result.practice_areas,
          firm_id: result.firm_id,
          qr_code_url: result.qr_code_url,
          business_cards: result.business_cards, // Include full business card data
          created_at: new Date().toISOString()
        };

        // Translate content if not in English
        if (currentLanguage !== 'en') {
          websiteData = await translateWebsiteContent(websiteData, currentLanguage);
        }
        
        setCurrentWebsite(websiteData);
        
        toast.success('✅ Professional law firm website created successfully!');
        toast.success(`🌐 Website URL: ${result.website_url}`, { duration: 8000 });
        if (result.business_card_url) {
          toast.success(`💼 Business cards generated! Check deployment section for downloads.`, { duration: 6000 });
        }
      } else {
        throw new Error(result.error || 'Failed to create law firm website');
      }

    } catch (error) {
      console.error('Law Firm Website Creation Error:', error);
      console.error('Full error details:', error.stack);
      
      // Try to get more detailed error info
      if (error.response) {
        console.error('Response error:', error.response);
      }
      
      toast.error(error.message || 'Failed to create professional law firm website');
    } finally {
      setAiLoading(false);
    }
  };

  const createProfessionalSpaWebsite = async () => {
    try {
      setAiLoading(true);
      
      const formData = watch();
      if (!formData.website_name || !formData.contact_info?.email) {
        toast.error('Please enter website name and business email first');
        return;
      }

      toast.loading('🌸 Creating professional spa website...', { duration: 4000 });
      
      const spaData = {
        // Basic salon info
        salon_name: formData.website_name,
        owner_name: formData.owner_name || 'Spa Owner',
        email_address: formData.contact_info?.email,
        phone_number: formData.contact_info?.phone || '',
        address: formData.contact_info?.address || '',
        description: formData.description || `Luxury spa and beauty services at ${formData.website_name}`,
        
        // Services
        services: [
          { name: 'Facial Treatments', price: '80', duration: '60', description: 'Professional facial treatments for radiant skin' },
          { name: 'Massage Therapy', price: '100', duration: '90', description: 'Relaxing full-body massage therapy' },
          { name: 'Hair Styling', price: '60', duration: '45', description: 'Expert hair styling and coloring' },
          { name: 'Nail Care', price: '40', duration: '30', description: 'Manicure and pedicure services' },
          { name: 'Spa Packages', price: '200', duration: '180', description: 'Complete relaxation spa packages' },
          { name: 'Skincare Consultation', price: '50', duration: '30', description: 'Personalized skincare advice' }
        ],
        
        // Staff members
        staff_members: [
          {
            name: formData.staff_name || 'Head Stylist',
            title: 'Senior Beauty Specialist',
            specializations: ['Hair Styling', 'Color Expert', 'Bridal Beauty'],
            bio: 'Expert beauty specialist with years of experience in luxury spa treatments',
            available_hours: {
              monday: ['09:00', '17:00'],
              tuesday: ['09:00', '17:00'],
              wednesday: ['09:00', '17:00'],
              thursday: ['09:00', '17:00'],
              friday: ['09:00', '17:00'],
              saturday: ['10:00', '16:00']
            }
          },
          {
            name: 'Spa Therapist',
            title: 'Massage Therapist',
            specializations: ['Deep Tissue Massage', 'Hot Stone', 'Aromatherapy'],
            bio: 'Licensed massage therapist specializing in relaxation and therapeutic treatments',
            available_hours: {
              monday: ['10:00', '18:00'],
              tuesday: ['10:00', '18:00'],
              wednesday: ['10:00', '18:00'],
              thursday: ['10:00', '18:00'],
              friday: ['10:00', '18:00'],
              saturday: ['11:00', '17:00']
            }
          }
        ],
        
        // Business card design
        business_card_design: formData.business_card_design || 'spa_serenity',
        
        // Language preference
        target_language: currentLanguage,
        
        // Operating hours
        business_hours: {
          monday: '9:00 AM - 6:00 PM',
          tuesday: '9:00 AM - 6:00 PM',
          wednesday: '9:00 AM - 6:00 PM',
          thursday: '9:00 AM - 6:00 PM',
          friday: '9:00 AM - 6:00 PM',
          saturday: '10:00 AM - 5:00 PM',
          sunday: 'Closed'
        },
        
        // Optional
        business_id: formData.business_id || null
      };

      console.log('Sending spa data:', spaData);

      // Use beauty salon integration service
      const response = await api.post('/beauty-salon/create-complete-salon', spaData);
      const result = response.data;
      
      console.log('Backend response:', result);
      console.log('Response status:', response.status);
      
      if (result.success) {
        let websiteData = {
          ...formData,
          website_url: result.website_url || result.website?.website_url || null,
          netlify_url: result.netlify_url || result.website?.netlify_url || null,
          spa_features: true,
          business_card_url: result.business_card_url,
          business_card_front_url: result.business_card_url, // Map to front_url
          business_card_back_url: result.business_card_back_url,
          business_card_design: result.business_card_design,
          staff_profiles: result.staff_profiles,
          services: result.services,
          salon_id: result.salon_id,
          qr_code_url: result.qr_code_url,
          business_cards: result.business_cards, // Include full business card data
          website_files: result.website?.website_files, // Include website files
          deployment_info: result.website?.deployment, // Include deployment info
          created_at: new Date().toISOString()
        };

        // Translate content if not in English
        if (currentLanguage !== 'en') {
          websiteData = await translateWebsiteContent(websiteData, currentLanguage);
        }
        
        setCurrentWebsite(websiteData);
        
        toast.success('✅ Professional spa website created successfully!');
        
        // Show appropriate URL message
        if (websiteData.website_url) {
          toast.success(`🌐 Website deployed! URL: ${websiteData.website_url}`, { duration: 8000 });
          
          // Show QR code message if available
          if (websiteData.qr_code_url) {
            toast.success(`📱 QR code generated! Scan to visit your spa website.`, { duration: 6000 });
          }
        } else if (websiteData.deployment_info?.ready_for_netlify) {
          if (websiteData.deployment_info?.netlify_deployed === false) {
            toast.success(`📁 Website files created! Netlify deployment attempted but files are ready for manual deployment.`, { duration: 8000 });
          } else {
            toast.success(`📁 Website files created! Ready for deployment to Netlify.`, { duration: 6000 });
          }
        }
        
        if (result.business_cards && result.business_cards.length > 0) {
          toast.success(`💼 Spa business cards generated! Check deployment section for downloads.`, { duration: 6000 });
        }
      } else {
        throw new Error(result.error || 'Failed to create spa website');
      }

    } catch (error) {
      console.error('Spa Website Creation Error:', error);
      console.error('Full error details:', error.stack);
      
      // Try to get more detailed error info
      if (error.response) {
        console.error('Response error:', error.response);
      }
      
      toast.error(error.message || 'Failed to create professional spa website');
    } finally {
      setAiLoading(false);
    }
  };

  const onSubmit = async (data) => {
    try {
      setLoading(true);
      
      // Call authenticated production CRUD endpoints if user has website
      const url = currentWebsite ? '/website-builder/update' : '/website-builder/create';
      const method = currentWebsite ? 'put' : 'post';
      
      const response = await api[method](url, data);
      const result = response.data;
      
      if (result.website || result.website_id) {
        toast.success(result.message || 'Website saved successfully!');
        // Refresh to load real database state and ID
        await fetchCurrentWebsite();
      } else {
        throw new Error(result.error || 'Failed to save website');
      }
      
    } catch (error) {
      console.error('Website creation error, falling back to local mode:', error);
      // Fallback to dev-create in case the JWT or DB connection has issues
      try {
        const response = await api.post('/website-builder/dev-create', data);
        if (response.data.success) {
          toast.success('Saved locally (development mode)');
          if (response.data.website) {
            setCurrentWebsite(response.data.website);
          }
        } else {
          throw new Error(response.data.error || 'Failed to save locally');
        }
      } catch (fallbackError) {
        console.error('Fallback failed:', fallbackError);
        toast.error(error.response?.data?.error || error.message || 'Failed to save website');
      }
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
    <div className="space-y-6 animate-fade-in relative">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('website_builder', 'Website Builder')}</h1>
          <p className="text-gray-600 mt-2">
            {currentWebsite 
              ? t('update_business_website', 'Update your business website')
              : t('create_business_website', 'Create your business website')
            }
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
          
          {/* Helpful Tips for Small Business */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-blue-900 mb-2">💡 Tips for Small Business Owners</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Be specific about your services - help customers understand exactly what you offer</li>
              <li>• Mention your location to attract local customers</li>
              <li>• Highlight what makes you different from competitors</li>
              <li>• Include contact information so customers can easily reach you</li>
            </ul>
          </div>
          
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
                <option value="restaurant">Restaurant/Food Service</option>
                <option value="retail">Retail Store</option>
                <option value="bakery">Bakery/Café</option>
                <option value="beauty">Beauty Salon/Spa</option>
                <option value="fitness">Fitness Center/Gym</option>
                <option value="automotive">Auto Repair/Service</option>
                <option value="healthcare">Healthcare/Medical</option>
                <option value="lawfirm">Law Firm/Legal Services</option>
                <option value="real_estate">Real Estate</option>
                <option value="consulting">Consulting/Professional Services</option>
                <option value="education">Education/Training</option>
                <option value="photography">Photography/Creative</option>
                <option value="home_services">Home Services/Repair</option>
                <option value="technology">Technology/IT Services</option>
                <option value="agriculture">Agriculture/Farming</option>
                <option value="other">Other</option>
              </select>
              {errors.business_type && (
                <p className="text-red-500 text-sm mt-1">{errors.business_type.message}</p>
              )}
              
              {/* Law Firm Information Banner */}
              {selectedBusinessType === 'lawfirm' && (
                <div className="mt-3 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <svg className="w-6 h-6 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h4 className="text-sm font-semibold text-blue-900 mb-1">Law Firm Features Available</h4>
                      <p className="text-sm text-blue-800 mb-2">
                        You've selected Law Firm - additional features will be available including:
                      </p>
                      <ul className="text-sm text-blue-700 space-y-1">
                        <li>• Professional attorney profiles with photos and bios</li>
                        <li>• Custom business card generation (5 professional designs)</li>
                        <li>• Practice area specialization setup</li>
                        <li>• Consultation booking system</li>
                        <li>• Professional law firm website templates</li>
                      </ul>
                      <p className="text-sm text-blue-600 mt-2 font-medium">
                        🎯 Fill out all sections, then use "Create Professional Law Firm Website" button!
                      </p>
                    </div>
                  </div>
                </div>
              )}
              {selectedBusinessType === 'lawfirm' && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-start space-x-2">
                    <svg className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <h4 className="text-sm font-semibold text-blue-900">Law Firm Features Enabled</h4>
                      <p className="text-sm text-blue-700 mt-1">
                        You'll be able to create a professional law firm website with business cards, attorney profiles, practice area showcases, and consultation booking system.
                      </p>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Beauty Salon/Spa Information Banner */}
              {selectedBusinessType === 'beauty' && (
                <div className="mt-3 p-4 bg-pink-50 border border-pink-200 rounded-lg">
                  <div className="flex items-start space-x-3">
                    <svg className="w-6 h-6 text-pink-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                    <div>
                      <h4 className="text-sm font-semibold text-pink-900 mb-1">Beauty Salon/Spa Features Available</h4>
                      <p className="text-sm text-pink-800 mb-2">
                        You've selected Beauty Salon/Spa - advanced spa features will be available including:
                      </p>
                      <ul className="text-sm text-pink-700 space-y-1">
                        <li>• Professional staff profiles with specializations</li>
                        <li>• Beautiful spa-themed business cards (5 elegant designs)</li>
                        <li>• Service catalog with pricing and duration</li>
                        <li>• Advanced appointment booking system</li>
                        <li>• Luxury spa website templates with relaxing themes</li>
                        <li>• Client review and feedback system</li>
                      </ul>
                      <p className="text-sm text-pink-600 mt-2 font-medium">
                        🌸 Fill out all sections, then use "Create Professional Spa Website" button!
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Description *
              </label>
              <textarea
                {...register('description', { required: 'Business description is required' })}
                rows="3"
                className="input-field"
                placeholder="Describe your business, what you offer, and what makes you special..."
              />
              {errors.description && (
                <p className="text-red-500 text-sm mt-1">{errors.description.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Main Products/Services *
              </label>
              <input
                {...register('services_products', { required: 'Please list your main offerings' })}
                className="input-field"
                placeholder="e.g., Fresh baked goods, Custom cakes, Coffee"
              />
              {errors.services_products && (
                <p className="text-red-500 text-sm mt-1">{errors.services_products.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Target Customers
              </label>
              <input
                {...register('target_audience')}
                className="input-field"
                placeholder="e.g., Local families, Young professionals, Students"
              />
            </div>

            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                What Makes You Special?
              </label>
              <textarea
                {...register('unique_selling_points')}
                rows="2"
                className="input-field"
                placeholder="e.g., 20 years experience, Organic ingredients, 24/7 service, Award-winning..."
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
                Phone Number
              </label>
              <input
                {...register('phone')}
                className="input-field"
                placeholder="(555) 123-4567"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <input
                type="email"
                {...register('email')}
                className="input-field"
                placeholder="business@example.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Street Address
              </label>
              <input
                {...register('address')}
                className="input-field"
                placeholder="123 Main Street"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Goals
              </label>
              <select
                {...register('business_goals')}
                className="input-field"
              >
                <option value="">Select Primary Goal</option>
                <option value="increase_sales">Increase Sales</option>
                <option value="attract_customers">Attract New Customers</option>
                <option value="build_brand">Build Brand Awareness</option>
                <option value="showcase_products">Showcase Products/Services</option>
                <option value="improve_credibility">Improve Business Credibility</option>
                <option value="expand_reach">Expand Geographic Reach</option>
                <option value="customer_retention">Improve Customer Retention</option>
              </select>
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

        {/* Contact Information */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Settings size={20} />
            <span>Contact & Call-to-Action</span>
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Main Call-to-Action
              </label>
              <input
                {...register('contact_cta')}
                className="input-field"
                placeholder="e.g., Call Now for Free Quote, Book Your Appointment, Order Online"
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

        {/* Law Firm Specific Fields */}
        {selectedBusinessType === 'lawfirm' && (
          <>
            {/* Attorney Information */}
            <div className="card border-l-4 border-blue-500">
              <h3 className="text-lg font-semibold text-blue-900 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                </svg>
                Attorney Information
              </h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Attorney Name *
                  </label>
                  <input
                    {...register('attorney_name', { 
                      required: selectedBusinessType === 'lawfirm' ? 'Attorney name is required' : false 
                    })}
                    className="input-field"
                    placeholder="John Smith, Esq."
                  />
                  {errors.attorney_name && (
                    <p className="text-red-500 text-sm mt-1">{errors.attorney_name.message}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Years of Experience
                  </label>
                  <input
                    {...register('years_experience')}
                    type="number"
                    className="input-field"
                    placeholder="10"
                    min="0"
                  />
                </div>

                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Attorney Bio
                  </label>
                  <textarea
                    {...register('attorney_bio')}
                    rows="4"
                    className="input-field"
                    placeholder="Professional background, education, specializations, and achievements..."
                  />
                </div>
              </div>
            </div>

            {/* Practice Areas */}
            <div className="card border-l-4 border-green-500">
              <h3 className="text-lg font-semibold text-green-900 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                Practice Areas
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Practice Areas (Select multiple)
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {[
                      'Civil Law', 'Criminal Law', 'Family Law', 'Business Law', 
                      'Real Estate Law', 'Personal Injury', 'Immigration Law',
                      'Employment Law', 'Intellectual Property', 'Tax Law',
                      'Estate Planning', 'Medical Malpractice'
                    ].map((area) => (
                      <label key={area} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          {...register('practice_areas')}
                          value={area}
                          className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                        />
                        <span className="text-sm text-gray-700">{area}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Other Practice Areas
                  </label>
                  <input
                    {...register('other_practice_areas')}
                    className="input-field"
                    placeholder="Enter additional practice areas (comma separated)"
                  />
                </div>
              </div>
            </div>

            {/* Business Card Design */}
            <div className="card border-l-4 border-purple-500">
              <h3 className="text-lg font-semibold text-purple-900 mb-4 flex items-center">
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h4l2-2-4-4-2 2v4z" />
                </svg>
                Business Card Design
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Choose Business Card Style
                  </label>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {[
                      { value: 'modern', label: 'Modern Professional', desc: 'Clean, minimalist design with blue accents' },
                      { value: 'classic', label: 'Classic Traditional', desc: 'Traditional layout with serif fonts' },
                      { value: 'elegant', label: 'Elegant Premium', desc: 'Sophisticated design with gold accents' },
                      { value: 'corporate', label: 'Corporate Standard', desc: 'Standard business format' },
                      { value: 'creative', label: 'Creative Contemporary', desc: 'Modern design with creative elements' }
                    ].map((design) => (
                      <label key={design.value} className="cursor-pointer">
                        <input
                          type="radio"
                          {...register('business_card_design')}
                          value={design.value}
                          className="sr-only"
                        />
                        <div className="border-2 border-gray-200 rounded-lg p-4 hover:border-purple-500 transition-colors duration-200 peer-checked:border-purple-500 peer-checked:bg-purple-50">
                          <h4 className="font-semibold text-gray-900">{design.label}</h4>
                          <p className="text-sm text-gray-600 mt-1">{design.desc}</p>
                        </div>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </>
        )}

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

            {/* Business Card Download Section */}
            {(currentWebsite.business_card_front_url || currentWebsite.business_card_back_url) && (
              <div className="mt-6 p-4 bg-gradient-to-br from-amber-50 to-orange-50 border border-amber-200 rounded-lg">
                <div className="flex items-center mb-3">
                  <CreditCard className="text-amber-600 mr-2" size={20} />
                  <h4 className="text-lg font-semibold text-amber-900">
                    {currentWebsite.spa_features ? 'Professional Spa Business Cards' : 
                     currentWebsite.law_firm_features ? 'Professional Law Firm Business Cards' : 
                     'Professional Business Cards'}
                  </h4>
                </div>
                <p className="text-sm text-amber-800 mb-4">
                  Download your professionally designed business cards below
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentWebsite.business_card_front_url && (
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-amber-200">
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="font-medium text-gray-900">Front Design</h5>
                        <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full">
                          {currentWebsite.business_card_design || 'Modern'}
                        </span>
                      </div>
                      <div className="mb-3">
                        <img 
                          src={currentWebsite.business_card_front_url} 
                          alt="Business Card Front" 
                          className="w-full h-32 object-cover rounded border border-gray-200"
                          style={{ aspectRatio: '3.5/2' }}
                        />
                      </div>
                      <a
                        href={currentWebsite.business_card_front_url}
                        download="business-card-front.png"
                        className="w-full bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                      >
                        <Download size={16} />
                        <span>Download Front</span>
                      </a>
                    </div>
                  )}
                  
                  {currentWebsite.business_card_back_url && (
                    <div className="bg-white p-4 rounded-lg shadow-sm border border-amber-200">
                      <div className="flex items-center justify-between mb-3">
                        <h5 className="font-medium text-gray-900">Back Design</h5>
                        <span className="text-xs bg-amber-100 text-amber-800 px-2 py-1 rounded-full">
                          Professional
                        </span>
                      </div>
                      <div className="mb-3">
                        <img 
                          src={currentWebsite.business_card_back_url} 
                          alt="Business Card Back" 
                          className="w-full h-32 object-cover rounded border border-gray-200"
                          style={{ aspectRatio: '3.5/2' }}
                        />
                      </div>
                      <a
                        href={currentWebsite.business_card_back_url}
                        download="business-card-back.png"
                        className="w-full bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium py-2 px-4 rounded-lg flex items-center justify-center space-x-2 transition-colors"
                      >
                        <Download size={16} />
                        <span>Download Back</span>
                      </a>
                    </div>
                  )}
                </div>
                
                <div className="mt-4 p-3 bg-amber-100 rounded-lg">
                  <p className="text-xs text-amber-800">
                    💡 <strong>Tip:</strong> These business cards are professionally designed and print-ready at standard business card dimensions (3.5" × 2").
                  </p>
                </div>
              </div>
            )}
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
              onClick={handlePreview}
              disabled={aiLoading}
              className="btn-primary flex items-center space-x-2 bg-indigo-600 hover:bg-indigo-700"
            >
              {aiLoading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Eye size={16} />
              )}
              <span>Preview Website</span>
            </button>
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
            
            {/* Law Firm Specific Option */}
            {selectedBusinessType === 'lawfirm' && (
              <button
                type="button"
                onClick={createProfessionalLawFirmWebsite}
                disabled={aiLoading}
                className="btn-primary flex items-center space-x-2 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800"
              >
                {aiLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <Globe size={16} />
                )}
                <span>Create Professional Law Firm Website</span>
              </button>
            )}
            
            {/* Beauty Salon/Spa Specific Option */}
            {selectedBusinessType === 'beauty' && (
              <button
                type="button"
                onClick={createProfessionalSpaWebsite}
                disabled={aiLoading}
                className="btn-primary flex items-center space-x-2 bg-gradient-to-r from-pink-600 to-pink-700 hover:from-pink-700 hover:to-pink-800"
              >
                {aiLoading ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                ) : (
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clipRule="evenodd" />
                  </svg>
                )}
                <span>Create Professional Spa Website</span>
              </button>
            )}
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
            _id: currentWebsite?._id || currentWebsite?.id,
            website_url: currentWebsite?.website_url || deployedUrl
          }}
          isVisible={previewMode}
          onToggle={() => setPreviewMode(!previewMode)}
        />
      </div>

      {/* Preview Modal */}
      {previewHtml && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.7)', zIndex: 9999,
          display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
          padding: 20,
        }}>
          <div style={{
            background: '#1e293b', borderRadius: 12, width: '90vw', maxWidth: 1200,
            height: '85vh', display: 'flex', flexDirection: 'column', overflow: 'hidden',
            boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
          }}>
            <div style={{
              padding: '12px 20px', display: 'flex', justifyContent: 'space-between',
              alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.1)',
            }}>
              <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 14 }}>
                🔍 Website Preview
              </span>
              <div style={{ display: 'flex', gap: 8 }}>
                <button
                  onClick={confirmDeploy}
                  style={{
                    padding: '6px 16px', fontSize: 13, fontWeight: 600,
                    background: '#10b981', color: 'white', border: 'none',
                    borderRadius: 6, cursor: 'pointer',
                  }}
                >
                  ✅ Looks Good — Deploy!
                </button>
                <button
                  onClick={() => setPreviewHtml(null)}
                  style={{
                    padding: '6px 16px', fontSize: 13, fontWeight: 600,
                    background: 'rgba(255,255,255,0.1)', color: '#e2e8f0',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: 6, cursor: 'pointer',
                  }}
                >
                  ✕ Close
                </button>
              </div>
            </div>
            <iframe
              srcDoc={previewHtml}
              title="Website Preview"
              style={{ flex: 1, border: 'none', background: 'white' }}
              sandbox="allow-scripts"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default WebsiteBuilder;

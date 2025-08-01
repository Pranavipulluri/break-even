// AI Services integration for Break-even frontend
import { api } from './api';

export const aiServices = {
  // Gemini AI Services
  gemini: {
    generateContent: async (prompt, maxTokens = 1000) => {
      const response = await api.post('/ai-tools/gemini/generate-content', {
        prompt,
        max_tokens: maxTokens
      });
      return response.data;
    },

    generateBusinessDescription: async (businessName, businessType, keyFeatures) => {
      const response = await api.post('/ai-tools/gemini/business-description', {
        business_name: businessName,
        business_type: businessType,
        key_features: keyFeatures
      });
      return response.data;
    },

    generateWebsiteContent: async (businessInfo) => {
      const response = await api.post('/ai-tools/gemini/website-content', {
        business_info: businessInfo
      });
      return response.data;
    },

    generateSocialMedia: async (businessName, businessType, occasion = null) => {
      const response = await api.post('/ai-tools/gemini/social-media', {
        business_name: businessName,
        business_type: businessType,
        occasion
      });
      return response.data;
    }
  },

  // GitHub Integration
  github: {
    createWebsite: async (businessName, websiteContent) => {
      const response = await api.post('/ai-tools/github/create-website', {
        business_name: businessName,
        website_content: websiteContent
      });
      return response.data;
    }
  },

  // Netlify Integration
  netlify: {
    deployWebsite: async (businessName, websiteContent) => {
      const response = await api.post('/ai-tools/netlify/deploy-website', {
        business_name: businessName,
        website_content: websiteContent
      });
      return response.data;
    }
  },

  // General
  getDeployments: async () => {
    const response = await api.get('/ai-tools/deployments');
    return response.data;
  }
};

// AI-powered website builder workflow
export const aiWebsiteBuilder = {
  async createCompleteWebsite(businessInfo, deploymentPlatform = 'netlify') {
    try {
      // Step 1: Generate website content using Gemini AI
      console.log('🤖 Generating website content with AI...');
      const contentResult = await aiServices.gemini.generateWebsiteContent(businessInfo);
      
      if (!contentResult.success) {
        throw new Error('Failed to generate website content');
      }

      const websiteContent = contentResult.parsed_content || {
        hero_title: `Welcome to ${businessInfo.name}`,
        hero_subtitle: 'Your trusted business partner',
        about_us: `${businessInfo.name} is dedicated to providing excellent service.`,
        services_intro: 'We offer comprehensive services to meet your needs.',
        contact_cta: 'Ready to get started? Contact us today!',
        phone: businessInfo.contact_info?.phone || '',
        email: businessInfo.contact_info?.email || '',
        address: businessInfo.area || ''
      };

      // Step 2: Deploy to selected platform
      console.log(`🚀 Deploying to ${deploymentPlatform}...`);
      let deployResult;
      
      if (deploymentPlatform === 'netlify') {
        deployResult = await aiServices.netlify.deployWebsite(businessInfo.name, websiteContent);
      } else if (deploymentPlatform === 'github') {
        deployResult = await aiServices.github.createWebsite(businessInfo.name, websiteContent);
      } else {
        throw new Error('Unsupported deployment platform');
      }

      if (!deployResult.success) {
        throw new Error(`Deployment failed: ${deployResult.error}`);
      }

      return {
        success: true,
        websiteContent,
        deployment: deployResult,
        websiteUrl: deployResult.website_url,
        platform: deploymentPlatform
      };

    } catch (error) {
      console.error('AI Website Builder Error:', error);
      return {
        success: false,
        error: error.message || 'Failed to create website'
      };
    }
  }
};

// AI Content Generator Hook
export const useAIContentGenerator = () => {
  const generateBusinessContent = async (businessName, businessType) => {
    try {
      const [descriptionResult, socialResult] = await Promise.all([
        aiServices.gemini.generateBusinessDescription(businessName, businessType),
        aiServices.gemini.generateSocialMedia(businessName, businessType)
      ]);

      return {
        description: descriptionResult.success ? descriptionResult.content : null,
        socialMedia: socialResult.success ? socialResult.content : null,
        errors: {
          description: !descriptionResult.success ? descriptionResult.error : null,
          socialMedia: !socialResult.success ? socialResult.error : null
        }
      };
    } catch (error) {
      console.error('Content generation error:', error);
      return {
        description: null,
        socialMedia: null,
        errors: { general: error.message }
      };
    }
  };

  return { generateBusinessContent };
};

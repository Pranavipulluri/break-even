import React from 'react';
import { ExternalLink, Eye, EyeOff } from 'lucide-react';

const WebsitePreview = ({ websiteData, isVisible = true, onToggle }) => {
  if (!websiteData) return null;

  const {
    website_name = 'My Website',
    business_type = 'Business',
    area = 'Local Area',
    theme = 'modern',
    website_url = null,
    contact_email = 'contact@business.com',
    contact_phone = '',
    theme_color = '#3B82F6'
  } = websiteData;

  const generatePreviewHTML = () => {
    return `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>${website_name}</title>
        <style>
          * { margin: 0; padding: 0; box-sizing: border-box; }
          body { font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }
          .container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }
          .header { background: linear-gradient(135deg, ${theme_color}, ${theme_color}dd); color: white; padding: 2rem 0; text-align: center; }
          .hero-title { font-size: 2.5rem; font-weight: bold; margin-bottom: 1rem; }
          .hero-subtitle { font-size: 1.2rem; opacity: 0.9; }
          .section { padding: 3rem 0; }
          .about { background: #f8f9fa; }
          .about-content { max-width: 800px; margin: 0 auto; text-align: center; }
          .section-title { font-size: 2rem; margin-bottom: 2rem; color: ${theme_color}; }
          .contact { background: ${theme_color}11; text-align: center; }
          .contact-info { display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem; }
          .contact-item { background: white; padding: 1rem 2rem; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
          .footer { background: #333; color: white; text-align: center; padding: 2rem 0; }
        </style>
      </head>
      <body>
        <header class="header">
          <div class="container">
            <h1 class="hero-title">${website_name}</h1>
            <p class="hero-subtitle">Professional ${business_type} services in ${area}</p>
          </div>
        </header>
        
        <section class="section about">
          <div class="container">
            <div class="about-content">
              <h2 class="section-title">About Us</h2>
              <p>Welcome to ${website_name}. We provide excellent ${business_type} services in ${area}. Our team is dedicated to delivering quality results and exceptional customer service.</p>
            </div>
          </div>
        </section>
        
        <section class="section contact">
          <div class="container">
            <h2 class="section-title">Contact Us</h2>
            <p>Get in touch with us today for more information!</p>
            <div class="contact-info">
              ${contact_email ? `<div class="contact-item">
                <strong>Email</strong><br>${contact_email}
              </div>` : ''}
              ${contact_phone ? `<div class="contact-item">
                <strong>Phone</strong><br>${contact_phone}
              </div>` : ''}
              ${area ? `<div class="contact-item">
                <strong>Location</strong><br>${area}
              </div>` : ''}
            </div>
          </div>
        </section>
        
        <footer class="footer">
          <div class="container">
            <p>&copy; 2025 ${website_name}. All rights reserved.</p>
          </div>
        </footer>
      </body>
      </html>
    `;
  };

  if (!isVisible) {
    return (
      <button
        onClick={onToggle}
        className="flex items-center space-x-2 px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
      >
        <Eye size={16} />
        <span>Show Preview</span>
      </button>
    );
  }

  return (
    <div className="border rounded-lg overflow-hidden bg-white shadow-sm">
      <div className="bg-gray-50 px-4 py-3 border-b flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex space-x-1">
            <div className="w-3 h-3 bg-red-400 rounded-full"></div>
            <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
            <div className="w-3 h-3 bg-green-400 rounded-full"></div>
          </div>
          <div className="text-sm text-gray-600 font-mono bg-white px-3 py-1 rounded border">
            {website_url || `preview-${website_name.toLowerCase().replace(/\s+/g, '-')}.com`}
          </div>
          {website_url && (
            <a
              href={website_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 p-1 rounded hover:bg-blue-50"
              title="Open live website"
            >
              <ExternalLink size={14} />
            </a>
          )}
        </div>
        
        <button
          onClick={onToggle}
          className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
        >
          <EyeOff size={14} />
          <span className="text-sm">Hide</span>
        </button>
      </div>
      
      <div className="relative">
        <iframe
          srcDoc={generatePreviewHTML()}
          className="w-full border-0"
          style={{ height: '600px' }}
          title="Website Preview"
          sandbox="allow-same-origin"
        />
        
        {!website_url && (
          <div className="absolute top-4 right-4 bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm font-medium">
            Preview Mode
          </div>
        )}
        
        {website_url && (
          <div className="absolute top-4 right-4 bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
            Live Website
          </div>
        )}
      </div>
      
      <div className="bg-gray-50 px-4 py-3 border-t">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center space-x-4">
            <span>Theme: <span className="font-medium">{theme}</span></span>
            <span>Type: <span className="font-medium">{business_type}</span></span>
            {area && <span>Area: <span className="font-medium">{area}</span></span>}
          </div>
          
          {website_url ? (
            <div className="flex items-center space-x-2 text-green-600">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="font-medium">Deployed</span>
            </div>
          ) : (
            <div className="flex items-center space-x-2 text-yellow-600">
              <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
              <span className="font-medium">Not Deployed</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WebsitePreview;

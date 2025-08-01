import React, { useState, useEffect } from 'react';
import { Download, Share2, Copy, ExternalLink } from 'lucide-react';
import QRCodeReact from 'qrcode.react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const QRCode = () => {
  const { user } = useAuth();
  const [qrData, setQrData] = useState(null);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [deployedWebsites, setDeployedWebsites] = useState([]);
  const [selectedWebsiteUrl, setSelectedWebsiteUrl] = useState('');
  const [qrSize, setQrSize] = useState(256);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchQRData();
  }, []);

  const fetchQRData = async () => {
    try {
      // Use development endpoint for now
      const response = await fetch('http://localhost:5000/api/qr-code/dev');
      const data = await response.json();
      
      setQrData(data);
      setWebsiteUrl(data.websiteUrl);
      setDeployedWebsites(data.deployedWebsites || []);
      setSelectedWebsiteUrl(data.websiteUrl);
    } catch (error) {
      console.error('QR fetch error:', error);
      toast.error('Failed to fetch QR code data');
    }
  };

  const updateQRUrl = async (newUrl) => {
    try {
      setLoading(true);
      
      const response = await fetch('http://localhost:5000/api/qr-code/dev/update-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ website_url: newUrl })
      });
      
      const result = await response.json();
      
      if (response.ok) {
        setWebsiteUrl(newUrl);
        setSelectedWebsiteUrl(newUrl);
        toast.success('QR code updated successfully!');
      } else {
        throw new Error(result.error || 'Failed to update QR code');
      }
    } catch (error) {
      console.error('QR update error:', error);
      toast.error(error.message || 'Failed to update QR code');
    } finally {
      setLoading(false);
    }
  };

  const downloadQR = () => {
    const canvas = document.getElementById('qr-code');
    const pngUrl = canvas
      .toDataURL("image/png")
      .replace("image/png", "image/octet-stream");
    
    let downloadLink = document.createElement("a");
    downloadLink.href = pngUrl;
    downloadLink.download = `${user?.businessName || 'business'}-qr-code.png`;
    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const shareQR = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: `${user?.businessName} - Visit our website`,
          text: 'Check out our products and services!',
          url: websiteUrl
        });
      } catch (error) {
        console.log('Error sharing:', error);
      }
    } else {
      copyToClipboard(websiteUrl);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">QR Code</h1>
        <p className="text-gray-600 mt-2">Your business QR code for customer access</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* QR Code Display */}
        <div className="card text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-6">Your Business QR Code</h3>
          
          <div className="flex justify-center mb-6">
            <div className="p-4 bg-white rounded-xl shadow-sm border-2 border-gray-200">
              <QRCodeReact
                id="qr-code"
                value={websiteUrl}
                size={qrSize}
                bgColor="#ffffff"
                fgColor="#000000"
                level="M"
                includeMargin={true}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                QR Code Size
              </label>
              <input
                type="range"
                min="128"
                max="512"
                value={qrSize}
                onChange={(e) => setQrSize(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="flex justify-between text-sm text-gray-500 mt-1">
                <span>128px</span>
                <span>{qrSize}px</span>
                <span>512px</span>
              </div>
            </div>

            <div className="flex space-x-2">
              <button
                onClick={downloadQR}
                className="btn-primary flex items-center space-x-2 flex-1"
              >
                <Download size={16} />
                <span>Download</span>
              </button>
              <button
                onClick={shareQR}
                className="btn-secondary flex items-center space-x-2 flex-1"
              >
                <Share2 size={16} />
                <span>Share</span>
              </button>
            </div>
          </div>
        </div>

        {/* QR Code Information */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Website Information</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Website URL
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={websiteUrl}
                    readOnly
                    className="input-field flex-1"
                  />
                  <button
                    onClick={() => copyToClipboard(websiteUrl)}
                    className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <Copy size={16} />
                  </button>
                  <a
                    href={websiteUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <ExternalLink size={16} />
                  </a>
                </div>
              </div>

              {deployedWebsites.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Deployed Website for QR Code
                  </label>
                  <div className="space-y-2">
                    {deployedWebsites.map((website) => (
                      <div key={website.id} className="flex items-center justify-between p-3 border rounded-lg hover:bg-gray-50">
                        <div className="flex-1">
                          <div className="font-medium text-gray-900">{website.name}</div>
                          <div className="text-sm text-gray-500 truncate">{website.url}</div>
                          <div className="text-xs text-gray-400 flex items-center space-x-2">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              website.platform === 'netlify' ? 'bg-teal-100 text-teal-800' :
                              website.platform === 'github' ? 'bg-gray-100 text-gray-800' :
                              'bg-blue-100 text-blue-800'
                            }`}>
                              {website.platform}
                            </span>
                          </div>
                        </div>
                        <button
                          onClick={() => updateQRUrl(website.url)}
                          disabled={loading || websiteUrl === website.url}
                          className={`ml-3 px-3 py-1 text-sm font-medium rounded-md transition-colors ${
                            websiteUrl === website.url
                              ? 'bg-green-100 text-green-800 cursor-default'
                              : 'bg-blue-100 text-blue-800 hover:bg-blue-200'
                          }`}
                        >
                          {websiteUrl === website.url ? 'Current' : 'Use This'}
                        </button>
                      </div>
                    ))}
                  </div>
                  
                  <div className="mt-3 text-sm text-gray-600">
                    💡 Tip: Deploy a website from the Website Builder, then select it here to update your QR code.
                  </div>
                </div>
              )}

              {deployedWebsites.length === 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <div className="text-sm text-blue-800">
                    <strong>No deployed websites found.</strong>
                  </div>
                  <div className="text-sm text-blue-600 mt-1">
                    Go to the Website Builder and deploy a website to Netlify or GitHub Pages, then return here to update your QR code.
                  </div>
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Business Name
                </label>
                <input
                  type="text"
                  value={user?.businessName || ''}
                  readOnly
                  className="input-field"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  QR Scans Today
                </label>
                <div className="text-2xl font-bold text-primary-600">
                  {qrData?.scansToday || 0}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Total QR Scans
                </label>
                <div className="text-2xl font-bold text-gray-900">
                  {qrData?.totalScans || 0}
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Usage Tips</h3>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>Print your QR code and display it prominently at your business location</span>
              </li>
              <li className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>Include the QR code on business cards, flyers, and promotional materials</span>
              </li>
              <li className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>Make sure the QR code is large enough to scan easily (minimum 2cm x 2cm)</span>
              </li>
              <li className="flex items-start space-x-2">
                <div className="w-2 h-2 bg-primary-500 rounded-full mt-2 flex-shrink-0"></div>
                <span>Test your QR code regularly to ensure it works properly</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QRCode;

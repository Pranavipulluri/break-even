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
  const [qrSize, setQrSize] = useState(256);

  useEffect(() => {
    fetchQRData();
  }, []);

  const fetchQRData = async () => {
    try {
      const response = await api.get('/qr-code');
      setQrData(response.data);
      setWebsiteUrl(response.data.websiteUrl);
    } catch (error) {
      toast.error('Failed to fetch QR code data');
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

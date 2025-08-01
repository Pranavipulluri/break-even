import React, { useState, useEffect } from 'react';
import { Download, Share2, Copy, ExternalLink, QrCode as QrCodeIcon, Zap, Palette, Settings, BarChart3 } from 'lucide-react';
import QRCodeReact from 'qrcode.react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const QRCode = () => {
  const { user } = useAuth();
  const [qrData, setQrData] = useState(null);
  const [websiteUrl, setWebsiteUrl] = useState('');
  const [qrSize, setQrSize] = useState(256);
  const [qrColor, setQrColor] = useState('#000000');
  const [bgColor, setBgColor] = useState('#ffffff');
  const [logoUrl, setLogoUrl] = useState('');
  const [selectedStyle, setSelectedStyle] = useState('square');

  const qrStyles = [
    { id: 'square', name: 'Square', preview: '⬛' },
    { id: 'rounded', name: 'Rounded', preview: '🔲' },
    { id: 'dots', name: 'Dots', preview: '⚫' },
    { id: 'circular', name: 'Circular', preview: '⭕' },
  ];

  const colorPresets = [
    { name: 'Classic', fg: '#000000', bg: '#ffffff' },
    { name: 'Blue', fg: '#3b82f6', bg: '#eff6ff' },
    { name: 'Green', fg: '#10b981', bg: '#ecfdf5' },
    { name: 'Purple', fg: '#8b5cf6', bg: '#f3e8ff' },
    { name: 'Red', fg: '#ef4444', bg: '#fef2f2' },
  ];

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
    
    toast.success('QR code downloaded! 📱');
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard! 📋');
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

  const applyColorPreset = (preset) => {
    setQrColor(preset.fg);
    setBgColor(preset.bg);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="text-center">
        <h1 className="heading-1 mb-4">QR Code Studio</h1>
        <p className="text-xl text-gray-600 max-w-3xl mx-auto">
          Create beautiful, customizable QR codes for your business. 
          Drive customers from physical locations to your digital presence.
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card bg-gradient-to-br from-blue-500 to-indigo-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium">Total Scans</p>
              <p className="text-3xl font-bold">{qrData?.totalScans || 0}</p>
            </div>
            <QrCodeIcon className="text-blue-200" size={32} />
          </div>
        </div>
        
        <div className="card bg-gradient-to-br from-green-500 to-emerald-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium">Today's Scans</p>
              <p className="text-3xl font-bold">{qrData?.scansToday || 0}</p>
            </div>
            <BarChart3 className="text-green-200" size={32} />
          </div>
        </div>
        
        <div className="card bg-gradient-to-br from-purple-500 to-pink-600 text-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium">Conversion Rate</p>
              <p className="text-3xl font-bold">12.5%</p>
            </div>
            <Zap className="text-purple-200" size={32} />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* QR Code Generator */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="heading-3 text-gray-900 mb-6 flex items-center space-x-2">
              <QrCodeIcon className="text-primary-600" size={24} />
              <span>Your QR Code</span>
            </h3>
            
            <div className="text-center mb-6">
              <div className="inline-block p-6 bg-gradient-to-br from-gray-50 to-white rounded-2xl shadow-inner border-2 border-gray-100">
                <QRCodeReact
                  id="qr-code"
                  value={websiteUrl}
                  size={qrSize}
                  bgColor={bgColor}
                  fgColor={qrColor}
                  level="M"
                  includeMargin={true}
                  imageSettings={logoUrl ? {
                    src: logoUrl,
                    x: null,
                    y: null,
                    height: qrSize * 0.15,
                    width: qrSize * 0.15,
                    excavate: true,
                  } : undefined}
                />
              </div>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={downloadQR}
                className="btn-primary flex-1 flex items-center justify-center space-x-2"
              >
                <Download size={18} />
                <span>Download</span>
              </button>
              <button
                onClick={shareQR}
                className="btn-secondary flex items-center justify-center space-x-2 px-4"
              >
                <Share2 size={18} />
                <span>Share</span>
              </button>
            </div>
          </div>

          {/* Website Info */}
          <div className="card">
            <h3 className="heading-3 text-gray-900 mb-6">Website Information</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Website URL
                </label>
                <div className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={websiteUrl}
                    readOnly
                    className="input-field flex-1 bg-gray-50"
                  />
                  <button
                    onClick={() => copyToClipboard(websiteUrl)}
                    className="p-3 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-colors"
                  >
                    <Copy size={18} />
                  </button>
                  <a
                    href={websiteUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="p-3 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-xl transition-colors"
                  >
                    <ExternalLink size={18} />
                  </a>
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Business Name
                </label>
                <input
                  type="text"
                  value={user?.businessName || ''}
                  readOnly
                  className="input-field bg-gray-50"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Customization Panel */}
        <div className="space-y-6">
          <div className="card">
            <h3 className="heading-3 text-gray-900 mb-6 flex items-center space-x-2">
              <Palette className="text-purple-600" size={24} />
              <span>Customize Design</span>
            </h3>

            <div className="space-y-6">
              {/* Size Slider */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Size: {qrSize}px
                </label>
                <input
                  type="range"
                  min="128"
                  max="512"
                  value={qrSize}
                  onChange={(e) => setQrSize(parseInt(e.target.value))}
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                />
                <div className="flex justify-between text-sm text-gray-500 mt-1">
                  <span>128px</span>
                  <span>512px</span>
                </div>
              </div>

              {/* Color Presets */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">
                  Color Presets
                </label>
                <div className="grid grid-cols-5 gap-2">
                  {colorPresets.map((preset, index) => (
                    <button
                      key={index}
                      onClick={() => applyColorPreset(preset)}
                      className="aspect-square rounded-xl border-2 border-gray-200 hover:border-gray-300 transition-colors relative overflow-hidden group"
                      style={{ backgroundColor: preset.bg }}
                    >
                      <div 
                        className="absolute inset-2 rounded-lg"
                        style={{ backgroundColor: preset.fg }}
                      ></div>
                      <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors rounded-xl"></div>
                    </button>
                  ))}
                </div>
              </div>

              {/* Custom Colors */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Foreground Color
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={qrColor}
                      onChange={(e) => setQrColor(e.target.value)}
                      className="w-12 h-12 rounded-xl border border-gray-200 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={qrColor}
                      onChange={(e) => setQrColor(e.target.value)}
                      className="input-field flex-1 font-mono text-sm"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Background Color
                  </label>
                  <div className="flex items-center space-x-2">
                    <input
                      type="color"
                      value={bgColor}
                      onChange={(e) => setBgColor(e.target.value)}
                      className="w-12 h-12 rounded-xl border border-gray-200 cursor-pointer"
                    />
                    <input
                      type="text"
                      value={bgColor}
                      onChange={(e) => setBgColor(e.target.value)}
                      className="input-field flex-1 font-mono text-sm"
                    />
                  </div>
                </div>
              </div>

              {/* Logo Upload */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Logo URL (Optional)
                </label>
                <input
                  type="url"
                  value={logoUrl}
                  onChange={(e) => setLogoUrl(e.target.value)}
                  className="input-field"
                  placeholder="https://example.com/logo.png"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Add your business logo to the center of the QR code
                </p>
              </div>
            </div>
          </div>

          {/* Usage Tips */}
          <div className="card bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200">
            <h3 className="heading-3 text-indigo-900 mb-4">💡 Usage Tips</h3>
            <ul className="space-y-3 text-sm text-indigo-800">
              <li className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Print your QR code at least 2cm x 2cm for reliable scanning</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Display prominently at your business entrance and checkout</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Include on business cards, flyers, and promotional materials</span>
              </li>
              <li className="flex items-start space-x-2">
                <span className="w-2 h-2 bg-indigo-500 rounded-full mt-2 flex-shrink-0"></span>
                <span>Test scanning from different devices before printing</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default QRCode;

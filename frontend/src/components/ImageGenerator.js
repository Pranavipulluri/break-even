import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ImageGenerator.css';

const ImageGenerator = () => {
    const [activeTab, setActiveTab] = useState('poster');
    const [loading, setLoading] = useState(false);
    const [generatedImages, setGeneratedImages] = useState([]);
    const [accountInfo, setAccountInfo] = useState(null);
    const [presets, setPresets] = useState({});

    // Form data states
    const [posterData, setPosterData] = useState({
        business_name: '',
        business_type: '',
        style: 'professional',
        additional_text: ''
    });

    const [productData, setProductData] = useState({
        product_name: '',
        product_description: '',
        style: 'high-quality product photo'
    });

    const [bannerData, setBannerData] = useState({
        business_name: '',
        message: '',
        dimensions: 'banner',
        style: 'modern'
    });

    const [heroData, setHeroData] = useState({
        business_name: '',
        business_type: '',
        mood: 'professional and welcoming'
    });

    useEffect(() => {
        fetchAccountInfo();
        fetchPresets();
    }, []);

    const fetchAccountInfo = async () => {
        try {
            const response = await axios.get('/api/images/account-info');
            if (response.data.success) {
                setAccountInfo(response.data.account);
            }
        } catch (error) {
            console.error('Error fetching account info:', error);
        }
    };

    const fetchPresets = async () => {
        try {
            const response = await axios.get('/api/images/business-presets');
            if (response.data.success) {
                setPresets(response.data.presets);
            }
        } catch (error) {
            console.error('Error fetching presets:', error);
        }
    };

    const generateBusinessPoster = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/images/generate-business-poster', posterData);
            if (response.data.success) {
                setGeneratedImages(response.data.images);
            } else {
                alert('Error: ' + response.data.error);
            }
        } catch (error) {
            alert('Generation failed: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const generateProductImage = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/images/generate-product-image', productData);
            if (response.data.success) {
                setGeneratedImages(response.data.images);
            } else {
                alert('Error: ' + response.data.error);
            }
        } catch (error) {
            alert('Generation failed: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const generateMarketingBanner = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/images/generate-marketing-banner', bannerData);
            if (response.data.success) {
                setGeneratedImages(response.data.images);
            } else {
                alert('Error: ' + response.data.error);
            }
        } catch (error) {
            alert('Generation failed: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const generateHeroImage = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/images/generate-hero-image', heroData);
            if (response.data.success) {
                setGeneratedImages(response.data.images);
            } else {
                alert('Error: ' + response.data.error);
            }
        } catch (error) {
            alert('Generation failed: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const generateCompleteBranding = async () => {
        setLoading(true);
        try {
            const response = await axios.post('/api/images/generate-business-branding', {
                business_name: posterData.business_name,
                business_type: posterData.business_type,
                style: posterData.style
            });
            
            if (response.data.success) {
                // Collect all generated images from all results
                const allImages = [];
                Object.values(response.data.results).forEach(result => {
                    if (result.success && result.images) {
                        allImages.push(...result.images);
                    }
                });
                setGeneratedImages(allImages);
                alert(`Complete branding generated! ${response.data.summary.successful} out of ${response.data.summary.total_requested} images created successfully.`);
            } else {
                alert('Error: ' + response.data.error);
            }
        } catch (error) {
            alert('Branding generation failed: ' + error.message);
        } finally {
            setLoading(false);
        }
    };

    const renderPosterTab = () => (
        <div className="tab-content">
            <h3>🎨 Business Poster Generator</h3>
            <div className="form-group">
                <label>Business Name *</label>
                <input
                    type="text"
                    value={posterData.business_name}
                    onChange={(e) => setPosterData({...posterData, business_name: e.target.value})}
                    placeholder="Enter your business name"
                />
            </div>
            <div className="form-group">
                <label>Business Type *</label>
                <select
                    value={posterData.business_type}
                    onChange={(e) => setPosterData({...posterData, business_type: e.target.value})}
                >
                    <option value="">Select business type</option>
                    <option value="bakery">Bakery</option>
                    <option value="restaurant">Restaurant</option>
                    <option value="retail">Retail Store</option>
                    <option value="service">Service Business</option>
                    <option value="beauty">Beauty Salon</option>
                    <option value="fitness">Fitness Center</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div className="form-group">
                <label>Style</label>
                <select
                    value={posterData.style}
                    onChange={(e) => setPosterData({...posterData, style: e.target.value})}
                >
                    <option value="professional">Professional</option>
                    <option value="creative">Creative</option>
                    <option value="minimal">Minimal</option>
                    <option value="vintage">Vintage</option>
                    <option value="modern">Modern</option>
                </select>
            </div>
            <div className="form-group">
                <label>Additional Details (Optional)</label>
                <textarea
                    value={posterData.additional_text}
                    onChange={(e) => setPosterData({...posterData, additional_text: e.target.value})}
                    placeholder="Any specific themes or elements you want included"
                    rows="3"
                />
            </div>
            <button 
                className="generate-btn"
                onClick={generateBusinessPoster}
                disabled={loading || !posterData.business_name || !posterData.business_type}
            >
                {loading ? '🎨 Generating...' : '🎨 Generate Business Poster'}
            </button>
        </div>
    );

    const renderProductTab = () => (
        <div className="tab-content">
            <h3>📸 Product Image Generator</h3>
            <div className="form-group">
                <label>Product Name *</label>
                <input
                    type="text"
                    value={productData.product_name}
                    onChange={(e) => setProductData({...productData, product_name: e.target.value})}
                    placeholder="Enter product name"
                />
            </div>
            <div className="form-group">
                <label>Product Description</label>
                <textarea
                    value={productData.product_description}
                    onChange={(e) => setProductData({...productData, product_description: e.target.value})}
                    placeholder="Describe your product in detail"
                    rows="3"
                />
            </div>
            <div className="form-group">
                <label>Photography Style</label>
                <select
                    value={productData.style}
                    onChange={(e) => setProductData({...productData, style: e.target.value})}
                >
                    <option value="high-quality product photo">High-Quality Product Photo</option>
                    <option value="lifestyle product photography">Lifestyle Photography</option>
                    <option value="minimalist product shot">Minimalist Shot</option>
                    <option value="artisanal product styling">Artisanal Styling</option>
                    <option value="commercial product display">Commercial Display</option>
                </select>
            </div>
            <button 
                className="generate-btn"
                onClick={generateProductImage}
                disabled={loading || !productData.product_name}
            >
                {loading ? '📸 Generating...' : '📸 Generate Product Image'}
            </button>
        </div>
    );

    const renderBannerTab = () => (
        <div className="tab-content">
            <h3>🎯 Marketing Banner Generator</h3>
            <div className="form-group">
                <label>Business Name *</label>
                <input
                    type="text"
                    value={bannerData.business_name}
                    onChange={(e) => setBannerData({...bannerData, business_name: e.target.value})}
                    placeholder="Enter your business name"
                />
            </div>
            <div className="form-group">
                <label>Marketing Message *</label>
                <input
                    type="text"
                    value={bannerData.message}
                    onChange={(e) => setBannerData({...bannerData, message: e.target.value})}
                    placeholder="Enter your marketing message"
                />
            </div>
            <div className="form-group">
                <label>Banner Size</label>
                <select
                    value={bannerData.dimensions}
                    onChange={(e) => setBannerData({...bannerData, dimensions: e.target.value})}
                >
                    <option value="banner">Web Banner (1344x448)</option>
                    <option value="social">Social Media (1200x630)</option>
                    <option value="facebook">Facebook Post (1200x630)</option>
                    <option value="instagram">Instagram Square (1080x1080)</option>
                    <option value="twitter">Twitter Header (1200x600)</option>
                    <option value="linkedin">LinkedIn Post (1200x627)</option>
                    <option value="wide">Wide Screen (1920x1080)</option>
                </select>
            </div>
            <div className="form-group">
                <label>Design Style</label>
                <select
                    value={bannerData.style}
                    onChange={(e) => setBannerData({...bannerData, style: e.target.value})}
                >
                    <option value="modern">Modern</option>
                    <option value="professional">Professional</option>
                    <option value="creative">Creative</option>
                    <option value="elegant">Elegant</option>
                    <option value="bold">Bold</option>
                </select>
            </div>
            <button 
                className="generate-btn"
                onClick={generateMarketingBanner}
                disabled={loading || !bannerData.business_name || !bannerData.message}
            >
                {loading ? '🎯 Generating...' : '🎯 Generate Marketing Banner'}
            </button>
        </div>
    );

    const renderHeroTab = () => (
        <div className="tab-content">
            <h3>🌟 Website Hero Image Generator</h3>
            <div className="form-group">
                <label>Business Name *</label>
                <input
                    type="text"
                    value={heroData.business_name}
                    onChange={(e) => setHeroData({...heroData, business_name: e.target.value})}
                    placeholder="Enter your business name"
                />
            </div>
            <div className="form-group">
                <label>Business Type *</label>
                <select
                    value={heroData.business_type}
                    onChange={(e) => setHeroData({...heroData, business_type: e.target.value})}
                >
                    <option value="">Select business type</option>
                    <option value="bakery">Bakery</option>
                    <option value="restaurant">Restaurant</option>
                    <option value="retail">Retail Store</option>
                    <option value="service">Service Business</option>
                    <option value="beauty">Beauty Salon</option>
                    <option value="fitness">Fitness Center</option>
                    <option value="other">Other</option>
                </select>
            </div>
            <div className="form-group">
                <label>Atmosphere/Mood</label>
                <select
                    value={heroData.mood}
                    onChange={(e) => setHeroData({...heroData, mood: e.target.value})}
                >
                    <option value="professional and welcoming">Professional & Welcoming</option>
                    <option value="cozy and warm">Cozy & Warm</option>
                    <option value="modern and sleek">Modern & Sleek</option>
                    <option value="elegant and luxurious">Elegant & Luxurious</option>
                    <option value="energetic and vibrant">Energetic & Vibrant</option>
                    <option value="calm and peaceful">Calm & Peaceful</option>
                </select>
            </div>
            <button 
                className="generate-btn"
                onClick={generateHeroImage}
                disabled={loading || !heroData.business_name || !heroData.business_type}
            >
                {loading ? '🌟 Generating...' : '🌟 Generate Hero Image'}
            </button>
        </div>
    );

    return (
        <div className="image-generator">
            <div className="image-generator-header">
                <h2>🎨 AI Image Generator</h2>
                <p>Create professional business images using Stability AI</p>
                {accountInfo && (
                    <div className="account-info">
                        <span>Credits: {accountInfo.credits || 'N/A'}</span>
                    </div>
                )}
            </div>

            <div className="image-tabs">
                <button 
                    className={`tab-btn ${activeTab === 'poster' ? 'active' : ''}`}
                    onClick={() => setActiveTab('poster')}
                >
                    🎨 Business Poster
                </button>
                <button 
                    className={`tab-btn ${activeTab === 'product' ? 'active' : ''}`}
                    onClick={() => setActiveTab('product')}
                >
                    📸 Product Images
                </button>
                <button 
                    className={`tab-btn ${activeTab === 'banner' ? 'active' : ''}`}
                    onClick={() => setActiveTab('banner')}
                >
                    🎯 Marketing Banner
                </button>
                <button 
                    className={`tab-btn ${activeTab === 'hero' ? 'active' : ''}`}
                    onClick={() => setActiveTab('hero')}
                >
                    🌟 Hero Image
                </button>
            </div>

            <div className="image-generator-content">
                <div className="generation-panel">
                    {activeTab === 'poster' && renderPosterTab()}
                    {activeTab === 'product' && renderProductTab()}
                    {activeTab === 'banner' && renderBannerTab()}
                    {activeTab === 'hero' && renderHeroTab()}

                    <div className="branding-section">
                        <h4>🎯 Complete Business Branding</h4>
                        <p>Generate poster, hero image, and marketing banner all at once</p>
                        <button 
                            className="generate-btn complete-branding"
                            onClick={generateCompleteBranding}
                            disabled={loading || !posterData.business_name || !posterData.business_type}
                        >
                            {loading ? '🎨 Generating Complete Branding...' : '🎨 Generate Complete Branding'}
                        </button>
                    </div>
                </div>

                <div className="results-panel">
                    {loading && (
                        <div className="loading-state">
                            <div className="loading-spinner"></div>
                            <p>Generating your AI image... This may take 30-60 seconds</p>
                        </div>
                    )}

                    {generatedImages.length > 0 && (
                        <div className="generated-images">
                            <h4>Generated Images</h4>
                            <div className="images-grid">
                                {generatedImages.map((image, index) => (
                                    <div key={index} className="image-result">
                                        <img 
                                            src={`http://localhost:5000${image.url}`} 
                                            alt={`Generated ${index + 1}`}
                                            onError={(e) => {
                                                e.target.style.display = 'none';
                                                e.target.nextSibling.style.display = 'block';
                                            }}
                                        />
                                        <div className="image-error" style={{display: 'none'}}>
                                            Image failed to load
                                        </div>
                                        <div className="image-info">
                                            <p>Size: {image.size}</p>
                                            <p>File: {image.filename}</p>
                                            <a 
                                                href={`http://localhost:5000${image.url}`} 
                                                download={image.filename}
                                                className="download-btn"
                                            >
                                                📥 Download
                                            </a>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ImageGenerator;

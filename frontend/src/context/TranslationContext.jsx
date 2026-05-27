import { createContext, useContext, useEffect, useState } from 'react';

// Translation Context
const TranslationContext = createContext();

export const useTranslation = () => {
  const context = useContext(TranslationContext);
  if (!context) {
    throw new Error('useTranslation must be used within a TranslationProvider');
  }
  return context;
};

// Translation Provider Component
export const TranslationProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');
  const [translations, setTranslations] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [translationCache, setTranslationCache] = useState({});

  // Load translation cache from localStorage
  useEffect(() => {
    try {
      const cachedTranslations = localStorage.getItem('translation-cache');
      if (cachedTranslations) {
        setTranslationCache(JSON.parse(cachedTranslations));
      }
    } catch (error) {
      console.warn('Could not load translation cache:', error);
    }
  }, []);

  // Save translation cache to localStorage
  const saveTranslationCache = (newCache) => {
    try {
      setTranslationCache(newCache);
      localStorage.setItem('translation-cache', JSON.stringify(newCache));
    } catch (error) {
      console.warn('Could not save translation cache:', error);
    }
  };

  // Load UI translations for current language
  const loadTranslations = async (language) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`http://localhost:5000/api/translation/get-ui-translations?lang=${language}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Response is not JSON');
      }
      
      const data = await response.json();
      
      if (data.success && data.ui_translations) {
        setTranslations(data.ui_translations);
      } else {
        throw new Error(data.error || 'Failed to load translations');
      }
    } catch (err) {
      console.warn('Translation loading error:', err.message);
      setError(err.message);
      
      // Use fallback translations for common UI elements
      const fallbackTranslations = {
        'website_builder': language === 'te' ? 'వెబ్‌సైట్ బిల్డర్' : 
                          language === 'hi' ? 'वेबसाइट बिल्डर' :
                          'Website Builder',
        'create_business_website': language === 'te' ? 'మీ వ్యాపార వెబ్‌సైట్‌ను సృష్టించండి' :
                                  language === 'hi' ? 'अपनी व्यावसायिक वेबसाइट बनाएं' :
                                  'Create your business website',
        'update_business_website': language === 'te' ? 'మీ వ్యాపార వెబ్‌సైట్‌ను అప్‌డేట్ చేయండి' :
                                  language === 'hi' ? 'अपनी व्यावसायिक वेबसाइट को अपडेट करें' :
                                  'Update your business website',
        'business_name': language === 'te' ? 'వ్యాపార పేరు' :
                        language === 'hi' ? 'व्यवसाय का नाम' :
                        'Business Name',
        'services': language === 'te' ? 'సేవలు' :
                   language === 'hi' ? 'सेवाएं' :
                   'Services'
      };
      
      setTranslations(fallbackTranslations);
    } finally {
      setLoading(false);
    }
  };

  // Change language
  const changeLanguage = async (newLanguage) => {
    if (newLanguage === currentLanguage) return;
    
    setCurrentLanguage(newLanguage);
    await loadTranslations(newLanguage);
    
    // Store language preference
    localStorage.setItem('preferred-language', newLanguage);
  };

  // Translate text using API with caching
  const translateText = async (text, targetLang = currentLanguage, sourceLang = 'en') => {
    if (!text || targetLang === sourceLang) return text;
    
    // Check cache first
    const cacheKey = `${sourceLang}:${targetLang}:${text}`;
    if (translationCache[cacheKey]) {
      return translationCache[cacheKey];
    }
    
    try {
      const response = await fetch('http://localhost:5000/api/translation/translate-text', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          target_lang: targetLang,
          source_lang: sourceLang
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Cache the translation
        const newCache = { ...translationCache, [cacheKey]: data.translated_text };
        saveTranslationCache(newCache);
        
        return data.translated_text;
      } else {
        console.error('Translation failed:', data.error);
        return text; // Return original text on failure
      }
    } catch (error) {
      console.error('Translation request failed:', error);
      return text;
    }
  };

  // Translate website content
  const translateWebsiteContent = async (websiteData, targetLang = currentLanguage) => {
    if (!websiteData || targetLang === 'en') return websiteData;
    
    try {
      const response = await fetch('http://localhost:5000/api/translation/translate-website', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          website_data: websiteData,
          target_lang: targetLang
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Response is not JSON');
      }
      
      const data = await response.json();
      
      if (data.success && data.translated_website) {
        return data.translated_website;
      } else {
        throw new Error(data.error || 'Translation failed');
      }
    } catch (error) {
      console.warn('Website translation request failed:', error.message);
      // Return original data if translation fails
      return websiteData;
    }
  };

  // Translate business card content
  const translateBusinessCard = async (cardData, targetLang = currentLanguage) => {
    if (!cardData || targetLang === 'en') return cardData;
    
    try {
      const response = await fetch('http://localhost:5000/api/translation/translate-business-card', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          card_data: cardData,
          target_lang: targetLang
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        return data.translated_card;
      } else {
        console.error('Business card translation failed:', data.error);
        return cardData;
      }
    } catch (error) {
      console.error('Business card translation request failed:', error);
      return cardData;
    }
  };

  // Get translated text with fallback
  const t = (key, fallback = key) => {
    return translations[key] || fallback;
  };

  // Detect language of text
  const detectLanguage = async (text) => {
    if (!text) return 'en';
    
    try {
      const response = await fetch('http://localhost:5000/api/translation/detect-language', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text })
      });
      
      const data = await response.json();
      
      if (data.success) {
        return data.detected_language;
      } else {
        return 'en';
      }
    } catch (error) {
      console.error('Language detection failed:', error);
      return 'en';
    }
  };

  // Batch translate multiple items
  const batchTranslate = async (items, targetLang = currentLanguage, sourceLang = 'en') => {
    if (!items || !Array.isArray(items) || targetLang === sourceLang) return items;
    
    try {
      const response = await fetch('http://localhost:5000/api/translation/batch-translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          items,
          target_lang: targetLang,
          source_lang: sourceLang
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        return data.translated_items;
      } else {
        console.error('Batch translation failed:', data.error);
        return items;
      }
    } catch (error) {
      console.error('Batch translation request failed:', error);
      return items;
    }
  };

  // Initialize translation on mount
  useEffect(() => {
    const initializeTranslation = async () => {
      // Get stored language preference
      const storedLanguage = localStorage.getItem('preferred-language') || 'en';
      setCurrentLanguage(storedLanguage);
      
      // Load initial translations
      await loadTranslations(storedLanguage);
    };

    initializeTranslation();
  }, []);

  const contextValue = {
    currentLanguage,
    translations,
    loading,
    error,
    changeLanguage,
    translateText,
    translateWebsiteContent,
    translateBusinessCard,
    detectLanguage,
    batchTranslate,
    t, // Translation function
  };

  return (
    <TranslationContext.Provider value={contextValue}>
      {children}
    </TranslationContext.Provider>
  );
};

// HOC for translation support
export const withTranslation = (Component) => {
  return function WrappedComponent(props) {
    const translation = useTranslation();
    return <Component {...props} translation={translation} />;
  };
};

export default TranslationContext;
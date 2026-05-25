import { Check, ChevronDown, Globe } from 'lucide-react';
import { useEffect, useState } from 'react';

const LanguageSelector = ({ 
  currentLanguage = 'en', 
  onLanguageChange, 
  position = 'top-right',
  compact = false 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [availableLanguages, setAvailableLanguages] = useState({});
  const [loading, setLoading] = useState(true);

  // Load available languages from API
  useEffect(() => {
    const fetchLanguages = async () => {
      try {
        const response = await fetch('/api/translation/languages');
        
        // Check if response is ok and is JSON
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error('Response is not JSON');
        }
        
        const data = await response.json();
        
        if (data.success && data.languages) {
          setAvailableLanguages(data.languages);
        } else {
          throw new Error(data.error || 'API returned unsuccessful response');
        }
      } catch (error) {
        console.warn('Failed to load languages from API:', error.message);
        // Fallback to hardcoded languages - only English, Telugu, and Hindi
        setAvailableLanguages({
          'en': { name: 'English', native: 'English', flag: '🇺🇸' },
          'te': { name: 'Telugu', native: 'తెలుగు', flag: '🇮�' },
          'hi': { name: 'Hindi', native: 'हिंदी', flag: '�🇳' }
        });
      } finally {
        setLoading(false);
      }
    };

    fetchLanguages();
  }, []);

  const handleLanguageSelect = (langCode) => {
    setIsOpen(false);
    if (onLanguageChange) {
      onLanguageChange(langCode);
    }
  };

  const currentLang = availableLanguages[currentLanguage] || availableLanguages['en'];

  // Position classes
  const positionClasses = {
    'top-right': 'absolute top-4 right-4',
    'top-left': 'absolute top-4 left-4',
    'bottom-right': 'absolute bottom-4 right-4',
    'bottom-left': 'absolute bottom-4 left-4',
    'inline': 'relative'
  };

  if (loading) {
    return (
      <div className={`${positionClasses[position]} z-50`}>
        <div className="animate-pulse">
          <div className="w-8 h-8 bg-gray-200 rounded-full"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`${positionClasses[position]} z-50`}>
      <div className="relative">
        {/* Language Selector Button */}
        <button
          onClick={() => setIsOpen(!isOpen)}
          className={`
            flex items-center gap-2 bg-white border border-gray-200 rounded-lg shadow-lg
            hover:shadow-xl transition-all duration-200 hover:bg-gray-50
            ${compact ? 'p-2' : 'px-3 py-2'}
          `}
          title="Select Language"
        >
          {compact ? (
            <div className="flex items-center gap-1">
              <span className="text-lg">{currentLang?.flag || '🌐'}</span>
              <ChevronDown size={12} className={`transform transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </div>
          ) : (
            <>
              <Globe size={16} className="text-blue-600" />
              <span className="text-lg">{currentLang?.flag || '🌐'}</span>
              <span className="text-sm font-medium text-gray-700">
                {currentLang?.native || 'English'}
              </span>
              <ChevronDown size={16} className={`text-gray-400 transform transition-transform ${isOpen ? 'rotate-180' : ''}`} />
            </>
          )}
        </button>

        {/* Language Dropdown */}
        {isOpen && (
          <div className={`
            absolute ${position.includes('right') ? 'right-0' : 'left-0'} 
            ${position.includes('bottom') ? 'bottom-full mb-2' : 'top-full mt-2'}
            bg-white border border-gray-200 rounded-lg shadow-xl
            min-w-48 max-h-60 overflow-y-auto
            animate-in slide-in-from-top-2 duration-200
          `}>
            <div className="p-2">
              <div className="text-xs text-gray-500 px-2 py-1 border-b border-gray-100 mb-1">
                Select Language
              </div>
              
              {Object.entries(availableLanguages).map(([code, lang]) => (
                <button
                  key={code}
                  onClick={() => handleLanguageSelect(code)}
                  className={`
                    w-full flex items-center gap-3 px-3 py-2 rounded-md
                    hover:bg-blue-50 transition-colors duration-150
                    ${currentLanguage === code ? 'bg-blue-50 text-blue-700' : 'text-gray-700'}
                  `}
                >
                  <span className="text-lg">{lang.flag}</span>
                  <div className="flex-1 text-left">
                    <div className="text-sm font-medium">{lang.native}</div>
                    <div className="text-xs text-gray-500">{lang.name}</div>
                  </div>
                  {currentLanguage === code && (
                    <Check size={16} className="text-blue-600" />
                  )}
                </button>
              ))}
            </div>
            
            {/* Footer */}
            <div className="border-t border-gray-100 p-2">
              <div className="text-xs text-gray-400 text-center">
                Powered by Gemini AI
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Overlay to close dropdown */}
      {isOpen && (
        <div 
          className="fixed inset-0 -z-10"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default LanguageSelector;
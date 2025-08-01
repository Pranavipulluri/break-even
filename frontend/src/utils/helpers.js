import { REGEX_PATTERNS, DATE_FORMATS } from './constants';

export const formatCurrency = (amount, currency = 'USD') => {
  try {
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) return '$0.00';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(numAmount);
  } catch (error) {
    return '$0.00';
  }
};

export const formatNumber = (number, options = {}) => {
  try {
    const numValue = parseFloat(number);
    if (isNaN(numValue)) return '0';
    
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: options.decimals || 0,
      maximumFractionDigits: options.decimals || 0,
      ...options
    }).format(numValue);
  } catch (error) {
    return '0';
  }
};

export const formatDate = (date, format = DATE_FORMATS.SHORT) => {
  try {
    const dateObj = new Date(date);
    if (isNaN(dateObj.getTime())) return 'Invalid Date';
    
    switch (format) {
      case DATE_FORMATS.SHORT:
        return dateObj.toLocaleDateString();
      case DATE_FORMATS.LONG:
        return dateObj.toLocaleDateString('en-US', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
      case DATE_FORMATS.WITH_TIME:
        return dateObj.toLocaleString();
      default:
        return dateObj.toLocaleDateString();
    }
  } catch (error) {
    return 'Invalid Date';
  }
};

export const formatRelativeTime = (date) => {
  try {
    const now = new Date();
    const targetDate = new Date(date);
    const diffInSeconds = Math.floor((now - targetDate) / 1000);
    
    if (diffInSeconds < 60) return 'Just now';
    
    const diffInMinutes = Math.floor(diffInSeconds / 60);
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    const diffInWeeks = Math.floor(diffInDays / 7);
    if (diffInWeeks < 4) return `${diffInWeeks}w ago`;
    
    return formatDate(date);
  } catch (error) {
    return 'Unknown';
  }
};

export const truncateText = (text, maxLength = 100) => {
  if (!text) return '';
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const slugify = (text) => {
  return text
    .toString()
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')
    .replace(/[^\w\-]+/g, '')
    .replace(/\-\-+/g, '-')
    .replace(/^-+/, '')
    .replace(/-+$/, '');
};

export const capitalizeFirst = (str) => {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1);
};

export const capitalizeWords = (str) => {
  if (!str) return '';
  return str.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

export const validateEmail = (email) => {
  return REGEX_PATTERNS.EMAIL.test(email);
};

export const validatePhone = (phone) => {
  const cleanPhone = phone.replace(/\D/g, '');
  return cleanPhone.length >= 10 && cleanPhone.length <= 15;
};

export const validateUrl = (url) => {
  return REGEX_PATTERNS.URL.test(url);
};

export const formatPhoneNumber = (phoneNumber) => {
  const cleaned = phoneNumber.replace(/\D/g, '');
  
  if (cleaned.length === 10) {
    return `(${cleaned.slice(0, 3)}) ${cleaned.slice(3, 6)}-${cleaned.slice(6)}`;
  } else if (cleaned.length === 11 && cleaned[0] === '1') {
    return `+1 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7)}`;
  }
  
  return phoneNumber;
};

export const generateId = () => {
  return Math.random().toString(36).substr(2, 9);
};

export const debounce = (func, wait) => {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

export const throttle = (func, limit) => {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

export const downloadFile = (data, filename, type = 'application/json') => {
  const blob = new Blob([data], { type });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

export const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch (err) {
    // Fallback for older browsers
    const textArea = document.createElement('textarea');
    textArea.value = text;
    document.body.appendChild(textArea);
    textArea.select();
    try {
      document.execCommand('copy');
      return true;
    } catch (fallbackErr) {
      return false;
    } finally {
      document.body.removeChild(textArea);
    }
  }
};

export const getInitials = (name) => {
  if (!name) return '';
  return name
    .split(' ')
    .map(word => word.charAt(0))
    .join('')
    .toUpperCase()
    .slice(0, 2);
};

export const generateColorFromString = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 60%)`;
};

export const isValidImageUrl = (url) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => resolve(true);
    img.onerror = () => resolve(false);
    img.src = url;
  });
};

export const getFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

export const sortArrayByKey = (array, key, direction = 'asc') => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (direction === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });
};

export const groupArrayByKey = (array, key) => {
  return array.reduce((result, item) => {
    const group = item[key];
    if (!result[group]) {
      result[group] = [];
    }
    result[group].push(item);
    return result;
  }, {});
};

export const calculatePercentageChange = (oldValue, newValue) => {
  if (oldValue === 0) return newValue > 0 ? 100 : 0;
  return ((newValue - oldValue) / oldValue) * 100;
};

export const getBusinessHoursStatus = (hours) => {
  if (!hours) return { isOpen: false, message: 'Hours not specified' };
  
  const now = new Date();
  const currentDay = now.toLocaleDateString('en-US', { weekday: 'long' }).toLowerCase();
  const currentTime = now.getHours() * 60 + now.getMinutes();
  
  const todayHours = hours[currentDay];
  if (!todayHours || todayHours.closed) {
    return { isOpen: false, message: 'Closed today' };
  }
  
  const [openHour, openMin] = todayHours.open.split(':').map(Number);
  const [closeHour, closeMin] = todayHours.close.split(':').map(Number);
  
  const openTime = openHour * 60 + openMin;
  const closeTime = closeHour * 60 + closeMin;
  
  if (currentTime >= openTime && currentTime <= closeTime) {
    const closeTimeStr = `${closeHour > 12 ? closeHour - 12 : closeHour}:${closeMin.toString().padStart(2, '0')} ${closeHour >= 12 ? 'PM' : 'AM'}`;
    return { isOpen: true, message: `Open until ${closeTimeStr}` };
  } else if (currentTime < openTime) {
    const openTimeStr = `${openHour > 12 ? openHour - 12 : openHour}:${openMin.toString().padStart(2, '0')} ${openHour >= 12 ? 'PM' : 'AM'}`;
    return { isOpen: false, message: `Opens at ${openTimeStr}` };
  } else {
    return { isOpen: false, message: 'Closed for today' };
  }
};

export const generateQRCodeFilename = (businessName) => {
  const timestamp = new Date().toISOString().slice(0, 10);
  const safeName = slugify(businessName || 'business');
  return `qr-code-${safeName}-${timestamp}.png`;
};

export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export const BUSINESS_TYPES = {
  food_store: 'Food Store',
  fashion: 'Fashion & Clothing', 
  professional: 'Professional Services',
  beauty: 'Beauty & Wellness',
  technology: 'Technology',
  general: 'General Business'
};

export const COLOR_THEMES = {
  warm: 'Warm',
  fresh: 'Fresh', 
  elegant: 'Elegant',
  modern: 'Modern',
  classic: 'Classic',
  bold: 'Bold',
  corporate: 'Corporate',
  minimal: 'Minimal',
  trust: 'Trust',
  soft: 'Soft',
  luxurious: 'Luxurious',
  tech: 'Tech',
  futuristic: 'Futuristic',
  neutral: 'Neutral',
  business: 'Business',
  friendly: 'Friendly'
};

export const PRODUCT_CATEGORIES = [
  'electronics',
  'clothing',
  'food',
  'books', 
  'home',
  'beauty',
  'sports',
  'automotive',
  'toys',
  'other'
];

export const MESSAGE_TYPES = {
  contact_form: 'Contact Form',
  inquiry: 'Product Inquiry',
  feedback: 'Customer Feedback',
  support: 'Support Request'
};

export const NOTIFICATION_TYPES = {
  NEW_MESSAGE: 'new_message',
  NEW_CUSTOMER: 'new_customer', 
  QR_SCAN: 'qr_scan',
  NEW_FEEDBACK: 'new_feedback',
  LOW_STOCK: 'low_stock'
};

export const CHART_COLORS = {
  primary: '#3b82f6',
  secondary: '#10b981',
  tertiary: '#f59e0b',
  quaternary: '#ef4444',
  quinary: '#8b5cf6'
};

export const DEFAULT_PAGINATION = {
  page: 1,
  per_page: 20
};

export const STOCK_THRESHOLDS = {
  OUT_OF_STOCK: 0,
  LOW_STOCK: 10,
  ADEQUATE_STOCK: 50
};

export const DATE_FORMATS = {
  SHORT: 'MM/dd/yyyy',
  LONG: 'MMMM dd, yyyy',
  WITH_TIME: 'MM/dd/yyyy HH:mm'
};

export const REGEX_PATTERNS = {
  EMAIL: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
  PHONE: /^[\+]?[1-9][\d]{0,15}$/,
  URL: /^https?:\/\/(?:[-\w.])+(?:[:\d]+)?(?:\/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$/
};

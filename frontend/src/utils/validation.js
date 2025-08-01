export const validationRules = {
  email: {
    required: 'Email is required',
    pattern: {
      value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
      message: 'Invalid email address'
    }
  },
  
  password: {
    required: 'Password is required',
    minLength: {
      value: 8,
      message: 'Password must be at least 8 characters'
    },
    pattern: {
      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).*$/,
      message: 'Password must contain at least one uppercase letter, one lowercase letter, and one number'
    }
  },
  
  name: {
    required: 'Name is required',
    minLength: {
      value: 2,
      message: 'Name must be at least 2 characters'
    },
    maxLength: {
      value: 100,
      message: 'Name must be less than 100 characters'
    }
  },
  
  phone: {
    pattern: {
      value: /^[\+]?[1-9][\d]{0,15}$/,
      message: 'Invalid phone number'
    }
  },
  
  url: {
    pattern: {
      value: /^https?:\/\/(?:[-\w.])+(?:[:\d]+)?(?:\/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w*))?)?$/,
      message: 'Invalid URL format'
    }
  },
  
  businessName: {
    required: 'Business name is required',
    minLength: {
      value: 2,
      message: 'Business name must be at least 2 characters'
    },
    maxLength: {
      value: 100,
      message: 'Business name must be less than 100 characters'
    }
  },
  
  productName: {
    required: 'Product name is required',
    minLength: {
      value: 2,
      message: 'Product name must be at least 2 characters'
    },
    maxLength: {
      value: 200,
      message: 'Product name must be less than 200 characters'
    }
  },
  
  productDescription: {
    required: 'Product description is required',
    minLength: {
      value: 10,
      message: 'Description must be at least 10 characters'
    },
    maxLength: {
      value: 2000,
      message: 'Description must be less than 2000 characters'
    }
  },
  
  price: {
    required: 'Price is required',
    min: {
      value: 0,
      message: 'Price must be non-negative'
    },
    max: {
      value: 999999.99,
      message: 'Price must be less than $1,000,000'
    }
  },
  
  stock: {
    required: 'Stock quantity is required',
    min: {
      value: 0,
      message: 'Stock must be non-negative'
    },
    max: {
      value: 999999,
      message: 'Stock must be less than 1,000,000'
    }
  },
  
  message: {
    required: 'Message is required',
    minLength: {
      value: 10,
      message: 'Message must be at least 10 characters'
    },
    maxLength: {
      value: 5000,
      message: 'Message must be less than 5000 characters'
    }
  }
};

export const validateField = (value, rules) => {
  if (rules.required && (!value || value.toString().trim() === '')) {
    return rules.required;
  }
  
  if (value && rules.minLength && value.toString().length < rules.minLength.value) {
    return rules.minLength.message;
  }
  
  if (value && rules.maxLength && value.toString().length > rules.maxLength.value) {
    return rules.maxLength.message;
  }
  
  if (value && rules.min && parseFloat(value) < rules.min.value) {
    return rules.min.message;
  }
  
  if (value && rules.max && parseFloat(value) > rules.max.value) {
    return rules.max.message;
  }
  
  if (value && rules.pattern && !rules.pattern.value.test(value)) {
    return rules.pattern.message;
  }
  
  return null;
};

export const validateForm = (data, schema) => {
  const errors = {};
  
  Object.keys(schema).forEach(field => {
    const value = data[field];
    const rules = schema[field];
    const error = validateField(value, rules);
    
    if (error) {
      errors[field] = { message: error };
    }
  });
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  };
};

// Custom validation functions
export const isStrongPassword = (password) => {
  const minLength = password.length >= 8;
  const hasUpperCase = /[A-Z]/.test(password);
  const hasLowerCase = /[a-z]/.test(password);
  const hasNumbers = /\d/.test(password);
  const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);
  
  return {
    isStrong: minLength && hasUpperCase && hasLowerCase && hasNumbers,
    checks: {
      minLength,
      hasUpperCase,
      hasLowerCase,
      hasNumbers,
      hasSpecialChar
    }
  };
};

export const isValidBusinessHours = (hours) => {
  if (!hours || typeof hours !== 'object') return false;
  
  const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'];
  
  for (const day of days) {
    if (hours[day]) {
      const dayHours = hours[day];
      if (dayHours.closed) continue;
      
      if (!dayHours.open || !dayHours.close) return false;
      
      const timeRegex = /^([01]?\d|2[0-3]):[0-5]\d$/;
      if (!timeRegex.test(dayHours.open) || !timeRegex.test(dayHours.close)) {
        return false;
      }
    }
  }
  
  return true;
};

export const sanitizeInput = (input) => {
  if (typeof input !== 'string') return input;
  
  return input
    .replace(/[<>]/g, '') // Remove potential HTML tags
    .trim();
};

export const validateImageFile = (file) => {
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
  const maxSize = 5 * 1024 * 1024; // 5MB
  
  if (!allowedTypes.includes(file.type)) {
    return 'Invalid file type. Please upload a JPEG, PNG, GIF, or WebP image.';
  }
  
  if (file.size > maxSize) {
    return 'File size too large. Please upload an image smaller than 5MB.';
  }
  
  return null;
};
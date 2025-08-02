import React from 'react';

export const Alert = ({ children, className = '' }) => (
  <div className={`p-4 rounded-md border ${className}`}>
    {children}
  </div>
);

export const AlertDescription = ({ children, className = '' }) => (
  <div className={`text-sm ${className}`}>
    {children}
  </div>
);

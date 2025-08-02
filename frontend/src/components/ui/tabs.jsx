import React, { useState } from 'react';

export const Tabs = ({ defaultValue, children, className = '' }) => {
  const [activeTab, setActiveTab] = useState(defaultValue);
  
  return (
    <div className={className}>
      {React.Children.map(children, child =>
        React.cloneElement(child, { activeTab, setActiveTab })
      )}
    </div>
  );
};

export const TabsList = ({ children, activeTab, setActiveTab, className = '' }) => (
  <div className={`flex space-x-1 rounded-lg bg-gray-100 p-1 ${className}`}>
    {React.Children.map(children, child =>
      React.cloneElement(child, { activeTab, setActiveTab })
    )}
  </div>
);

export const TabsTrigger = ({ value, children, activeTab, setActiveTab, className = '' }) => (
  <button
    onClick={() => setActiveTab(value)}
    className={`flex-1 rounded-md px-3 py-1.5 text-sm font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
      activeTab === value
        ? 'bg-white text-gray-900 shadow-sm'
        : 'text-gray-600 hover:text-gray-900'
    } ${className}`}
  >
    {children}
  </button>
);

export const TabsContent = ({ value, children, activeTab, className = '' }) => {
  if (activeTab !== value) return null;
  
  return (
    <div className={className}>
      {children}
    </div>
  );
};

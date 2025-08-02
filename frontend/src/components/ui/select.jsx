import React, { useState } from 'react';
import { ChevronDown } from 'lucide-react';

export const Select = ({ 
  children, 
  value, 
  onValueChange, 
  className = '' 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
  // Find the selected option label
  const getSelectedLabel = () => {
    let selectedLabel = null;
    React.Children.forEach(children, child => {
      if (child.type === SelectContent) {
        React.Children.forEach(child.props.children, item => {
          if (item?.props?.value === value) {
            selectedLabel = item.props.children;
          }
        });
      }
    });
    return selectedLabel;
  };
  
  return (
    <div className={`relative ${className}`}>
      {React.Children.map(children, child => {
        if (child.type === SelectTrigger) {
          return React.cloneElement(child, { 
            onClick: () => setIsOpen(!isOpen),
            isOpen,
            children: React.Children.map(child.props.children, triggerChild => {
              if (triggerChild?.type === SelectValue) {
                const selectedLabel = getSelectedLabel();
                return (
                  <span className={selectedLabel ? 'text-gray-900' : 'text-gray-500'}>
                    {selectedLabel || triggerChild.props.placeholder}
                  </span>
                );
              }
              return triggerChild;
            })
          });
        }
        if (child.type === SelectContent && isOpen) {
          return React.cloneElement(child, {
            onClose: () => setIsOpen(false),
            onSelect: (itemValue) => {
              onValueChange(itemValue);
              setIsOpen(false);
            }
          });
        }
        return null;
      })}
    </div>
  );
};

export const SelectTrigger = ({ children, onClick, className = '' }) => (
  <button
    type="button"
    onClick={onClick}
    className={`flex items-center justify-between w-full px-3 py-2 text-left bg-white border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${className}`}
  >
    {children}
    <ChevronDown size={16} className="text-gray-400" />
  </button>
);

export const SelectValue = ({ placeholder = 'Select...' }) => {
  // This component will be replaced by the parent Select with the actual value
  return (
    <span className="text-gray-500">{placeholder}</span>
  );
};

export const SelectContent = ({ children, onClose, onSelect, className = '' }) => (
  <>
    <div className="fixed inset-0 z-10" onClick={onClose} />
    <div className={`absolute z-20 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-auto ${className}`}>
      {React.Children.map(children, child =>
        React.cloneElement(child, { onSelect })
      )}
    </div>
  </>
);

export const SelectItem = ({ children, value, onSelect, className = '' }) => (
  <button
    type="button"
    onClick={() => onSelect(value)}
    className={`block w-full px-3 py-2 text-left hover:bg-gray-100 focus:bg-gray-100 focus:outline-none ${className}`}
  >
    {children}
  </button>
);

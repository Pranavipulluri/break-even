import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';

const MetricsCard = ({ 
  title, 
  value, 
  icon: Icon, 
  color = "bg-blue-500", 
  change, 
  changeType = "percentage",
  description,
  onClick 
}) => {
  const formatValue = (val) => {
    if (typeof val === 'number') {
      if (val >= 1000000) {
        return `${(val / 1000000).toFixed(1)}M`;
      } else if (val >= 1000) {
        return `${(val / 1000).toFixed(1)}K`;
      }
      return val.toLocaleString();
    }
    return val;
  };

  const formatChange = (changeVal) => {
    if (changeType === 'currency') {
      return `$${Math.abs(changeVal).toLocaleString()}`;
    }
    return `${Math.abs(changeVal)}%`;
  };

  const getChangeColor = (changeVal) => {
    if (changeVal > 0) return 'text-green-600';
    if (changeVal < 0) return 'text-red-600';
    return 'text-gray-600';
  };

  const getTrendIcon = (changeVal) => {
    if (changeVal > 0) return <TrendingUp size={14} />;
    if (changeVal < 0) return <TrendingDown size={14} />;
    return null;
  };

  return (
    <div 
      className={`card hover:shadow-lg transition-shadow cursor-pointer ${onClick ? 'hover:bg-gray-50' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mb-1">
            {formatValue(value)}
          </p>
          
          {change !== undefined && (
            <div className={`flex items-center space-x-1 text-sm ${getChangeColor(change)}`}>
              {getTrendIcon(change)}
              <span>
                {change > 0 ? '+' : ''}{formatChange(change)} from last period
              </span>
            </div>
          )}
          
          {description && (
            <p className="text-xs text-gray-500 mt-2">{description}</p>
          )}
        </div>
        
        <div className={`p-3 rounded-full ${color} flex-shrink-0`}>
          <Icon size={24} className="text-white" />
        </div>
      </div>
    </div>
  );
};

export default MetricsCard;

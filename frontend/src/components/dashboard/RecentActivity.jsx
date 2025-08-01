import React from 'react';
import { MessageSquare, User, QrCode, Package, Clock } from 'lucide-react';

const RecentActivity = ({ activities = [] }) => {
  const getActivityIcon = (type) => {
    switch (type) {
      case 'message':
        return <MessageSquare size={16} className="text-blue-500" />;
      case 'customer':
        return <User size={16} className="text-green-500" />;
      case 'qr_scan':
        return <QrCode size={16} className="text-orange-500" />;
      case 'product':
        return <Package size={16} className="text-purple-500" />;
      default:
        return <Clock size={16} className="text-gray-500" />;
    }
  };

  const getActivityColor = (type) => {
    switch (type) {
      case 'message':
        return 'border-blue-200 bg-blue-50';
      case 'customer':
        return 'border-green-200 bg-green-50';
      case 'qr_scan':
        return 'border-orange-200 bg-orange-50';
      case 'product':
        return 'border-purple-200 bg-purple-50';
      default:
        return 'border-gray-200 bg-gray-50';
    }
  };

  const formatTimeAgo = (timestamp) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now - time) / (1000 * 60));

    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    
    const diffInHours = Math.floor(diffInMinutes / 60);
    if (diffInHours < 24) return `${diffInHours}h ago`;
    
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    
    return time.toLocaleDateString();
  };

  const defaultActivities = [
    {
      id: 1,
      type: 'message',
      title: 'New customer message',
      description: 'John Doe sent an inquiry about your services',
      timestamp: new Date(Date.now() - 1000 * 60 * 15) // 15 minutes ago
    },
    {
      id: 2,
      type: 'customer',
      title: 'New customer registration',
      description: 'Sarah Smith joined your customer list',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2) // 2 hours ago
    },
    {
      id: 3,
      type: 'qr_scan',
      title: 'QR code scanned',
      description: '3 people scanned your QR code today',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4) // 4 hours ago
    },
    {
      id: 4,
      type: 'product',
      title: 'Product updated',
      description: 'Updated inventory for "Premium Service"',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24) // 1 day ago
    }
  ];

  const displayActivities = activities.length > 0 ? activities : defaultActivities;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View All
        </button>
      </div>
      
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {displayActivities.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <Clock size={48} className="mx-auto mb-4 text-gray-300" />
            <p>No recent activity</p>
          </div>
        ) : (
          displayActivities.map((activity) => (
            <div
              key={activity.id}
              className={`flex items-start space-x-3 p-3 rounded-lg border ${getActivityColor(activity.type)}`}
            >
              <div className="flex-shrink-0 mt-1">
                {getActivityIcon(activity.type)}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {activity.title}
                </p>
                <p className="text-sm text-gray-600 mt-1">
                  {activity.description}
                </p>
                <p className="text-xs text-gray-500 mt-2">
                  {formatTimeAgo(activity.timestamp)}
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default RecentActivity;
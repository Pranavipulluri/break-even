import React from 'react';
import { Reply, Clock, Mail, Phone, MessageSquare } from 'lucide-react';

const MessageCard = ({ message, onReply, onMarkRead, onClick }) => {
  const getMessageTypeIcon = (type) => {
    switch (type) {
      case 'contact_form':
        return <Mail size={16} className="text-blue-500" />;
      case 'inquiry':
        return <MessageSquare size={16} className="text-green-500" />;
      case 'feedback':
        return <MessageSquare size={16} className="text-purple-500" />;
      default:
        return <MessageSquare size={16} className="text-gray-500" />;
    }
  };

  const getStatusBadge = () => {
    if (message.reply) {
      return <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Replied</span>;
    } else if (message.is_read) {
      return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Read</span>;
    } else {
      return <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">New</span>;
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = (now - date) / (1000 * 60 * 60);

    if (diffInHours < 24) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInHours < 24 * 7) {
      return date.toLocaleDateString([], { weekday: 'short', hour: '2-digit', minute: '2-digit' });
    } else {
      return date.toLocaleDateString();
    }
  };

  return (
    <div
      className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
        !message.is_read 
          ? 'border-primary-200 bg-primary-50 hover:bg-primary-100' 
          : 'border-gray-200 bg-white hover:bg-gray-50'
      }`}
      onClick={() => onClick && onClick(message)}
    >
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3 flex-1">
          <div className="flex-shrink-0 mt-1">
            {getMessageTypeIcon(message.message_type)}
          </div>
          
          <div className="flex-1 min-w-0">
            {/* Header */}
            <div className="flex items-center space-x-2 mb-1">
              <h3 className={`font-medium truncate ${!message.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                {message.customer_name}
              </h3>
              <span className="text-gray-500 text-sm truncate">{message.customer_email}</span>
            </div>
            
            {/* Message Preview */}
            <p className={`text-sm mb-2 line-clamp-2 ${!message.is_read ? 'text-gray-800' : 'text-gray-600'}`}>
              {message.content}
            </p>
            
            {/* Metadata */}
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <span className="flex items-center space-x-1">
                <Clock size={12} />
                <span>{formatDate(message.created_at)}</span>
              </span>
              
              {message.customer_phone && (
                <span className="flex items-center space-x-1">
                  <Phone size={12} />
                  <span className="truncate">{message.customer_phone}</span>
                </span>
              )}
              
              <span className="capitalize">{message.message_type}</span>
            </div>
            
            {/* Reply Preview */}
            {message.reply && (
              <div className="mt-3 p-2 bg-blue-50 rounded-lg border-l-2 border-blue-200">
                <p className="text-xs text-blue-800 font-medium">Your Reply:</p>
                <p className="text-sm text-blue-700 line-clamp-1">{message.reply}</p>
              </div>
            )}
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center space-x-2 flex-shrink-0">
          {getStatusBadge()}
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              if (!message.is_read) {
                onMarkRead(message._id);
              }
            }}
            className={`p-2 rounded-lg transition-colors ${
              !message.is_read 
                ? 'text-primary-600 hover:bg-primary-100' 
                : 'text-gray-400'
            }`}
            disabled={message.is_read}
            title={message.is_read ? 'Already read' : 'Mark as read'}
          >
            <MessageSquare size={16} />
          </button>
          
          <button
            onClick={(e) => {
              e.stopPropagation();
              onReply(message);
            }}
            className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
            title="Reply to message"
          >
            <Reply size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default MessageCard;
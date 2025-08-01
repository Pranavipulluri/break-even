import React, { useState, useEffect } from 'react';
import { MessageSquare, Reply, Eye, Clock, User, Mail, Phone } from 'lucide-react';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';
import Modal from '../components/common/Modal';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

const Messages = () => {
  const { messages, dispatch } = useApp();
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [isReplyModalOpen, setIsReplyModalOpen] = useState(false);
  const [filter, setFilter] = useState('all'); // all, unread, replied
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => {
    fetchMessages();
  }, [currentPage, filter]);

  const fetchMessages = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const response = await api.get(`/messages?page=${currentPage}&per_page=10&filter=${filter}`);
      dispatch({ type: 'SET_MESSAGES', payload: response.data.messages });
      setTotalPages(response.data.pages);
    } catch (error) {
      toast.error('Failed to fetch messages');
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const markAsRead = async (messageId) => {
    try {
      await api.put(`/messages/${messageId}/mark-read`);
      
      // Update local state
      dispatch({
        type: 'SET_MESSAGES',
        payload: messages.map(msg => 
          msg._id === messageId 
            ? { ...msg, is_read: true }
            : msg
        )
      });
    } catch (error) {
      toast.error('Failed to mark message as read');
    }
  };

  const handleReply = async (data) => {
    try {
      await api.post(`/messages/${selectedMessage._id}/reply`, {
        reply: data.reply
      });
      
      toast.success('Reply sent successfully');
      setIsReplyModalOpen(false);
      setSelectedMessage(null);
      reset();
      fetchMessages(); // Refresh messages
    } catch (error) {
      toast.error('Failed to send reply');
    }
  };

  const openMessage = (message) => {
    setSelectedMessage(message);
    if (!message.is_read) {
      markAsRead(message._id);
    }
  };

  const openReplyModal = (message) => {
    setSelectedMessage(message);
    setIsReplyModalOpen(true);
  };

  const getMessageTypeIcon = (type) => {
    switch (type) {
      case 'contact_form':
        return <Mail size={16} className="text-blue-500" />;
      case 'inquiry':
        return <MessageSquare size={16} className="text-green-500" />;
      case 'feedback':
        return <Eye size={16} className="text-purple-500" />;
      default:
        return <MessageSquare size={16} className="text-gray-500" />;
    }
  };

  const getStatusBadge = (message) => {
    if (message.reply) {
      return <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">Replied</span>;
    } else if (message.is_read) {
      return <span className="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded-full">Read</span>;
    } else {
      return <span className="px-2 py-1 bg-red-100 text-red-800 text-xs rounded-full">New</span>;
    }
  };

  const filteredMessages = messages.filter(message => {
    switch (filter) {
      case 'unread':
        return !message.is_read;
      case 'replied':
        return message.reply;
      default:
        return true;
    }
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Messages</h1>
          <p className="text-gray-600 mt-2">Customer inquiries and feedback</p>
        </div>
        
        {/* Filter buttons */}
        <div className="flex space-x-2">
          {['all', 'unread', 'replied'].map((filterType) => (
            <button
              key={filterType}
              onClick={() => setFilter(filterType)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                filter === filterType
                  ? 'bg-primary-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {filterType.charAt(0).toUpperCase() + filterType.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Messages List */}
      <div className="card">
        {filteredMessages.length === 0 ? (
          <div className="text-center py-12">
            <MessageSquare size={48} className="mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No messages yet</h3>
            <p className="text-gray-600">Customer messages will appear here when they contact you through your website.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredMessages.map((message) => (
              <div
                key={message._id}
                className={`p-4 border rounded-lg cursor-pointer transition-colors hover:bg-gray-50 ${
                  !message.is_read ? 'border-primary-200 bg-primary-50' : 'border-gray-200'
                }`}
                onClick={() => openMessage(message)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className="flex-shrink-0 mt-1">
                      {getMessageTypeIcon(message.message_type)}
                    </div>
                    
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h3 className={`font-medium ${!message.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                          {message.customer_name}
                        </h3>
                        <span className="text-gray-500 text-sm">{message.customer_email}</span>
                      </div>
                      
                      <p className={`text-sm mb-2 ${!message.is_read ? 'text-gray-800' : 'text-gray-600'}`}>
                        {message.content.length > 150 
                          ? `${message.content.substring(0, 150)}...` 
                          : message.content
                        }
                      </p>
                      
                      <div className="flex items-center space-x-4 text-xs text-gray-500">
                        <span className="flex items-center space-x-1">
                          <Clock size={12} />
                          <span>{new Date(message.created_at).toLocaleDateString()}</span>
                        </span>
                        {message.customer_phone && (
                          <span className="flex items-center space-x-1">
                            <Phone size={12} />
                            <span>{message.customer_phone}</span>
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {getStatusBadge(message)}
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openReplyModal(message);
                      }}
                      className="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                    >
                      <Reply size={16} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex justify-center space-x-2 mt-6">
            <button
              onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
              disabled={currentPage === 1}
              className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Previous
            </button>
            
            <span className="px-3 py-2 text-gray-600">
              Page {currentPage} of {totalPages}
            </span>
            
            <button
              onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
              disabled={currentPage === totalPages}
              className="px-3 py-2 border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
            >
              Next
            </button>
          </div>
        )}
      </div>

      {/* Message Detail Modal */}
      <Modal
        isOpen={!!selectedMessage && !isReplyModalOpen}
        onClose={() => setSelectedMessage(null)}
        title="Message Details"
        size="lg"
      >
        {selectedMessage && (
          <div className="space-y-4">
            <div className="border-b pb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold">{selectedMessage.customer_name}</h3>
                {getStatusBadge(selectedMessage)}
              </div>
              
              <div className="space-y-1 text-sm text-gray-600">
                <div className="flex items-center space-x-2">
                  <Mail size={14} />
                  <span>{selectedMessage.customer_email}</span>
                </div>
                {selectedMessage.customer_phone && (
                  <div className="flex items-center space-x-2">
                    <Phone size={14} />
                    <span>{selectedMessage.customer_phone}</span>
                  </div>
                )}
                <div className="flex items-center space-x-2">
                  <Clock size={14} />
                  <span>{new Date(selectedMessage.created_at).toLocaleString()}</span>
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-medium mb-2">Message:</h4>
              <p className="text-gray-700 whitespace-pre-wrap">{selectedMessage.content}</p>
            </div>
            
            {selectedMessage.reply && (
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium mb-2 text-blue-900">Your Reply:</h4>
                <p className="text-blue-800 whitespace-pre-wrap">{selectedMessage.reply}</p>
                <p className="text-xs text-blue-600 mt-2">
                  Sent on {new Date(selectedMessage.replied_at).toLocaleString()}
                </p>
              </div>
            )}
            
            <div className="flex space-x-3 pt-4">
              <button
                onClick={() => openReplyModal(selectedMessage)}
                className="btn-primary flex items-center space-x-2"
              >
                <Reply size={16} />
                <span>{selectedMessage.reply ? 'Send Another Reply' : 'Reply'}</span>
              </button>
              <button
                onClick={() => setSelectedMessage(null)}
                className="btn-secondary"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </Modal>

      {/* Reply Modal */}
      <Modal
        isOpen={isReplyModalOpen}
        onClose={() => {
          setIsReplyModalOpen(false);
          setSelectedMessage(null);
          reset();
        }}
        title="Reply to Message"
      >
        {selectedMessage && (
          <form onSubmit={handleSubmit(handleReply)} className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <p className="text-sm text-gray-600 mb-2">
                <strong>From:</strong> {selectedMessage.customer_name} ({selectedMessage.customer_email})
              </p>
              <p className="text-sm text-gray-700">
                <strong>Original message:</strong> {selectedMessage.content}
              </p>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Your Reply *
              </label>
              <textarea
                {...register('reply', { required: 'Reply is required' })}
                rows="6"
                className="input-field"
                placeholder="Type your reply here..."
              />
              {errors.reply && (
                <p className="text-red-500 text-sm mt-1">{errors.reply.message}</p>
              )}
            </div>
            
            <div className="flex space-x-3">
              <button type="submit" className="btn-primary flex-1">
                Send Reply
              </button>
              <button
                type="button"
                onClick={() => {
                  setIsReplyModalOpen(false);
                  setSelectedMessage(null);
                  reset();
                }}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
            </div>
          </form>
        )}
      </Modal>
    </div>
  );
};

export default Messages;
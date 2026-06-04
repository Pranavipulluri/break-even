import { Calendar, Clock, Eye, Mail, MessageSquare, Phone, Reply, Send, X } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';

const Messages = () => {
  const { messages, dispatch } = useApp();
  const [selectedMessage, setSelectedMessage] = useState(null);
  const [isReplyModalOpen, setIsReplyModalOpen] = useState(false);
  const [filter, setFilter] = useState('all'); // all, unread, replied
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [activeTab, setActiveTab] = useState('messages'); // messages, consultations
  const [consultations, setConsultations] = useState([]);
  const [showReplyModal, setShowReplyModal] = useState(false);
  const [replyTo, setReplyTo] = useState(null);
  const [replyMessage, setReplyMessage] = useState('');
  const [isReplying, setIsReplying] = useState(false);
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => {
    if (activeTab === 'messages') {
      fetchMessages();
    } else {
      fetchConsultations();
    }
  }, [currentPage, filter, activeTab]);


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

  const fetchConsultations = async () => {
    try {
      const response = await api.get('/bookings/consultations');
      if (response.data.success) {
        const mapped = response.data.bookings.map(booking => ({
          _id: booking._id,
          clientName: `${booking.client_info?.first_name || ''} ${booking.client_info?.last_name || ''}`.trim() || 'Unknown Client',
          email: booking.client_info?.email || '',
          phone: booking.client_info?.phone || '',
          practiceArea: booking.consultation_details?.practice_area || 'General Practice',
          preferredDate: booking.consultation_details?.preferred_date ? `${booking.consultation_details.preferred_date} at ${booking.consultation_details.preferred_time || ''}` : 'Not Specified',
          status: booking.status || 'pending',
          message: booking.consultation_details?.case_description || '',
          createdAt: booking.created_at || new Date().toISOString()
        }));
        setConsultations(mapped);
      }
    } catch (error) {
      console.error('Failed to fetch consultations:', error);
      toast.error('Failed to fetch consultations');
    }
  };

  const confirmConsultation = async (consultationId) => {
    try {
      const response = await api.put(`/bookings/consultations/${consultationId}`, {
        status: 'confirmed'
      });
      if (response.data.success) {
        setConsultations(prev => 
          prev.map(cons => 
            cons._id === consultationId 
              ? { ...cons, status: 'confirmed' }
              : cons
          )
        );
        toast.success('Consultation confirmed successfully!');
      } else {
        throw new Error(response.data.message || 'Failed to update consultation');
      }
    } catch (error) {
      console.error('Failed to confirm consultation:', error);
      toast.error('Failed to confirm consultation');
    }
  };

  const cancelConsultation = async (consultationId, reason = '') => {
    try {
      const response = await api.put(`/bookings/consultations/${consultationId}`, {
        status: 'cancelled',
        notes: reason
      });
      if (response.data.success) {
        setConsultations(prev => 
          prev.map(cons => 
            cons._id === consultationId 
              ? { ...cons, status: 'cancelled', cancellationReason: reason }
              : cons
          )
        );
        toast.success('Consultation cancelled successfully!');
      } else {
        throw new Error(response.data.message || 'Failed to cancel consultation');
      }
    } catch (error) {
      console.error('Failed to cancel consultation:', error);
      toast.error('Failed to cancel consultation');
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

  const closeMessage = () => {
    setSelectedMessage(null);
  };

  const openReplyModal = (message) => {
    setReplyTo(message);
    setShowReplyModal(true);
    setSelectedMessage(null);
  };

  const closeReplyModal = () => {
    setShowReplyModal(false);
    setReplyTo(null);
    setReplyMessage('');
  };

  const sendReply = async () => {
    if (!replyMessage.trim() || !replyTo) return;
    
    setIsReplying(true);
    try {
      const response = await api.post(`/messages/${replyTo._id}/reply`, {
        reply: replyMessage
      });

      if (response.data.success || response.status === 200) {
        toast.success('Reply sent successfully');
        closeReplyModal();
        fetchMessages(); // Refresh messages
      } else {
        toast.error('Failed to send reply');
      }
    } catch (error) {
      console.error('Error sending reply:', error);
      toast.error('Failed to send reply');
    } finally {
      setIsReplying(false);
    }
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
          <h1 className="text-3xl font-bold text-gray-900">Communications</h1>
          <p className="text-gray-600 mt-2">Manage customer messages and consultations</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => setActiveTab('messages')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'messages'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <MessageSquare size={16} />
              <span>Messages</span>
              <span className="bg-red-100 text-red-800 text-xs rounded-full px-2 py-0.5">
                {messages.filter(m => !m.is_read).length}
              </span>
            </div>
          </button>
          <button
            onClick={() => setActiveTab('consultations')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'consultations'
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center space-x-2">
              <Calendar size={16} />
              <span>Consultations</span>
              <span className="bg-blue-100 text-blue-800 text-xs rounded-full px-2 py-0.5">
                {consultations.filter(c => c.status === 'pending').length}
              </span>
            </div>
          </button>
        </nav>
      </div>

      {activeTab === 'messages' ? (
        <>
          {/* Filter buttons for messages */}
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

          {/* Messages List */}
          <MessagesTab 
            messages={messages}
            filter={filter}
            openMessage={openMessage}
            openReplyModal={openReplyModal}
            getMessageTypeIcon={getMessageTypeIcon}
            getStatusBadge={getStatusBadge}
          />
        </>
      ) : (
        <>
          {/* Filter buttons for consultations */}
          <div className="flex space-x-2">
            {['all', 'pending', 'confirmed', 'cancelled'].map((filterType) => (
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

          {/* Consultations List */}
          <ConsultationsTab 
            consultations={consultations}
            filter={filter}
            confirmConsultation={confirmConsultation}
            cancelConsultation={cancelConsultation}
          />
        </>
      )}

      {/* Message Details Modal */}
      {selectedMessage && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full max-h-[80vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{selectedMessage.customer_name}</h3>
                  <p className="text-gray-600">{selectedMessage.customer_email}</p>
                </div>
                <button
                  onClick={closeMessage}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Message Type</label>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                    {selectedMessage.message_type}
                  </span>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
                  <div className="bg-gray-50 p-3 rounded-lg">
                    <p className="text-gray-900">{selectedMessage.content}</p>
                  </div>
                </div>
                
                {selectedMessage.customer_phone && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Phone</label>
                    <p className="text-gray-900">{selectedMessage.customer_phone}</p>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Received</label>
                  <p className="text-gray-900">{new Date(selectedMessage.created_at).toLocaleString()}</p>
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => openReplyModal(selectedMessage)}
                  className="flex-1 bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 transition-colors flex items-center justify-center space-x-2"
                >
                  <Reply size={16} />
                  <span>Reply</span>
                </button>
                <button
                  onClick={closeMessage}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reply Modal */}
      {showReplyModal && replyTo && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-lg w-full">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Reply to {replyTo.customer_name}</h3>
                <button
                  onClick={closeReplyModal}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X size={24} />
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Your Reply</label>
                  <textarea
                    value={replyMessage}
                    onChange={(e) => setReplyMessage(e.target.value)}
                    placeholder="Type your reply here..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows={5}
                  />
                </div>
              </div>
              
              <div className="flex space-x-3 mt-6">
                <button
                  onClick={sendReply}
                  disabled={!replyMessage.trim() || isReplying}
                  className="flex-1 bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center space-x-2"
                >
                  <Send size={16} />
                  <span>{isReplying ? 'Sending...' : 'Send Reply'}</span>
                </button>
                <button
                  onClick={closeReplyModal}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Messages Tab Component
const MessagesTab = ({ messages, filter, openMessage, openReplyModal, getMessageTypeIcon, getStatusBadge }) => {
  const filteredMessages = messages.filter(message => {
    if (filter === 'unread') return !message.is_read;
    if (filter === 'replied') return message.reply_sent;
    return true;
  });

  return (
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
                    className="p-2 text-gray-400 hover:text-primary-500 hover:bg-primary-50 rounded-lg transition-colors"
                  >
                    <Reply size={16} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Consultations Tab Component
const ConsultationsTab = ({ consultations, filter, confirmConsultation, cancelConsultation }) => {
  const filteredConsultations = consultations.filter(consultation => {
    if (filter === 'pending') return consultation.status === 'pending';
    if (filter === 'confirmed') return consultation.status === 'confirmed';
    if (filter === 'cancelled') return consultation.status === 'cancelled';
    return true;
  });

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'confirmed': return 'bg-green-100 text-green-800';
      case 'cancelled': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card">
      {filteredConsultations.length === 0 ? (
        <div className="text-center py-12">
          <Calendar size={48} className="mx-auto text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No consultations yet</h3>
          <p className="text-gray-600">Client consultation requests will appear here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredConsultations.map((consultation) => (
            <div
              key={consultation._id}
              className="p-4 border rounded-lg transition-colors hover:bg-gray-50"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2 mb-2">
                    <h3 className="font-medium text-gray-900">{consultation.clientName}</h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(consultation.status)}`}>
                      {consultation.status.charAt(0).toUpperCase() + consultation.status.slice(1)}
                    </span>
                  </div>
                  
                  <div className="space-y-1 text-sm text-gray-600">
                    <p><span className="font-medium">Practice Area:</span> {consultation.practiceArea}</p>
                    <p><span className="font-medium">Preferred Date:</span> {consultation.preferredDate}</p>
                    <p><span className="font-medium">Email:</span> {consultation.email}</p>
                    {consultation.phone && (
                      <p><span className="font-medium">Phone:</span> {consultation.phone}</p>
                    )}
                  </div>
                  
                  {consultation.message && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-700">
                        <span className="font-medium">Message:</span> {consultation.message}
                      </p>
                    </div>
                  )}
                  
                  <div className="flex items-center space-x-4 text-xs text-gray-500 mt-2">
                    <span className="flex items-center space-x-1">
                      <Clock size={12} />
                      <span>Requested {new Date(consultation.createdAt).toLocaleDateString()}</span>
                    </span>
                  </div>
                </div>
                
                {consultation.status === 'pending' && (
                  <div className="flex space-x-2 ml-4">
                    <button
                      onClick={() => confirmConsultation(consultation._id)}
                      className="px-3 py-1 bg-green-500 text-white text-sm rounded-lg hover:bg-green-600 transition-colors"
                    >
                      Confirm
                    </button>
                    <button
                      onClick={() => cancelConsultation(consultation._id)}
                      className="px-3 py-1 bg-red-500 text-white text-sm rounded-lg hover:bg-red-600 transition-colors"
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Messages;
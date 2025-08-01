import React, { useState, useEffect } from 'react';
import { User, Bell, Shield, Globe, CreditCard, Mail } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';

const Settings = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [customers, setCustomers] = useState([]);
  
  const { register, handleSubmit, reset, formState: { errors } } = useForm();

  useEffect(() => {
    if (user) {
      reset(user);
    }
    fetchCustomers();
  }, [user, reset]);

  const fetchCustomers = async () => {
    try {
      const response = await api.get('/customers');
      setCustomers(response.data.customers);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    }
  };

  const updateProfile = async (data) => {
    try {
      setLoading(true);
      await api.put('/auth/profile', data);
      toast.success('Profile updated successfully');
    } catch (error) {
      toast.error('Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const sendBulkEmail = async (data) => {
    try {
      setLoading(true);
      await api.post('/customers/send-bulk-email', {
        subject: data.subject,
        content: data.content,
        target_customers: data.target_customers
      });
      toast.success('Bulk email sent successfully');
    } catch (error) {
      toast.error('Failed to send bulk email');
    } finally {
      setLoading(false);
    }
  };

  const ProfileSettings = () => (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h3>
        
        <form onSubmit={handleSubmit(updateProfile)} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input
                {...register('name', { required: 'Name is required' })}
                className="input-field"
                placeholder="Your full name"
              />
              {errors.name && (
                <p className="text-red-500 text-sm mt-1">{errors.name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address *
              </label>
              <input
                {...register('email', { 
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: "Invalid email address"
                  }
                })}
                className="input-field"
                placeholder="your@email.com"
              />
              {errors.email && (
                <p className="text-red-500 text-sm mt-1">{errors.email.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Business Name
              </label>
              <input
                {...register('business_name')}
                className="input-field"
                placeholder="Your business name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                {...register('phone')}
                className="input-field"
                placeholder="(555) 123-4567"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button
              type="submit"
              disabled={loading}
              className="btn-primary"
            >
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
          </div>
        </form>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
        
        <form className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Password
            </label>
            <input
              type="password"
              className="input-field"
              placeholder="Enter current password"
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                New Password
              </label>
              <input
                type="password"
                className="input-field"
                placeholder="Enter new password"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirm New Password
              </label>
              <input
                type="password"
                className="input-field"
                placeholder="Confirm new password"
              />
            </div>
          </div>

          <div className="flex justify-end">
            <button type="submit" className="btn-primary">
              Change Password
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const NotificationSettings = () => (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
      
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900">Email Notifications</h4>
            <p className="text-sm text-gray-600">Receive email notifications for new messages</p>
          </div>
          <input type="checkbox" className="h-4 w-4 text-primary-600" defaultChecked />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900">Customer Messages</h4>
            <p className="text-sm text-gray-600">Get notified when customers send messages</p>
          </div>
          <input type="checkbox" className="h-4 w-4 text-primary-600" defaultChecked />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900">QR Code Scans</h4>
            <p className="text-sm text-gray-600">Daily summary of QR code scans</p>
          </div>
          <input type="checkbox" className="h-4 w-4 text-primary-600" />
        </div>

        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-medium text-gray-900">Marketing Tips</h4>
            <p className="text-sm text-gray-600">Weekly tips to grow your business</p>
          </div>
          <input type="checkbox" className="h-4 w-4 text-primary-600" />
        </div>

        <div className="flex justify-end pt-4">
          <button className="btn-primary">Save Preferences</button>
        </div>
      </div>
    </div>
  );

  const EmailCampaigns = () => {
    const { register: registerEmail, handleSubmit: handleEmailSubmit, reset: resetEmail } = useForm();

    const onEmailSubmit = (data) => {
      sendBulkEmail(data);
      resetEmail();
    };

    return (
      <div className="space-y-6">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Send Email Campaign</h3>
          
          <form onSubmit={handleEmailSubmit(onEmailSubmit)} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Subject *
              </label>
              <input
                {...registerEmail('subject', { required: 'Subject is required' })}
                className="input-field"
                placeholder="Email subject line"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Message Content *
              </label>
              <textarea
                {...registerEmail('content', { required: 'Content is required' })}
                rows="6"
                className="input-field"
                placeholder="Write your email message here..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Recipients
              </label>
              <select
                {...registerEmail('target_customers')}
                className="input-field"
              >
                <option value="">All Customers ({customers.length})</option>
                <option value="subscribed">Subscribed Only</option>
                <option value="recent">Recent Customers</option>
              </select>
            </div>

            <div className="flex justify-end">
              <button
                type="submit"
                disabled={loading}
                className="btn-primary"
              >
                {loading ? 'Sending...' : 'Send Campaign'}
              </button>
            </div>
          </form>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Templates</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Welcome Email</h4>
              <p className="text-sm text-gray-600 mb-3">
                Welcome new customers to your business
              </p>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                Use Template
              </button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Product Announcement</h4>
              <p className="text-sm text-gray-600 mb-3">
                Announce new products or services
              </p>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                Use Template
              </button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Special Offer</h4>
              <p className="text-sm text-gray-600 mb-3">
                Promote discounts and special deals
              </p>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                Use Template
              </button>
            </div>

            <div className="p-4 border border-gray-200 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">Newsletter</h4>
              <p className="text-sm text-gray-600 mb-3">
                Regular updates and business news
              </p>
              <button className="text-primary-600 hover:text-primary-700 text-sm font-medium">
                Use Template
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const SecuritySettings = () => (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Account Security</h3>
        
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <div>
                <h4 className="font-medium text-green-900">Account Status</h4>
                <p className="text-sm text-green-700">Your account is active and secure</p>
              </div>
            </div>
          </div>

          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-3">Login Activity</h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Last login</span>
                <span className="text-gray-900">Today at 2:30 PM</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Login location</span>
                <span className="text-gray-900">Your current location</span>
              </div>
            </div>
          </div>

          <div className="border-t pt-4">
            <h4 className="font-medium text-gray-900 mb-3">Two-Factor Authentication</h4>
            <p className="text-sm text-gray-600 mb-3">
              Add an extra layer of security to your account
            </p>
            <button className="btn-secondary">Enable 2FA</button>
          </div>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 text-red-600">Danger Zone</h3>
        
        <div className="space-y-4">
          <div className="border border-red-200 rounded-lg p-4">
            <h4 className="font-medium text-red-900 mb-2">Delete Account</h4>
            <p className="text-sm text-red-700 mb-3">
              Permanently delete your account and all associated data. This action cannot be undone.
            </p>
            <button className="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
              Delete Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account and business preferences</p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'profile', name: 'Profile', icon: User },
            { id: 'notifications', name: 'Notifications', icon: Bell },
            { id: 'email', name: 'Email Campaigns', icon: Mail },
            { id: 'security', name: 'Security', icon: Shield },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2 ${
                activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <tab.icon size={16} />
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && <ProfileSettings />}
      {activeTab === 'notifications' && <NotificationSettings />}
      {activeTab === 'email' && <EmailCampaigns />}
      {activeTab === 'security' && <SecuritySettings />}
    </div>
  );
};

export default Settings;
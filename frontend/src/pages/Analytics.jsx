import React, { useState, useEffect } from 'react';
import { BarChart3, TrendingUp, Users, MessageSquare, Eye, Heart, Filter, Download, Calendar, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area } from 'recharts';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [customerData, setCustomerData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState('30d');

  const tabs = [
    { 
      id: 'overview', 
      name: 'Overview', 
      icon: BarChart3,
      gradient: 'from-blue-500 to-indigo-600'
    },
    { 
      id: 'sentiment', 
      name: 'Customer Sentiment', 
      icon: Heart,
      gradient: 'from-pink-500 to-rose-600'
    },
    { 
      id: 'customers', 
      name: 'Customer Insights', 
      icon: Users,
      gradient: 'from-green-500 to-emerald-600'
    },
  ];

  const dateRanges = [
    { value: '7d', label: '7 Days' },
    { value: '30d', label: '30 Days' },
    { value: '90d', label: '90 Days' },
    { value: '1y', label: '1 Year' },
  ];

  useEffect(() => {
    fetchAnalyticsData();
  }, [dateRange]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      const [overviewRes, sentimentRes, customerRes] = await Promise.all([
        api.get(`/analytics/overview?range=${dateRange}`),
        api.get('/analytics/sentiment'),
        api.get('/analytics/customers')
      ]);
      
      setAnalyticsData(overviewRes.data);
      setSentimentData(sentimentRes.data);
      setCustomerData(customerRes.data);
    } catch (error) {
      toast.error('Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  const MetricCard = ({ title, value, icon: Icon, color, gradient, change, description }) => (
    <div className={`card-hover bg-gradient-to-br ${gradient} text-white relative overflow-hidden`}>
      <div className="absolute inset-0 bg-hero-pattern opacity-10"></div>
      <div className={`absolute -top-4 -right-4 w-24 h-24 ${color} rounded-full opacity-20`}></div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
            <Icon size={24} />
          </div>
          {change !== undefined && (
            <div className="flex items-center space-x-1 px-2 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium">
              <TrendingUp size={12} />
              <span>{change}%</span>
            </div>
          )}
        </div>
        
        <div>
          <p className="text-white/80 text-sm font-medium mb-1">{title}</p>
          <p className="text-2xl font-bold mb-1">{value}</p>
          {description && (
            <p className="text-white/70 text-xs">{description}</p>
          )}
        </div>
      </div>
    </div>
  );

  const ChartCard = ({ title, children, actions }) => (
    <div className="card-hover">
      <div className="flex items-center justify-between mb-6">
        <h3 className="heading-3 text-gray-900">{title}</h3>
        {actions && (
          <div className="flex space-x-2">
            {actions}
          </div>
        )}
      </div>
      {children}
    </div>
  );

  const SentimentIndicator = ({ sentiment, score }) => {
    const getConfig = () => {
      if (sentiment === 'positive') return { 
        color: 'text-green-600 bg-green-100 border-green-200',
        emoji: '😊'
      };
      if (sentiment === 'negative') return { 
        color: 'text-red-600 bg-red-100 border-red-200',
        emoji: '😞'
      };
      return { 
        color: 'text-gray-600 bg-gray-100 border-gray-200',
        emoji: '😐'
      };
    };

    const config = getConfig();

    return (
      <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full border text-xs font-medium ${config.color}`}>
        <span>{config.emoji}</span>
        <span>{sentiment}</span>
        <span>({(score * 100).toFixed(0)}%)</span>
      </span>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex justify-between items-center">
          <div>
            <div className="h-8 w-48 skeleton mb-2"></div>
            <div className="h-4 w-64 skeleton"></div>
          </div>
          <div className="h-10 w-32 skeleton rounded-xl"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 skeleton rounded-2xl"></div>
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card">
              <div className="h-32 skeleton rounded-xl"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="heading-1">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Deep insights into your business performance and customer behavior</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="input-field w-32"
          >
            {dateRanges.map(range => (
              <option key={range.value} value={range.value}>{range.label}</option>
            ))}
          </select>
          
          <button 
            onClick={fetchAnalyticsData}
            className="btn-secondary"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          
          <button className="btn-primary">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`card-hover text-left p-6 transition-all duration-300 relative overflow-hidden ${
              activeTab === tab.id 
                ? `bg-gradient-to-br ${tab.gradient} text-white shadow-colored` 
                : ''
            }`}
          >
            <div className="relative z-10 flex items-center space-x-4">
              <tab.icon size={24} className={activeTab === tab.id ? 'text-white' : 'text-gray-600'} />
              <div>
                <h3 className={`font-semibold ${activeTab === tab.id ? 'text-white' : 'text-gray-900'}`}>
                  {tab.name}
                </h3>
              </div>
            </div>
            
            {activeTab === tab.id && (
              <div className="absolute top-2 right-2">
                <div className="w-3 h-3 bg-white/30 rounded-full animate-pulse"></div>
              </div>
            )}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && analyticsData && (
        <div className="space-y-8">
          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Visitors"
              value="12.5K"
              icon={Eye}
              color="bg-blue-500"
              gradient="from-blue-500 to-indigo-600"
              change={15.3}
              description="Unique website visitors"
            />
            <MetricCard
              title="Customer Messages"
              value="234"
              icon={MessageSquare}
              color="bg-green-500"
              gradient="from-green-500 to-emerald-600"
              change={8.2}
              description="Messages received"
            />
            <MetricCard
              title="New Customers"
              value="89"
              icon={Users}
              color="bg-purple-500"
              gradient="from-purple-500 to-pink-600"
              change={-2.1}
              description="New registrations"
            />
            <MetricCard
              title="Engagement Rate"
              value="73%"
              icon={TrendingUp}
              color="bg-orange-500"
              gradient="from-orange-500 to-red-600"
              change={5.8}
              description="Customer interaction rate"
            />
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ChartCard title="Visitor Trends">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={[
                  { name: 'Mon', visitors: 1200, engagement: 68 },
                  { name: 'Tue', visitors: 1100, engagement: 72 },
                  { name: 'Wed', visitors: 1300, engagement: 65 },
                  { name: 'Thu', visitors: 1400, engagement: 78 },
                  { name: 'Fri', visitors: 1600, engagement: 82 },
                  { name: 'Sat', visitors: 1350, engagement: 75 },
                  { name: 'Sun', visitors: 1100, engagement: 70 },
                ]}>
                  <defs>
                    <linearGradient id="visitorsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="visitors" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    fill="url(#visitorsGradient)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Traffic Sources">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'QR Codes', value: 45, color: '#3b82f6' },
                      { name: 'Direct', value: 30, color: '#10b981' },
                      { name: 'Social Media', value: 15, color: '#f59e0b' },
                      { name: 'Search', value: 10, color: '#ef4444' },
                    ]}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {[
                      { name: 'QR Codes', value: 45, color: '#3b82f6' },
                      { name: 'Direct', value: 30, color: '#10b981' },
                      { name: 'Social Media', value: 15, color: '#f59e0b' },
                      { name: 'Search', value: 10, color: '#ef4444' },
                    ].map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              
              <div className="mt-6 grid grid-cols-2 gap-4">
                {[
                  { name: 'QR Codes', value: 45, color: '#3b82f6' },
                  { name: 'Direct', value: 30, color: '#10b981' },
                  { name: 'Social Media', value: 15, color: '#f59e0b' },
                  { name: 'Search', value: 10, color: '#ef4444' },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }}></div>
                      <span className="text-sm text-gray-600">{item.name}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </ChartCard>
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Eye className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Page Views</h3>
              <p className="text-3xl font-bold text-blue-600 mb-1">25.4K</p>
              <p className="text-sm text-gray-600">+12% vs last period</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Users className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Conversion Rate</h3>
              <p className="text-3xl font-bold text-green-600 mb-1">4.2%</p>
              <p className="text-sm text-gray-600">+0.8% vs last period</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <MessageSquare className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Avg. Session</h3>
              <p className="text-3xl font-bold text-purple-600 mb-1">3m 24s</p>
              <p className="text-sm text-gray-600">+15s vs last period</p>
            </div>
          </div>
        </div>
      )}

      {/* Sentiment Analysis Tab */}
      {activeTab === 'sentiment' && sentimentData && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Sentiment Overview */}
            <div className="card bg-gradient-to-br from-pink-50 to-rose-50 border-pink-200">
              <h3 className="heading-3 text-pink-900 mb-6">Overall Sentiment</h3>
              <div class="text-center">
                <div className="text-6xl mb-4">😊</div>
                <div className="text-2xl font-bold text-pink-700 mb-2">Positive</div>
                <div className="text-pink-600">Based on 156 interactions</div>
              </div>
              
              <div className="mt-6 space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-pink-700">Positive</span>
                  <span className="text-sm font-semibold text-pink-700">68%</span>
                </div>
                <div className="w-full bg-pink-200 rounded-full h-2">
                  <div className="bg-gradient-to-r from-pink-500 to-rose-500 h-2 rounded-full" style={{ width: '68%' }}></div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Neutral</span>
                  <span className="text-sm font-semibold text-gray-600">22%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-gray-400 h-2 rounded-full" style={{ width: '22%' }}></div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-red-600">Negative</span>
                  <span className="text-sm font-semibold text-red-600">10%</span>
                </div>
                <div className="w-full bg-red-200 rounded-full h-2">
                  <div className="bg-red-500 h-2 rounded-full" style={{ width: '10%' }}></div>
                </div>
              </div>
            </div>

            {/* Recent Feedback */}
            <div className="lg:col-span-2">
              <ChartCard title="Recent Customer Feedback">
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {[
                    { customer: 'Sarah Johnson', message: 'Amazing service! The team was very helpful and responsive.', sentiment: 'positive', score: 0.9, time: '2h ago' },
                    { customer: 'Mike Chen', message: 'Good experience overall, delivery was on time.', sentiment: 'positive', score: 0.7, time: '4h ago' },
                    { customer: 'Emma Davis', message: 'The product quality could be better for the price.', sentiment: 'neutral', score: 0.1, time: '6h ago' },
                    { customer: 'John Smith', message: 'Excellent customer support, resolved my issue quickly!', sentiment: 'positive', score: 0.95, time: '8h ago' },
                  ].map((feedback, index) => (
                    <div key={index} className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                            {feedback.customer.split(' ').map(n => n[0]).join('')}
                          </div>
                          <div>
                            <span className="font-medium text-gray-900">{feedback.customer}</span>
                            <div className="flex items-center space-x-2 mt-1">
                              <SentimentIndicator sentiment={feedback.sentiment} score={feedback.score} />
                              <span className="text-xs text-gray-500">{feedback.time}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <p className="text-gray-700 text-sm ml-13">{feedback.message}</p>
                    </div>
                  ))}
                </div>
              </ChartCard>
            </div>
          </div>
        </div>
      )}

      {/* Customer Insights Tab */}
      {activeTab === 'customers' && customerData && (
        <div className="space-y-8">
          {/* Customer Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="Total Customers"
              value="1,234"
              icon={Users}
              color="bg-blue-500"
              gradient="from-blue-500 to-indigo-600"
              change={12.5}
              description="Active customers"
            />
            <MetricCard
              title="Customer Lifetime Value"
              value="$312"
              icon={TrendingUp}
              color="bg-green-500" 
              gradient="from-green-500 to-emerald-600"
              change={8.3}
              description="Average per customer"
            />
            <MetricCard
              title="Retention Rate"
              value="84%"
              icon={Heart}
              color="bg-purple-500"
              gradient="from-purple-500 to-pink-600"
              change={5.2}
              description="Customer retention"
            />
          </div>

          {/* Customer Growth & Engagement */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <ChartCard title="Customer Growth">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={[
                  { month: 'Jan', customers: 120 },
                  { month: 'Feb', customers: 150 },
                  { month: 'Mar', customers: 180 },
                  { month: 'Apr', customers: 220 },
                  { month: 'May', customers: 280 },
                  { month: 'Jun', customers: 350 },
                ]}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="customers" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            <ChartCard title="Top Engaged Customers">
              <div className="space-y-4">
                {[
                  { name: 'Sarah Johnson', email: 'sarah@email.com', interactions: 24, value: '$450' },
                  { name: 'Mike Chen', email: 'mike@email.com', interactions: 18, value: '$320' },
                  { name: 'Emma Davis', email: 'emma@email.com', interactions: 15, value: '$280' },
                  { name: 'John Smith', email: 'john@email.com', interactions: 12, value: '$190' },
                ].map((customer, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{customer.name}</p>
                        <p className="text-sm text-gray-600">{customer.email}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{customer.value}</p>
                      <p className="text-sm text-gray-600">{customer.interactions} interactions</p>
                    </div>
                  </div>
                ))}
              </div>
            </ChartCard>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
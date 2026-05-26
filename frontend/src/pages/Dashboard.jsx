
import React, { useEffect, useState } from 'react';
import { TrendingUp, Users, ShoppingCart, DollarSign, Eye, MessageSquare, QrCode, Zap, ArrowUp, ArrowDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';
import { useApp } from '../context/AppContext';
import { api } from '../services/api';

const Dashboard = () => {
  const { analytics, dispatch } = useApp();
  const [stats, setStats] = useState({
    totalSales: 0,
    totalCustomers: 0,
    totalProducts: 0,
    totalMessages: 0,
    totalScans: 0,
    monthlyRevenue: 0
  });
  const [recentActivity, setRecentActivity] = useState({ messages: [], customers: [] });
  const [chartData, setChartData] = useState([]);
  const [timeframe, setTimeframe] = useState('7d');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, [timeframe]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get(`/dashboard?timeframe=${timeframe}`);
      const data = response.data;

      setStats(data.stats || {
        totalSales: 0,
        totalCustomers: 0,
        totalProducts: 0,
        totalMessages: 0,
        totalScans: 0,
        monthlyRevenue: 0
      });

      // Use real analytics data for charts
      if (data.analytics && data.analytics.length > 0) {
        setChartData(data.analytics);
      } else {
        setChartData([]);
      }

      // Use real recent activity
      setRecentActivity(data.recentActivity || { messages: [], customers: [] });

      dispatch({ type: 'SET_ANALYTICS', payload: data.analytics });
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Build activity feed from real data
  const buildActivityFeed = () => {
    const feed = [];

    if (recentActivity.messages) {
      recentActivity.messages.forEach(msg => {
        feed.push({
          type: 'message',
          message: `New message from ${msg.customer_name}: ${msg.content}`,
          time: msg.created_at ? new Date(msg.created_at).toLocaleString() : 'Recently',
          icon: MessageSquare,
          color: 'text-blue-500 bg-blue-100'
        });
      });
    }

    if (recentActivity.customers) {
      recentActivity.customers.forEach(cust => {
        feed.push({
          type: 'customer',
          message: `${cust.name} registered as a new customer`,
          time: cust.created_at ? new Date(cust.created_at).toLocaleString() : 'Recently',
          icon: Users,
          color: 'text-green-500 bg-green-100'
        });
      });
    }

    // Sort by time descending and limit
    feed.sort((a, b) => new Date(b.time) - new Date(a.time));

    if (feed.length === 0) {
      feed.push({
        type: 'info',
        message: 'No recent activity yet. Customer interactions will appear here.',
        time: 'Just now',
        icon: Eye,
        color: 'text-gray-400 bg-gray-100'
      });
    }

    return feed.slice(0, 5);
  };

  // Compute quick stats from real data
  const computeQuickStats = () => {
    const totalOrders = stats.totalSales || 0;
    const revenue = stats.monthlyRevenue || 0;
    const avgOrderValue = totalOrders > 0 ? (revenue / totalOrders).toFixed(2) : '0.00';
    const totalCustomers = stats.totalCustomers || 0;
    const totalMessages = stats.totalMessages || 0;
    const responseRate = totalMessages > 0 ? Math.min(100, Math.round((totalMessages / Math.max(1, totalCustomers)) * 100)) : 0;

    return [
      { label: 'Avg. Order Value', value: `$${avgOrderValue}`, change: totalOrders > 0 ? '+active' : 'N/A', positive: true },
      { label: 'Total Products', value: `${stats.totalProducts || 0}`, change: stats.totalProducts > 0 ? 'In stock' : 'None', positive: stats.totalProducts > 0 },
      { label: 'Customer Messages', value: `${totalMessages}`, change: totalMessages > 0 ? 'Active' : 'No messages', positive: totalMessages > 0 },
      { label: 'Response Rate', value: `${responseRate}%`, change: responseRate > 50 ? 'Good' : 'Needs attention', positive: responseRate > 50 },
    ];
  };

  // Build pie data from real sources
  const buildChannelData = () => {
    const scans = stats.totalScans || 0;
    const customers = stats.totalCustomers || 0;
    const messages = stats.totalMessages || 0;
    const total = scans + customers + messages;

    if (total === 0) {
      return [
        { name: 'QR Scans', value: 0, color: '#3b82f6' },
        { name: 'Customers', value: 0, color: '#10b981' },
        { name: 'Messages', value: 0, color: '#f59e0b' },
      ];
    }

    return [
      { name: 'QR Scans', value: Math.round((scans / total) * 100) || 0, color: '#3b82f6' },
      { name: 'Customers', value: Math.round((customers / total) * 100) || 0, color: '#10b981' },
      { name: 'Messages', value: Math.round((messages / total) * 100) || 0, color: '#f59e0b' },
    ];
  };

  const MetricCard = ({ title, value, icon: Icon, color, gradient, change, changeType, description, onClick }) => (
    <div 
      className={`card-hover cursor-pointer group bg-gradient-to-br ${gradient} text-white relative overflow-hidden`}
      onClick={onClick}
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 bg-hero-pattern opacity-10"></div>
      
      {/* Glowing orb */}
      <div className={`absolute -top-4 -right-4 w-24 h-24 ${color} rounded-full opacity-20 group-hover:opacity-30 transition-opacity duration-300`}></div>
      
      <div className="relative z-10">
        <div className="flex items-center justify-between mb-4">
          <div className={`p-3 bg-white/20 backdrop-blur-sm rounded-xl`}>
            <Icon size={24} className="text-white" />
          </div>
          {change !== undefined && (
            <div className={`flex items-center space-x-1 px-2 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium`}>
              {change > 0 ? (
                <ArrowUp size={12} />
              ) : (
                <ArrowDown size={12} />
              )}
              <span>{Math.abs(change)}%</span>
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

  if (loading) {
    return (
      <div className="space-y-6 animate-fade-in">
        {/* Loading Skeleton */}
        <div className="flex justify-between items-center">
          <div>
            <div className="h-8 w-48 skeleton mb-2"></div>
            <div className="h-4 w-64 skeleton"></div>
          </div>
          <div className="h-10 w-32 skeleton rounded-xl"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card">
              <div className="h-16 skeleton rounded-xl mb-4"></div>
              <div className="h-4 skeleton mb-2"></div>
              <div className="h-6 skeleton w-20"></div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="card">
              <div className="h-64 skeleton rounded-xl"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  const activityFeed = buildActivityFeed();
  const quickStats = computeQuickStats();
  const channelData = buildChannelData();

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="heading-1">Good morning! 👋</h1>
          <p className="text-gray-600 mt-2">Here's what's happening with your business today.</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <div className="flex bg-white rounded-xl p-1 shadow-sm border border-gray-200">
            {['7d', '30d', '90d'].map((period) => (
              <button
                key={period}
                onClick={() => setTimeframe(period)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 ${
                  timeframe === period
                    ? 'bg-primary-500 text-white shadow-md'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                {period === '7d' ? '7 Days' : period === '30d' ? '30 Days' : '90 Days'}
              </button>
            ))}
          </div>
          
          <button className="btn-primary">
            <Zap size={16} />
            AI Insights
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Total Revenue"
          value={`$${(stats.monthlyRevenue || 0).toLocaleString()}`}
          icon={DollarSign}
          color="bg-green-500"
          gradient="from-green-500 to-emerald-600"
          description="From all sales channels"
        />
        <MetricCard
          title="Customers"
          value={stats.totalCustomers || 0}
          icon={Users}
          color="bg-blue-500"
          gradient="from-blue-500 to-indigo-600"
          description="Registered customers"
        />
        <MetricCard
          title="Total Products"
          value={stats.totalProducts || 0}
          icon={ShoppingCart}
          color="bg-purple-500"
          gradient="from-purple-500 to-pink-600"
          description="Active products"
        />
        <MetricCard
          title="QR Scans"
          value={(stats.totalScans || 0).toLocaleString()}
          icon={QrCode}
          color="bg-orange-500"
          gradient="from-orange-500 to-red-600"
          description="Physical to digital"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Sales Chart */}
        <div className="lg:col-span-2">
          <ChartCard 
            title="Sales Overview" 
            actions={
              <>
                <button className="text-sm text-gray-500 hover:text-gray-700 font-medium">Sales</button>
                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">Revenue</button>
              </>
            }
          >
            {chartData.length > 0 ? (
              <ResponsiveContainer width="100%" height={320}>
                <AreaChart data={chartData}>
                  <defs>
                    <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis 
                    dataKey="month" 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6b7280' }}
                  />
                  <YAxis 
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#6b7280' }}
                  />
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.1)',
                      fontSize: '14px'
                    }}
                  />
                  <Area 
                    type="monotone" 
                    dataKey="sales" 
                    stroke="#3b82f6" 
                    strokeWidth={3}
                    fill="url(#salesGradient)"
                    name="Sales"
                  />
                  <Area 
                    type="monotone" 
                    dataKey="revenue" 
                    stroke="#10b981" 
                    strokeWidth={3}
                    fill="url(#revenueGradient)"
                    name="Revenue ($)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-80 text-gray-400">
                <div className="text-center">
                  <BarChart3 size={48} className="mx-auto mb-3 text-gray-300" />
                  <p className="text-sm">No sales data available yet.</p>
                  <p className="text-xs text-gray-400 mt-1">Data will populate as orders come in.</p>
                </div>
              </div>
            )}
          </ChartCard>
        </div>

        {/* Engagement Channels Pie Chart */}
        <ChartCard title="Engagement Channels">
          {(channelData.reduce((sum, d) => sum + d.value, 0)) > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={320}>
                <PieChart>
                  <Pie
                    data={channelData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {channelData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{
                      backgroundColor: 'white',
                      border: 'none',
                      borderRadius: '12px',
                      boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              
              <div className="mt-4 space-y-2">
                {channelData.map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full`} style={{ backgroundColor: item.color }}></div>
                      <span className="text-sm text-gray-600">{item.name}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div className="flex items-center justify-center h-80 text-gray-400">
              <div className="text-center">
                <Eye size={48} className="mx-auto mb-3 text-gray-300" />
                <p className="text-sm">No engagement data yet.</p>
              </div>
            </div>
          )}
        </ChartCard>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <ChartCard title="Recent Activity">
          <div className="space-y-4">
            {activityFeed.map((activity, index) => (
              <div key={index} className="flex items-start space-x-4 p-4 hover:bg-gray-50 rounded-xl transition-colors cursor-pointer group">
                <div className={`p-2 rounded-xl ${activity.color} group-hover:scale-110 transition-transform`}>
                  <activity.icon size={16} />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 mb-1">{activity.message}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </ChartCard>

        {/* Quick Stats */}
        <ChartCard title="Quick Stats">
          <div className="grid grid-cols-2 gap-4">
            {quickStats.map((stat, index) => (
              <div key={index} className="p-4 bg-gradient-to-br from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">{stat.label}</span>
                  <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                    stat.positive ? 'text-green-700 bg-green-100' : 'text-red-700 bg-red-100'
                  }`}>
                    {stat.change}
                  </span>
                </div>
                <p className="text-xl font-bold text-gray-900">{stat.value}</p>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>
    </div>
  );
};

// Import BarChart3 for the empty state
import { BarChart3 } from 'lucide-react';

export default Dashboard;

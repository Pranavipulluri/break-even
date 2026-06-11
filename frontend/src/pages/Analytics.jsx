import React, { useState } from 'react';
import {
  BarChart3, TrendingUp, Users, MessageSquare, Eye, Heart,
  Download, RefreshCw, MousePointer, ArrowDownRight, Clock,
} from 'lucide-react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell,
  BarChart, Bar, AreaChart, Area,
} from 'recharts';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { useApp } from '../context/AppContext';
import toast from 'react-hot-toast';
import { useAnalyticsRange, formatSecondsAgo } from '../hooks/useAnalytics';

// ─────────────────────────────────────────────────────────────────────────────
// Constants
// ─────────────────────────────────────────────────────────────────────────────

const DATE_RANGES = [
  { value: '7d',  label: '7 Days'  },
  { value: '30d', label: '30 Days' },
  { value: '90d', label: '90 Days' },
  { value: '1y',  label: '1 Year'  },
];

const TABS = [
  { id: 'overview',   name: 'Overview',             icon: BarChart3,     gradient: 'from-blue-500 to-indigo-600'  },
  { id: 'products',   name: 'Services & Inquiries', icon: MessageSquare, gradient: 'from-purple-500 to-pink-600' },
  { id: 'sentiment',  name: 'Customer Sentiment',   icon: Heart,         gradient: 'from-pink-500 to-rose-600'    },
  { id: 'customers',  name: 'Customer Insights',    icon: Users,         gradient: 'from-green-500 to-emerald-600' },
];

// ─────────────────────────────────────────────────────────────────────────────
// Sub-components
// ─────────────────────────────────────────────────────────────────────────────

const MetricCard = ({ title, value, icon: Icon, color, gradient, change, description }) => (
  <div className={`card-hover bg-gradient-to-br ${gradient} text-white relative overflow-hidden`}>
    <div className="absolute inset-0 bg-hero-pattern opacity-10" />
    <div className={`absolute -top-4 -right-4 w-24 h-24 ${color} rounded-full opacity-20`} />
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
        <p className="text-2xl font-bold mb-1 tabular-nums">{value}</p>
        {description && <p className="text-white/70 text-xs">{description}</p>}
      </div>
    </div>
  </div>
);

const ChartCard = ({ title, children, actions }) => (
  <div className="card-hover">
    <div className="flex items-center justify-between mb-6">
      <h3 className="heading-3 text-gray-900">{title}</h3>
      {actions && <div className="flex space-x-2">{actions}</div>}
    </div>
    {children}
  </div>
);

const SentimentIndicator = ({ sentiment, score }) => {
  const cfg =
    sentiment === 'positive' ? { color: 'text-green-600 bg-green-100 border-green-200',  emoji: '😊' } :
    sentiment === 'negative' ? { color: 'text-red-600 bg-red-100 border-red-200',        emoji: '😞' } :
                               { color: 'text-gray-600 bg-gray-100 border-gray-200',      emoji: '😐' };
  return (
    <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full border text-xs font-medium ${cfg.color}`}>
      <span>{cfg.emoji}</span>
      <span>{sentiment}</span>
      <span>({(score * 100).toFixed(0)}%)</span>
    </span>
  );
};

/** "Last updated X ago" + spinner refresh button */
const LastUpdatedBadge = ({ secondsAgo, onRefresh, refreshing }) => (
  <div className="flex items-center space-x-1.5 text-xs text-gray-400 select-none">
    <Clock size={12} />
    <span>Last updated {formatSecondsAgo(secondsAgo)}</span>
    <button
      id="analytics-refresh-btn"
      onClick={onRefresh}
      title="Refresh analytics now"
      className={`ml-1 p-1 rounded-full hover:bg-gray-100 hover:text-gray-600 transition-colors ${
        refreshing ? 'animate-spin text-primary-500' : ''
      }`}
    >
      <RefreshCw size={12} />
    </button>
  </div>
);

// ─────────────────────────────────────────────────────────────────────────────
// Analytics page
// ─────────────────────────────────────────────────────────────────────────────

const Analytics = () => {
  const { user }   = useAuth();
  const { dispatch } = useApp();
  const businessId = user?._id || user?.id || '';

  const [activeTab, setActiveTab] = useState('overview');
  const [dateRange, setDateRange] = useState('30d');

  // ── All data fetching is managed by this hook ────────────────────────────
  const {
    analyticsData,
    sentimentData,
    customerData,
    productData,
    eventSummary,
    loading,
    secondsAgo,
    refresh,
  } = useAnalyticsRange(dateRange, businessId);

  // Keep AppContext in sync whenever eventSummary changes
  React.useEffect(() => {
    if (!eventSummary) return;
    dispatch({
      type: 'SET_ENGAGEMENT_METRICS',
      payload: {
        bounce_rate:              eventSummary.bounce_rate              || 0,
        cta_click_rate:           eventSummary.cta_click_rate           || 0,
        booking_conversion_rate:  eventSummary.booking_conversion_rate  || 0,
        page_views:               eventSummary.page_view                || 0,
        cta_clicks:               eventSummary.cta_click                || 0,
        bounces:                  eventSummary.bounce                   || 0,
      },
    });
  }, [eventSummary, dispatch]);

  // ── Loading skeleton ──────────────────────────────────────────────────────
  if (loading && !analyticsData) {
    return (
      <div className="space-y-6 animate-fade-in">
        <div className="flex justify-between items-center">
          <div>
            <div className="h-8 w-48 skeleton mb-2" />
            <div className="h-4 w-64 skeleton" />
          </div>
          <div className="h-10 w-32 skeleton rounded-xl" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="h-24 skeleton rounded-2xl" />)}
        </div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card"><div className="h-32 skeleton rounded-xl" /></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="heading-1">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-1">
            Deep insights into your business performance and customer behavior
          </p>
          {/* Last updated indicator */}
          <div className="mt-2">
            <LastUpdatedBadge
              secondsAgo={secondsAgo}
              onRefresh={refresh}
              refreshing={loading && !!analyticsData}
            />
          </div>
        </div>

        <div className="flex items-center space-x-3">
          {/* ── Time-range filter — triggers immediate re-fetch via hook ── */}
          <select
            id="analytics-date-range"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
            className="input-field w-36"
          >
            {DATE_RANGES.map((r) => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>

          {/* ── Manual refresh button ──────────────────────────────────── */}
          <button
            id="analytics-manual-refresh"
            onClick={refresh}
            disabled={loading}
            className={`btn-secondary flex items-center space-x-2 ${loading ? 'opacity-60 cursor-not-allowed' : ''}`}
            title="Refresh all analytics data"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            <span>{loading ? 'Refreshing…' : 'Refresh'}</span>
          </button>

          <button className="btn-primary" id="analytics-export-btn">
            <Download size={16} />
            Export
          </button>
        </div>
      </div>

      {/* ── Tab selectors ───────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            id={`analytics-tab-${tab.id}`}
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
                <div className="w-3 h-3 bg-white/30 rounded-full animate-pulse" />
              </div>
            )}
          </button>
        ))}
      </div>

      {/* ══════════════════════════════════════════════════════════════════════
          OVERVIEW TAB
      ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'overview' && (
        <div className="space-y-8">

          {/* Key metrics — driven by live eventSummary where available */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total Visitors"
              value={(analyticsData?.totalVisits ?? eventSummary?.page_view ?? 0).toLocaleString()}
              icon={Eye}
              color="bg-blue-500"
              gradient="from-blue-500 to-indigo-600"
              description={eventSummary ? `${eventSummary.page_view || 0} page views this period` : 'Unique website visitors'}
            />
            <MetricCard
              title="Customer Messages"
              value={(analyticsData?.totalMessages ?? 0).toLocaleString()}
              icon={MessageSquare}
              color="bg-green-500"
              gradient="from-green-500 to-emerald-600"
              description="Messages received"
            />
            <MetricCard
              title="CTA Clicks"
              value={(eventSummary?.cta_click ?? 0).toLocaleString()}
              icon={MousePointer}
              color="bg-purple-500"
              gradient="from-purple-500 to-pink-600"
              description={`Click rate: ${eventSummary?.cta_click_rate ?? 0}%`}
            />
            <MetricCard
              title="Bounce Rate"
              value={`${eventSummary?.bounce_rate ?? 0}%`}
              icon={ArrowDownRight}
              color="bg-orange-500"
              gradient="from-orange-500 to-red-600"
              description={`${eventSummary?.bounce || 0} bounces / ${eventSummary?.page_view || 0} views`}
            />
          </div>

          {/* Charts — Visitor Trends & Traffic Sources */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* Visitor Trends — built from eventSummary when available, fallback to static */}
            <ChartCard title="Visitor Trends">
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={buildVisitorTrend(eventSummary, dateRange)}>
                  <defs>
                    <linearGradient id="visitorsGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.3} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'white', border: 'none',
                      borderRadius: '12px', boxShadow: '0 10px 40px -10px rgba(0,0,0,.1)',
                    }}
                  />
                  <Area type="monotone" dataKey="visitors" stroke="#3b82f6" strokeWidth={3} fill="url(#visitorsGradient)" name="Visitors" />
                </AreaChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Traffic Sources — static distribution */}
            <ChartCard title="Traffic Sources">
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={TRAFFIC_SOURCES}
                    cx="50%" cy="50%"
                    innerRadius={60} outerRadius={100}
                    paddingAngle={5} dataKey="value"
                  >
                    {TRAFFIC_SOURCES.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
              <div className="mt-6 grid grid-cols-2 gap-4">
                {TRAFFIC_SOURCES.map((item, i) => (
                  <div key={i} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm text-gray-600">{item.name}</span>
                    </div>
                    <span className="text-sm font-semibold text-gray-900">{item.value}%</span>
                  </div>
                ))}
              </div>
            </ChartCard>
          </div>

          {/* Performance summary cards — live data where possible */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Eye className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Page Views</h3>
              <p className="text-3xl font-bold text-blue-600 mb-1 tabular-nums">
                {eventSummary ? (eventSummary.page_view || 0).toLocaleString() : '—'}
              </p>
              <p className="text-sm text-gray-600">This period</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Users className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Conversion Rate</h3>
              <p className="text-3xl font-bold text-green-600 mb-1 tabular-nums">
                {eventSummary ? `${eventSummary.booking_conversion_rate ?? 0}%` : '—'}
              </p>
              <p className="text-sm text-gray-600">Booking conversions</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <MessageSquare className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">CTA Click Rate</h3>
              <p className="text-3xl font-bold text-purple-600 mb-1 tabular-nums">
                {eventSummary ? `${eventSummary.cta_click_rate ?? 0}%` : '—'}
              </p>
              <p className="text-sm text-gray-600">Calls to action</p>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          SERVICES & INQUIRIES TAB
      ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'products' && productData && (
        <div className="space-y-8 animate-fade-in">
          
          {/* Metrics Row */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="Total Service Views"
              value={(productData.totalViews ?? 0).toLocaleString()}
              icon={Eye}
              color="bg-purple-500"
              gradient="from-purple-500 to-indigo-600"
              description="Views on service cards"
            />
            <MetricCard
              title="Message Inquiries"
              value={(productData.totalMessageInquiries ?? productData.totalInquiries ?? 0).toLocaleString()}
              icon={MessageSquare}
              color="bg-pink-500"
              gradient="from-pink-500 to-rose-600"
              description={`${productData.totalContacts ?? 0} contacts · ${productData.totalConsultations ?? 0} consultations · ${productData.totalBookings ?? 0} bookings`}
            />
            <MetricCard
              title="Consultation Rate"
              value={`${productData.consultationRate ?? (productData.totalViews > 0 ? ((productData.totalInquiries / productData.totalViews) * 100).toFixed(1) : '0.0')}%`}
              icon={MousePointer}
              color="bg-emerald-500"
              gradient="from-emerald-500 to-teal-600"
              description="Consultations started from total inquiries"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Visual breakdown chart */}
            <div className="lg:col-span-2">
              <ChartCard title="Service Interest Breakdown (Views vs. Inquiries)">
                {productData.productAnalytics && productData.productAnalytics.length > 0 ? (
                  <ResponsiveContainer width="100%" height={320}>
                    <BarChart data={productData.productAnalytics}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                      <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                      <YAxis tick={{ fontSize: 11 }} />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: 'white',
                          border: 'none',
                          borderRadius: '12px',
                          boxShadow: '0 10px 40px -10px rgba(0,0,0,.1)',
                        }}
                      />
                      <Bar dataKey="views" fill="#a855f7" name="Views" radius={[4, 4, 0, 0]} />
                      <Bar dataKey="inquiries" fill="#ec4899" name="Inquiries" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                    <BarChart3 size={48} className="mb-2" />
                    <span>No service/product views tracked yet.</span>
                  </div>
                )}
              </ChartCard>
            </div>

            {/* Category distribution */}
            <div>
              <ChartCard title="Category Distribution">
                {productData.categoryDistribution && Object.keys(productData.categoryDistribution).length > 0 ? (
                  <div className="space-y-4 pt-4">
                    {Object.entries(productData.categoryDistribution).map(([category, count]) => {
                      const total = productData.totalProducts || 1;
                      const percentage = Math.round((count / total) * 100);
                      return (
                        <div key={category} className="space-y-1">
                          <div className="flex justify-between items-center text-sm">
                            <span className="font-medium text-gray-700 capitalize">{category}</span>
                            <span className="text-gray-500">{count} ({percentage}%)</span>
                          </div>
                          <div className="w-full bg-gray-100 rounded-full h-2">
                            <div 
                              className="bg-purple-600 h-2 rounded-full" 
                              style={{ width: `${percentage}%` }}
                            />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="flex flex-col items-center justify-center h-64 text-gray-400">
                    <span>No categories found.</span>
                    <span>Create a service to see breakdown.</span>
                  </div>
                )}
              </ChartCard>
            </div>
          </div>

          {/* Detailed Performance Table */}
          <ChartCard title="Services Performance Ledger">
            {productData.productAnalytics && productData.productAnalytics.length > 0 ? (
              <div className="overflow-x-auto -mx-6">
                <table className="w-full text-left border-collapse min-w-[600px]">
                  <thead>
                    <tr className="border-b border-gray-100 text-xs font-semibold text-gray-500 uppercase tracking-wider bg-gray-50/50">
                      <th className="px-8 py-4">Service Name</th>
                      <th className="px-6 py-4">Category</th>
                      <th className="px-6 py-4">Price</th>
                      <th className="px-6 py-4 text-center">Views</th>
                      <th className="px-6 py-4 text-center">Inquiries</th>
                      <th className="px-6 py-4 text-center">Interest Rate</th>
                      <th className="px-8 py-4">Popularity Score</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {productData.productAnalytics.map((p) => {
                      const maxScore = Math.max(...productData.productAnalytics.map(x => x.popularity_score), 1);
                      const pct = Math.round((p.popularity_score / maxScore) * 100);
                      const rate = p.views > 0 ? ((p.inquiries / p.views) * 100).toFixed(1) : '0.0';
                      return (
                        <tr key={p.id} className="hover:bg-gray-50/50 transition-colors">
                          <td className="px-8 py-4">
                            <div className="font-semibold text-gray-900">{p.name}</div>
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 capitalize">{p.category}</td>
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            {typeof p.price === 'number' ? `$${p.price.toFixed(2)}` : p.price}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-600 text-center font-mono">{p.views}</td>
                          <td className="px-6 py-4 text-sm text-gray-600 text-center font-mono">{p.inquiries}</td>
                          <td className="px-6 py-4 text-center">
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold ${
                              parseFloat(rate) > 20 ? 'bg-green-50 text-green-700' :
                              parseFloat(rate) > 5 ? 'bg-blue-50 text-blue-700' : 'bg-gray-50 text-gray-600'
                            }`}>
                              {rate}%
                            </span>
                          </td>
                          <td className="px-8 py-4">
                            <div className="flex items-center space-x-3">
                              <span className="text-sm font-semibold text-gray-900 font-mono w-8 text-right">{p.popularity_score}</span>
                              <div className="w-24 bg-gray-100 rounded-full h-1.5 overflow-hidden">
                                <div 
                                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-1.5 rounded-full" 
                                  style={{ width: `${pct}%` }}
                                />
                              </div>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                No active services/products registered under this account.
              </div>
            )}
          </ChartCard>

        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          SENTIMENT TAB
      ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'sentiment' && sentimentData && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Sentiment overview */}
            <div className="card bg-gradient-to-br from-pink-50 to-rose-50 border-pink-200">
              <h3 className="heading-3 text-pink-900 mb-6">Overall Sentiment</h3>
              <div className="text-center">
                <div className="text-6xl mb-4">😊</div>
                <div className="text-2xl font-bold text-pink-700 mb-2">Positive</div>
                <div className="text-pink-600">Based on 156 interactions</div>
              </div>
              <div className="mt-6 space-y-3">
                {[
                  { label: 'Positive', pct: 68, barClass: 'bg-gradient-to-r from-pink-500 to-rose-500', textClass: 'text-pink-700', bgClass: 'bg-pink-200' },
                  { label: 'Neutral',  pct: 22, barClass: 'bg-gray-400',  textClass: 'text-gray-600',  bgClass: 'bg-gray-200' },
                  { label: 'Negative', pct: 10, barClass: 'bg-red-500',   textClass: 'text-red-600',   bgClass: 'bg-red-200' },
                ].map((row) => (
                  <React.Fragment key={row.label}>
                    <div className="flex justify-between items-center">
                      <span className={`text-sm ${row.textClass}`}>{row.label}</span>
                      <span className={`text-sm font-semibold ${row.textClass}`}>{row.pct}%</span>
                    </div>
                    <div className={`w-full ${row.bgClass} rounded-full h-2`}>
                      <div className={`${row.barClass} h-2 rounded-full`} style={{ width: `${row.pct}%` }} />
                    </div>
                  </React.Fragment>
                ))}
              </div>
            </div>

            {/* Recent Feedback */}
            <div className="lg:col-span-2">
              <ChartCard title="Recent Customer Feedback">
                <div className="space-y-4 max-h-96 overflow-y-auto">
                  {SAMPLE_FEEDBACK.map((fb, i) => (
                    <div key={i} className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                            {fb.customer.split(' ').map((n) => n[0]).join('')}
                          </div>
                          <div>
                            <span className="font-medium text-gray-900">{fb.customer}</span>
                            <div className="flex items-center space-x-2 mt-1">
                              <SentimentIndicator sentiment={fb.sentiment} score={fb.score} />
                              <span className="text-xs text-gray-500">{fb.time}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <p className="text-gray-700 text-sm">{fb.message}</p>
                    </div>
                  ))}
                </div>
              </ChartCard>
            </div>
          </div>
        </div>
      )}

      {/* ══════════════════════════════════════════════════════════════════════
          CUSTOMER INSIGHTS TAB
      ══════════════════════════════════════════════════════════════════════ */}
      {activeTab === 'customers' && customerData && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="Total Customers"
              value={(customerData?.totalCustomers ?? 0).toLocaleString() || '1,234'}
              icon={Users}
              color="bg-blue-500"
              gradient="from-blue-500 to-indigo-600"
              change={12.5}
              description="Active customers"
            />
            <MetricCard
              title="Customer Lifetime Value"
              value={customerData?.avgLifetimeValue ? `$${customerData.avgLifetimeValue}` : '$312'}
              icon={TrendingUp}
              color="bg-green-500"
              gradient="from-green-500 to-emerald-600"
              change={8.3}
              description="Average per customer"
            />
            <MetricCard
              title="Retention Rate"
              value={customerData?.retentionRate ? `${customerData.retentionRate}%` : '84%'}
              icon={Heart}
              color="bg-purple-500"
              gradient="from-purple-500 to-pink-600"
              change={5.2}
              description="Customer retention"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Customer Growth — built from customerData or fallback */}
            <ChartCard title="Customer Growth">
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={buildCustomerGrowth(customerData)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Bar dataKey="customers" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </ChartCard>

            {/* Top engaged customers */}
            <ChartCard title="Top Engaged Customers">
              <div className="space-y-4">
                {(customerData?.topCustomers ?? SAMPLE_CUSTOMERS).map((c, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100">
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                        {i + 1}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{c.name}</p>
                        <p className="text-sm text-gray-600">{c.email}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-gray-900">{c.value}</p>
                      <p className="text-sm text-gray-600">{c.interactions} interactions</p>
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

// ─────────────────────────────────────────────────────────────────────────────
// Helpers — build chart data from live API response with sensible fallbacks
// ─────────────────────────────────────────────────────────────────────────────

const TRAFFIC_SOURCES = [
  { name: 'QR Codes',     value: 45, color: '#3b82f6' },
  { name: 'Direct',       value: 30, color: '#10b981' },
  { name: 'Social Media', value: 15, color: '#f59e0b' },
  { name: 'Search',       value: 10, color: '#ef4444' },
];

const SAMPLE_FEEDBACK = [
  { customer: 'Sarah Johnson', message: 'Amazing service! The team was very helpful and responsive.', sentiment: 'positive', score: 0.9,  time: '2h ago' },
  { customer: 'Mike Chen',     message: 'Good experience overall, delivery was on time.',            sentiment: 'positive', score: 0.7,  time: '4h ago' },
  { customer: 'Emma Davis',    message: 'The product quality could be better for the price.',        sentiment: 'neutral',  score: 0.1,  time: '6h ago' },
  { customer: 'John Smith',    message: 'Excellent customer support, resolved my issue quickly!',   sentiment: 'positive', score: 0.95, time: '8h ago' },
];

const SAMPLE_CUSTOMERS = [
  { name: 'Sarah Johnson', email: 'sarah@email.com', interactions: 24, value: '$450' },
  { name: 'Mike Chen',     email: 'mike@email.com',  interactions: 18, value: '$320' },
  { name: 'Emma Davis',    email: 'emma@email.com',  interactions: 15, value: '$280' },
  { name: 'John Smith',    email: 'john@email.com',  interactions: 12, value: '$190' },
];

/** Build a simple visitor trend chart from the event summary total + range */
function buildVisitorTrend(summary, range) {
  const DAYS_MAP = { '7d': 7, '30d': 30, '90d': 90, '1y': 52 };
  const points   = DAYS_MAP[range] ?? 7;
  const total    = summary?.page_view ?? 0;

  if (!total) {
    // Fallback: deterministic demo data so the chart is never empty
    return ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'].map((name, i) => ({
      name,
      visitors: [1200, 1100, 1300, 1400, 1600, 1350, 1100][i],
    }));
  }

  // Distribute total page views across the selected period with slight variance
  const labels = range === '7d'
    ? ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    : range === '1y'
    ? ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    : Array.from({ length: Math.min(points, 12) }, (_, i) => `W${i + 1}`);

  const base  = Math.round(total / labels.length);
  return labels.map((name, i) => ({
    name,
    visitors: Math.max(0, base + Math.round((Math.sin(i) * base * 0.2))),
  }));
}

function buildCustomerGrowth(customerData) {
  if (customerData?.growthData) return customerData.growthData;
  return [
    { month: 'Jan', customers: 120 },
    { month: 'Feb', customers: 150 },
    { month: 'Mar', customers: 180 },
    { month: 'Apr', customers: 220 },
    { month: 'May', customers: 280 },
    { month: 'Jun', customers: 350 },
  ];
}

export default Analytics;
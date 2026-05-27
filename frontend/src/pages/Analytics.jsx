import React, { useState, useEffect, useCallback } from 'react';
import {
  BarChart3, TrendingUp, Users, MessageSquare, Eye, Heart,
  Download, RefreshCw, AlertCircle, ArrowUp, ArrowDown
} from 'lucide-react';
import {
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, BarChart, Bar, AreaChart, Area
} from 'recharts';
import { api } from '../services/api';
import toast from 'react-hot-toast';

// ─── Constants ──────────────────────────────────────────────────────────────

const TABS = [
  { id: 'overview',   name: 'Overview',           icon: BarChart3,    gradient: 'from-blue-500 to-indigo-600'  },
  { id: 'sentiment',  name: 'Customer Sentiment',  icon: Heart,        gradient: 'from-pink-500 to-rose-600'    },
  { id: 'customers',  name: 'Customer Insights',   icon: Users,        gradient: 'from-green-500 to-emerald-600'},
];

const DATE_RANGES = [
  { value: '7d',  label: '7 Days',  days: 7   },
  { value: '30d', label: '30 Days', days: 30  },
  { value: '90d', label: '90 Days', days: 90  },
  { value: '1y',  label: '1 Year',  days: 365 },
];

const TRAFFIC_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444'];

// ─── Helpers ─────────────────────────────────────────────────────────────────

const fmt = (n, prefix = '') => {
  if (n === null || n === undefined) return `${prefix}0`;
  if (n >= 1_000_000) return `${prefix}${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000)     return `${prefix}${(n / 1_000).toFixed(1)}K`;
  return `${prefix}${n}`;
};

const pct = (n) => (n !== null && n !== undefined ? `${n > 0 ? '+' : ''}${n}%` : null);

const dayParam = (rangeValue) =>
  DATE_RANGES.find(r => r.value === rangeValue)?.days ?? 30;

// Derive dominant sentiment label from distribution counts
const dominantSentiment = (dist) => {
  if (!dist) return { label: 'neutral', emoji: '😐' };
  const entries = Object.entries(dist);
  if (!entries.length) return { label: 'neutral', emoji: '😐' };
  const [label] = entries.sort((a, b) => b[1] - a[1])[0];
  const emoji = label === 'positive' ? '😊' : label === 'negative' ? '😞' : '😐';
  return { label, emoji };
};

// Convert raw sentiment distribution counts → percentage objects
const sentimentPercents = (dist, total) => {
  if (!dist || !total) return { positive: 0, neutral: 0, negative: 0 };
  return {
    positive: Math.round(((dist.positive ?? 0) / total) * 100),
    neutral:  Math.round(((dist.neutral  ?? 0) / total) * 100),
    negative: Math.round(((dist.negative ?? 0) / total) * 100),
  };
};

// Build traffic-source pie slices from live visit/scan/message counts
const buildTrafficSlices = (overview) => {
  if (!overview) return [];
  const scans    = overview.totalScans    ?? 0;
  const visits   = overview.totalVisits   ?? 0;
  const messages = overview.totalMessages ?? 0;
  const total    = scans + visits + messages;
  if (total === 0) return [];
  return [
    { name: 'QR Codes',   value: Math.round((scans    / total) * 100), color: '#3b82f6' },
    { name: 'Web Visits', value: Math.round((visits   / total) * 100), color: '#10b981' },
    { name: 'Messages',   value: Math.round((messages / total) * 100), color: '#f59e0b' },
  ].filter(s => s.value > 0);
};

// Reformat ISO date key "YYYY-MM" → short month label "Jan"
const shortMonth = (key) => {
  if (!key) return '';
  try {
    const [year, month] = key.split('-');
    return new Date(parseInt(year), parseInt(month) - 1, 1)
      .toLocaleString('default', { month: 'short' });
  } catch { return key; }
};

// ─── Shared sub-components ───────────────────────────────────────────────────

const MetricCard = ({ title, value, icon: Icon, color, gradient, change, description }) => (
  <div className={`card-hover bg-gradient-to-br ${gradient} text-white relative overflow-hidden`}>
    <div className="absolute inset-0 bg-hero-pattern opacity-10" />
    <div className={`absolute -top-4 -right-4 w-24 h-24 ${color} rounded-full opacity-20`} />

    <div className="relative z-10">
      <div className="flex items-center justify-between mb-4">
        <div className="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
          <Icon size={24} />
        </div>
        {change !== null && change !== undefined && (
          <div className="flex items-center space-x-1 px-2 py-1 bg-white/20 backdrop-blur-sm rounded-full text-xs font-medium">
            {change >= 0 ? <ArrowUp size={12} /> : <ArrowDown size={12} />}
            <span>{Math.abs(change)}%</span>
          </div>
        )}
      </div>

      <div>
        <p className="text-white/80 text-sm font-medium mb-1">{title}</p>
        <p className="text-2xl font-bold mb-1">{value}</p>
        {description && <p className="text-white/70 text-xs">{description}</p>}
      </div>
    </div>
  </div>
);

const ChartCard = ({ title, children, actions, minH = 0 }) => (
  <div className="card-hover">
    <div className="flex items-center justify-between mb-6">
      <h3 className="heading-3 text-gray-900">{title}</h3>
      {actions && <div className="flex space-x-2">{actions}</div>}
    </div>
    <div style={minH ? { minHeight: minH } : {}}>{children}</div>
  </div>
);

const SentimentIndicator = ({ sentiment, score }) => {
  const cfg =
    sentiment === 'positive' ? { cls: 'text-green-600 bg-green-100 border-green-200',  emoji: '😊' } :
    sentiment === 'negative' ? { cls: 'text-red-600   bg-red-100   border-red-200',    emoji: '😞' } :
                               { cls: 'text-gray-600  bg-gray-100  border-gray-200',   emoji: '😐' };
  return (
    <span className={`inline-flex items-center space-x-1 px-3 py-1 rounded-full border text-xs font-medium ${cfg.cls}`}>
      <span>{cfg.emoji}</span>
      <span>{sentiment}</span>
      {score !== undefined && <span>({(score * 100).toFixed(0)}%)</span>}
    </span>
  );
};

const EmptyState = ({ icon: Icon = BarChart3, message = 'No data available yet.', sub }) => (
  <div className="flex items-center justify-center h-64 text-gray-400">
    <div className="text-center">
      <Icon size={48} className="mx-auto mb-3 text-gray-300" />
      <p className="text-sm">{message}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  </div>
);

const SectionSkeleton = ({ rows = 4 }) => (
  <div className="space-y-4">
    {[...Array(rows)].map((_, i) => (
      <div key={i} className="h-16 skeleton rounded-xl" />
    ))}
  </div>
);

// ─── Main component ───────────────────────────────────────────────────────────

const Analytics = () => {
  // Per-tab data
  const [overview,    setOverview]    = useState(null);
  const [sentiment,   setSentiment]   = useState(null);
  const [feedback,    setFeedback]    = useState([]);
  const [customers,   setCustomers]   = useState(null);

  // Per-tab loading
  const [loadingOverview,   setLoadingOverview]   = useState(false);
  const [loadingSentiment,  setLoadingSentiment]  = useState(false);
  const [loadingCustomers,  setLoadingCustomers]  = useState(false);

  // Global UI state
  const [activeTab,  setActiveTab]  = useState('overview');
  const [dateRange,  setDateRange]  = useState('30d');

  // ── Fetch overview (tab 1) ──────────────────────────────────────────────────
  const fetchOverview = useCallback(async () => {
    setLoadingOverview(true);
    try {
      const res = await api.get(`/analytics/overview?days=${dayParam(dateRange)}`);
      setOverview(res.data);
    } catch {
      toast.error('Failed to load overview analytics');
    } finally {
      setLoadingOverview(false);
    }
  }, [dateRange]);

  // ── Fetch sentiment + feedback (tab 2) ─────────────────────────────────────
  const fetchSentiment = useCallback(async () => {
    setLoadingSentiment(true);
    try {
      const [sentRes, fbRes] = await Promise.allSettled([
        api.get('/analytics/sentiment'),
        api.get('/customers/feedback?per_page=10'),
      ]);
      if (sentRes.status === 'fulfilled') setSentiment(sentRes.value.data);
      if (fbRes.status === 'fulfilled')   setFeedback(fbRes.value.data.feedback ?? []);
    } catch {
      toast.error('Failed to load sentiment data');
    } finally {
      setLoadingSentiment(false);
    }
  }, []);

  // ── Fetch customer insights (tab 3) ────────────────────────────────────────
  const fetchCustomers = useCallback(async () => {
    setLoadingCustomers(true);
    try {
      const res = await api.get('/analytics/customers');
      setCustomers(res.data);
    } catch {
      toast.error('Failed to load customer analytics');
    } finally {
      setLoadingCustomers(false);
    }
  }, []);

  // Load on tab/date change — lazy: only fetch what the active tab needs
  useEffect(() => {
    if (activeTab === 'overview')  fetchOverview();
  }, [activeTab, dateRange, fetchOverview]);

  useEffect(() => {
    if (activeTab === 'sentiment') fetchSentiment();
  }, [activeTab, fetchSentiment]);

  useEffect(() => {
    if (activeTab === 'customers') fetchCustomers();
  }, [activeTab, fetchCustomers]);

  // Manual refresh button
  const handleRefresh = () => {
    if (activeTab === 'overview')  fetchOverview();
    if (activeTab === 'sentiment') fetchSentiment();
    if (activeTab === 'customers') fetchCustomers();
  };

  // ── Derived values ──────────────────────────────────────────────────────────

  // Overview metrics cards — from /analytics/overview
  const totalVisitors   = overview?.totalVisits   ?? 0;
  const totalMessages   = overview?.totalMessages ?? 0;
  const totalNewCust    = overview?.totalCustomers ?? 0;
  const totalScans      = overview?.totalScans    ?? 0;
  const engagementRate  = totalVisitors > 0
    ? Math.min(100, Math.round(((totalMessages + totalNewCust) / totalVisitors) * 100))
    : 0;

  // Time-series chart — backend returns daily rows {date, messages, customers, visits}
  const timeSeriesData  = (overview?.timeSeriesData ?? []).map(row => ({
    name:      row.date ? new Date(row.date).toLocaleDateString('default', { month: 'short', day: 'numeric' }) : '',
    visitors:  row.visits    ?? 0,
    messages:  row.messages  ?? 0,
    customers: row.customers ?? 0,
  }));

  // Traffic source pie — built from live counts
  const trafficSlices   = buildTrafficSlices(overview);

  // Sentiment tab
  const sentDist        = sentiment?.sentimentDistribution ?? {};
  const sentTotal       = sentiment?.totalAnalyzed ?? 0;
  const sentPct         = sentimentPercents(sentDist, sentTotal);
  const dominant        = dominantSentiment(sentDist);

  // Customer growth chart — registrationTrend from /analytics/customers
  const growthData      = (customers?.registrationTrend ?? []).map(row => ({
    month:     shortMonth(row.month),
    customers: row.registrations ?? 0,
  }));

  // Top engaged customers from backend
  const topEngaged      = (customers?.topEngagedCustomers ?? []).slice(0, 8);

  // Customer lifetime value: not yet a backend field, show avg engagement as proxy
  const avgEngagement   = customers?.averageEngagement ?? 0;

  // ── Loading skeleton (full page, only shown before first overview load) ─────
  const isFirstLoad = loadingOverview && !overview && activeTab === 'overview';

  if (isFirstLoad) {
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
          {[...Array(3)].map((_, i) => (
            <div key={i} className="h-24 skeleton rounded-2xl" />
          ))}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card">
              <div className="h-32 skeleton rounded-xl" />
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {[...Array(2)].map((_, i) => (
            <div key={i} className="card">
              <div className="h-72 skeleton rounded-xl" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // ── Render ──────────────────────────────────────────────────────────────────
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
            {DATE_RANGES.map(r => (
              <option key={r.value} value={r.value}>{r.label}</option>
            ))}
          </select>

          <button onClick={handleRefresh} className="btn-secondary flex items-center space-x-2">
            <RefreshCw size={16} className={loadingOverview || loadingSentiment || loadingCustomers ? 'animate-spin' : ''} />
            <span>Refresh</span>
          </button>

          <button className="btn-primary flex items-center space-x-2">
            <Download size={16} />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Tab selector */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {TABS.map(tab => (
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
              <h3 className={`font-semibold ${activeTab === tab.id ? 'text-white' : 'text-gray-900'}`}>
                {tab.name}
              </h3>
            </div>
            {activeTab === tab.id && (
              <div className="absolute top-2 right-2">
                <div className="w-3 h-3 bg-white/30 rounded-full animate-pulse" />
              </div>
            )}
          </button>
        ))}
      </div>

      {/* ── OVERVIEW TAB ────────────────────────────────────────────────────── */}
      {activeTab === 'overview' && (
        <div className="space-y-8">

          {/* Key Metrics — all from /analytics/overview */}
          {loadingOverview ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => <div key={i} className="h-36 skeleton rounded-2xl" />)}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <MetricCard
                title="Total Visitors"
                value={fmt(totalVisitors)}
                icon={Eye}
                color="bg-blue-500"
                gradient="from-blue-500 to-indigo-600"
                change={null}
                description="Unique website visitors"
              />
              <MetricCard
                title="Customer Messages"
                value={fmt(totalMessages)}
                icon={MessageSquare}
                color="bg-green-500"
                gradient="from-green-500 to-emerald-600"
                change={null}
                description="Messages received"
              />
              <MetricCard
                title="New Customers"
                value={fmt(totalNewCust)}
                icon={Users}
                color="bg-purple-500"
                gradient="from-purple-500 to-pink-600"
                change={null}
                description="New registrations"
              />
              <MetricCard
                title="Engagement Rate"
                value={`${engagementRate}%`}
                icon={TrendingUp}
                color="bg-orange-500"
                gradient="from-orange-500 to-red-600"
                change={null}
                description="Customer interaction rate"
              />
            </div>
          )}

          {/* Charts — time series + traffic sources */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* Visitor / engagement trends — from timeSeriesData */}
            <ChartCard title="Visitor Trends">
              {loadingOverview ? (
                <div className="h-72 skeleton rounded-xl" />
              ) : timeSeriesData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={timeSeriesData}>
                    <defs>
                      <linearGradient id="visitorsGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%"  stopColor="#3b82f6" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}   />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white', border: 'none',
                        borderRadius: '12px', boxShadow: '0 10px 40px -10px rgba(0,0,0,0.1)',
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="visitors"
                      stroke="#3b82f6"
                      strokeWidth={3}
                      fill="url(#visitorsGrad)"
                      name="Visitors"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState icon={Eye} message="No visitor trend data yet." sub="Data appears as your website receives traffic." />
              )}
            </ChartCard>

            {/* Traffic Sources — built from live QR / visits / message counts */}
            <ChartCard title="Traffic Sources">
              {loadingOverview ? (
                <div className="h-72 skeleton rounded-xl" />
              ) : trafficSlices.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={220}>
                    <PieChart>
                      <Pie
                        data={trafficSlices}
                        cx="50%"
                        cy="50%"
                        innerRadius={55}
                        outerRadius={90}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {trafficSlices.map((entry, i) => (
                          <Cell key={`cell-${i}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip formatter={(v, n) => [`${v}%`, n]} />
                    </PieChart>
                  </ResponsiveContainer>

                  <div className="mt-4 grid grid-cols-2 gap-3">
                    {trafficSlices.map((item, i) => (
                      <div key={i} className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-sm text-gray-600">{item.name}</span>
                        </div>
                        <span className="text-sm font-semibold text-gray-900">{item.value}%</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <EmptyState icon={BarChart3} message="No traffic source data yet." sub="Data populates as visitors arrive via different channels." />
              )}
            </ChartCard>
          </div>

          {/* Performance summary — derived from overview totals */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Eye className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Total Visits</h3>
              <p className="text-3xl font-bold text-blue-600 mb-1">
                {loadingOverview ? '—' : fmt(totalVisitors)}
              </p>
              <p className="text-sm text-gray-600">In selected period</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <Users className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">QR Scans</h3>
              <p className="text-3xl font-bold text-green-600 mb-1">
                {loadingOverview ? '—' : fmt(totalScans)}
              </p>
              <p className="text-sm text-gray-600">Physical → Digital</p>
            </div>

            <div className="card text-center">
              <div className="w-16 h-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl mx-auto mb-4 flex items-center justify-center">
                <MessageSquare className="text-white" size={24} />
              </div>
              <h3 className="font-semibold text-gray-900 mb-2">Engagement Rate</h3>
              <p className="text-3xl font-bold text-purple-600 mb-1">
                {loadingOverview ? '—' : `${engagementRate}%`}
              </p>
              <p className="text-sm text-gray-600">Interactions vs. visits</p>
            </div>
          </div>
        </div>
      )}

      {/* ── SENTIMENT TAB ────────────────────────────────────────────────────── */}
      {activeTab === 'sentiment' && (
        <div className="space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

            {/* Sentiment Overview — from /analytics/sentiment sentimentDistribution */}
            <div className="card bg-gradient-to-br from-pink-50 to-rose-50 border-pink-200">
              <h3 className="heading-3 text-pink-900 mb-6">Overall Sentiment</h3>

              {loadingSentiment ? (
                <SectionSkeleton rows={3} />
              ) : sentTotal === 0 ? (
                <EmptyState icon={Heart} message="No sentiment data yet." />
              ) : (
                <>
                  <div className="text-center mb-6">
                    <div className="text-6xl mb-3">{dominant.emoji}</div>
                    <div className="text-2xl font-bold text-pink-700 mb-1 capitalize">{dominant.label}</div>
                    <div className="text-pink-600 text-sm">Based on {sentTotal} interactions</div>
                  </div>

                  <div className="space-y-4">
                    {/* Positive */}
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-pink-700">Positive</span>
                        <span className="text-sm font-semibold text-pink-700">{sentPct.positive}%</span>
                      </div>
                      <div className="w-full bg-pink-200 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-pink-500 to-rose-500 h-2 rounded-full transition-all duration-700"
                          style={{ width: `${sentPct.positive}%` }}
                        />
                      </div>
                    </div>

                    {/* Neutral */}
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-gray-600">Neutral</span>
                        <span className="text-sm font-semibold text-gray-600">{sentPct.neutral}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-gray-400 h-2 rounded-full transition-all duration-700"
                          style={{ width: `${sentPct.neutral}%` }}
                        />
                      </div>
                    </div>

                    {/* Negative */}
                    <div>
                      <div className="flex justify-between items-center mb-1">
                        <span className="text-sm text-red-600">Negative</span>
                        <span className="text-sm font-semibold text-red-600">{sentPct.negative}%</span>
                      </div>
                      <div className="w-full bg-red-200 rounded-full h-2">
                        <div
                          className="bg-red-500 h-2 rounded-full transition-all duration-700"
                          style={{ width: `${sentPct.negative}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Recent Customer Feedback — from /customers/feedback */}
            <div className="lg:col-span-2">
              <ChartCard title="Recent Customer Feedback">
                {loadingSentiment ? (
                  <SectionSkeleton rows={4} />
                ) : feedback.length === 0 ? (
                  <EmptyState icon={MessageSquare} message="No customer feedback yet." sub="Feedback submitted via your website will appear here." />
                ) : (
                  <div className="space-y-4 max-h-96 overflow-y-auto pr-1">
                    {feedback.map((fb, index) => {
                      const name = fb.customer_name || 'Anonymous';
                      const initials = name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
                      const sentimentLabel = fb.rating >= 4 ? 'positive' : fb.rating <= 2 ? 'negative' : 'neutral';
                      const sentimentScore = fb.rating ? (fb.rating - 1) / 4 : 0.5;
                      const relTime = fb.created_at
                        ? new Date(fb.created_at).toLocaleDateString()
                        : 'Recently';

                      return (
                        <div
                          key={fb._id ?? index}
                          className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-md transition-shadow"
                        >
                          <div className="flex justify-between items-start mb-2">
                            <div className="flex items-center space-x-3">
                              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-secondary-500 rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                                {initials}
                              </div>
                              <div>
                                <span className="font-medium text-gray-900">{name}</span>
                                <div className="flex items-center space-x-2 mt-1">
                                  <SentimentIndicator sentiment={sentimentLabel} score={sentimentScore} />
                                  <span className="text-xs text-gray-500">{relTime}</span>
                                </div>
                              </div>
                            </div>
                            {fb.rating && (
                              <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
                                ★ {fb.rating}/5
                              </span>
                            )}
                          </div>
                          {fb.feedback_text && (
                            <p className="text-gray-700 text-sm mt-2 ml-13 leading-relaxed">
                              {fb.feedback_text}
                            </p>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </ChartCard>
            </div>
          </div>
        </div>
      )}

      {/* ── CUSTOMER INSIGHTS TAB ────────────────────────────────────────────── */}
      {activeTab === 'customers' && (
        <div className="space-y-8">

          {/* Customer Stats — from /analytics/customers */}
          {loadingCustomers ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => <div key={i} className="h-36 skeleton rounded-2xl" />)}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <MetricCard
                title="Total Customers"
                value={fmt(customers?.totalCustomers ?? 0)}
                icon={Users}
                color="bg-blue-500"
                gradient="from-blue-500 to-indigo-600"
                change={null}
                description="Registered customers"
              />
              <MetricCard
                title="Avg. Messages / Customer"
                value={avgEngagement > 0 ? avgEngagement.toFixed(1) : '0'}
                icon={TrendingUp}
                color="bg-green-500"
                gradient="from-green-500 to-emerald-600"
                change={null}
                description="Engagement depth"
              />
              <MetricCard
                title="Unique Locations"
                value={Object.keys(customers?.locationDistribution ?? {}).length}
                icon={Heart}
                color="bg-purple-500"
                gradient="from-purple-500 to-pink-600"
                change={null}
                description="Distinct customer locations"
              />
            </div>
          )}

          {/* Customer Growth + Top Engaged */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

            {/* Customer Growth — registrationTrend from /analytics/customers */}
            <ChartCard title="Customer Growth">
              {loadingCustomers ? (
                <div className="h-72 skeleton rounded-xl" />
              ) : growthData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={growthData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                    <XAxis dataKey="month" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                    <Tooltip
                      contentStyle={{
                        backgroundColor: 'white', border: 'none',
                        borderRadius: '12px', boxShadow: '0 10px 40px -10px rgba(0,0,0,0.1)',
                      }}
                    />
                    <Bar dataKey="customers" fill="#3b82f6" radius={[4, 4, 0, 0]} name="New Customers" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <EmptyState icon={Users} message="No customer growth data yet." sub="Registration trends will appear here over time." />
              )}
            </ChartCard>

            {/* Top Engaged Customers — topEngagedCustomers from /analytics/customers */}
            <ChartCard title="Top Engaged Customers">
              {loadingCustomers ? (
                <SectionSkeleton rows={5} />
              ) : topEngaged.length === 0 ? (
                <EmptyState icon={Users} message="No engagement data yet." sub="Customers who message most frequently appear here." />
              ) : (
                <div className="space-y-3">
                  {topEngaged.map((customer, index) => {
                    const email    = customer.email ?? '';
                    const count    = customer.messageCount ?? 0;
                    const initials = email.slice(0, 2).toUpperCase();

                    return (
                      <div
                        key={index}
                        className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-white rounded-xl border border-gray-100 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-600 rounded-full flex items-center justify-center text-white text-sm font-semibold flex-shrink-0">
                            {index + 1}
                          </div>
                          <div>
                            <p className="font-medium text-gray-900 truncate max-w-[180px]">{email}</p>
                            <p className="text-xs text-gray-500">{count} message{count !== 1 ? 's' : ''}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <div className="w-full bg-gray-200 rounded-full h-2 w-16">
                            <div
                              className="bg-gradient-to-r from-green-400 to-emerald-500 h-2 rounded-full"
                              style={{
                                width: `${Math.min(100, (count / Math.max(1, topEngaged[0]?.messageCount ?? 1)) * 100)}%`
                              }}
                            />
                          </div>
                          <span className="text-xs font-semibold text-gray-700 w-8 text-right">{count}</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </ChartCard>
          </div>
        </div>
      )}
    </div>
  );
};

export default Analytics;
import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  Users, Mail, MessageSquare, TrendingUp, 
  Send, Eye, ThumbsUp, ThumbsDown, AlertCircle 
} from 'lucide-react';
import { api } from '../services/api';
import toast from 'react-hot-toast';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// Simple chart components to replace recharts temporarily
const SimpleBarChart = ({ data, dataKey, xKey }) => (
  <div className="space-y-2">
    {data.map((item, index) => (
      <div key={index} className="flex items-center space-x-3">
        <div className="w-20 text-sm text-gray-600 truncate">{item[xKey]}</div>
        <div className="flex-1 bg-gray-200 rounded-full h-4">
          <div 
            className="bg-blue-500 h-4 rounded-full" 
            style={{ width: `${Math.min(100, (item[dataKey] / Math.max(...data.map(d => d[dataKey]))) * 100)}%` }}
          />
        </div>
        <div className="w-12 text-sm font-medium text-gray-900">{item[dataKey]}</div>
      </div>
    ))}
  </div>
);

const SimplePieChart = ({ data }) => (
  <div className="space-y-2">
    {data.map((item, index) => (
      <div key={index} className="flex items-center justify-between p-2 rounded border">
        <div className="flex items-center space-x-2">
          <div 
            className="w-4 h-4 rounded-full" 
            style={{ backgroundColor: item.color || COLORS[index % COLORS.length] }}
          />
          <span className="text-sm font-medium">{item.name}</span>
        </div>
        <span className="text-sm text-gray-600">{item.value}</span>
      </div>
    ))}
  </div>
);

const WebsiteAnalytics = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [feedbackAnalytics, setFeedbackAnalytics] = useState(null);
  const [subscribers, setSubscribers] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Campaign form state
  const [campaignForm, setCampaignForm] = useState({
    subject: '',
    message: '',
    html_message: '',
    website_source: '',
    filter: 'all'
  });
  const [sendingCampaign, setSendingCampaign] = useState(false);
  const [campaignResult, setCampaignResult] = useState(null);

  // Filters
  const [selectedWebsite, setSelectedWebsite] = useState('');
  const [dateRange, setDateRange] = useState(30);

  useEffect(() => {
    loadDashboardData();
    loadFeedbackAnalytics();
    loadSubscribers();
    loadCampaigns();
  }, [selectedWebsite, dateRange]);

  const loadDashboardData = async () => {
    try {
      const response = await api.get('/analytics/dashboard-summary');
      if (response.data.success) {
        setDashboardData(response.data.summary);
      }
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      setError('Failed to load dashboard data');
    }
  };

  const loadFeedbackAnalytics = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedWebsite) params.append('website_source', selectedWebsite);
      params.append('days', dateRange.toString());
      
      const response = await api.get(`/analytics/feedback-analytics?${params}`);
      if (response.data.success) {
        setFeedbackAnalytics(response.data.analytics);
      }
    } catch (err) {
      console.error('Failed to load feedback analytics:', err);
    }
  };

  const loadSubscribers = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedWebsite) params.append('website_source', selectedWebsite);
      params.append('limit', '50');
      
      const response = await api.get(`/analytics/subscribers?${params}`);
      if (response.data.success) {
        setSubscribers(response.data.subscribers);
      }
    } catch (err) {
      console.error('Failed to load subscribers:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await api.get('/analytics/campaign-history');
      if (response.data.success) {
        setCampaigns(response.data.campaigns);
      }
    } catch (err) {
      console.error('Failed to load campaigns:', err);
    }
  };

  const sendCampaign = async () => {
    if (!campaignForm.subject || !campaignForm.message) {
      setError('Subject and message are required');
      return;
    }

    setSendingCampaign(true);
    try {
      const response = await api.post('/analytics/send-campaign', campaignForm);
      if (response.data.success) {
        setCampaignResult(response.data);
        setCampaignForm({
          subject: '',
          message: '',
          html_message: '',
          website_source: '',
          filter: 'all'
        });
        loadCampaigns(); // Refresh campaign history
      }
    } catch (err) {
      console.error('Failed to send campaign:', err);
      setError('Failed to send campaign');
    } finally {
      setSendingCampaign(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  const sentimentData = feedbackAnalytics ? [
    { name: 'Positive', value: feedbackAnalytics.sentiment_breakdown.positive, color: '#00C49F' },
    { name: 'Neutral', value: feedbackAnalytics.sentiment_breakdown.neutral, color: '#FFBB28' },
    { name: 'Negative', value: feedbackAnalytics.sentiment_breakdown.negative, color: '#FF8042' }
  ] : [];

  const ratingData = feedbackAnalytics ? [
    { rating: '5⭐', count: feedbackAnalytics.rating_distribution['5'] },
    { rating: '4⭐', count: feedbackAnalytics.rating_distribution['4'] },
    { rating: '3⭐', count: feedbackAnalytics.rating_distribution['3'] },
    { rating: '2⭐', count: feedbackAnalytics.rating_distribution['2'] },
    { rating: '1⭐', count: feedbackAnalytics.rating_distribution['1'] }
  ] : [];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Website Analytics Dashboard</h1>
        <div className="flex gap-4">
          <Select value={selectedWebsite} onValueChange={setSelectedWebsite}>
            <SelectTrigger className="w-48">
              <SelectValue placeholder="All Websites" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Websites</SelectItem>
              {dashboardData?.website_sources.map((source) => (
                <SelectItem key={source._id} value={source._id}>
                  {source._id} ({source.count})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          
          <Select value={dateRange.toString()} onValueChange={(value) => setDateRange(parseInt(value))}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">7 days</SelectItem>
              <SelectItem value="30">30 days</SelectItem>
              <SelectItem value="90">90 days</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {error && (
        <Alert className="mb-6">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="feedback">Feedback Analysis</TabsTrigger>
          <TabsTrigger value="subscribers">Subscribers</TabsTrigger>
          <TabsTrigger value="campaigns">Email Campaigns</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {dashboardData && (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Subscribers</CardTitle>
                    <Users className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData.subscribers.total}</div>
                    <p className="text-xs text-muted-foreground">
                      +{dashboardData.subscribers.new_this_week} this week
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
                    <MessageSquare className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{dashboardData.feedback.total}</div>
                    <p className="text-xs text-muted-foreground">
                      +{dashboardData.feedback.new_this_week} this week
                    </p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Growth Rate</CardTitle>
                    <TrendingUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {dashboardData.subscribers.growth_rate.toFixed(1)}%
                    </div>
                    <p className="text-xs text-muted-foreground">Weekly growth</p>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium">Positive Sentiment</CardTitle>
                    <ThumbsUp className="h-4 w-4 text-muted-foreground" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {dashboardData.feedback.sentiment_summary.positive}
                    </div>
                    <p className="text-xs text-muted-foreground">Positive feedback</p>
                  </CardContent>
                </Card>
              </div>

              {/* Website Sources Chart */}
              <Card>
                <CardHeader>
                  <CardTitle>Website Sources</CardTitle>
                </CardHeader>
                <CardContent>
                  <SimpleBarChart 
                    data={dashboardData.website_sources} 
                    dataKey="count" 
                    xKey="_id" 
                  />
                </CardContent>
              </Card>

              {/* Recent Activity */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Registrations</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {dashboardData.recent_activity.map((activity, index) => (
                      <div key={index} className="flex items-center justify-between border-b pb-2">
                        <div>
                          <p className="font-medium">{activity.name || activity.email}</p>
                          <p className="text-sm text-muted-foreground">{activity.email}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">{activity.website_source}</p>
                          <p className="text-xs text-muted-foreground">
                            {new Date(activity.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="feedback" className="space-y-6">
          {feedbackAnalytics && (
            <>
              {/* Feedback Overview */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <Card>
                  <CardHeader>
                    <CardTitle>Sentiment Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <SimplePieChart data={sentimentData} />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Rating Distribution</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <SimpleBarChart 
                      data={ratingData} 
                      dataKey="count" 
                      xKey="rating" 
                    />
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle>Key Metrics</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Total Feedback</p>
                      <p className="text-2xl font-bold">{feedbackAnalytics.total_feedback}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Average Rating</p>
                      <p className="text-2xl font-bold">{feedbackAnalytics.avg_rating}⭐</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Sentiment Score</p>
                      <p className="text-2xl font-bold">{feedbackAnalytics.avg_sentiment_score}</p>
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Word Cloud */}
              <Card>
                <CardHeader>
                  <CardTitle>Top Words in Feedback</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex flex-wrap gap-2">
                    {feedbackAnalytics.word_cloud.map(([word, count], index) => (
                      <Badge key={index} variant="secondary" className="text-sm">
                        {word} ({count})
                      </Badge>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Recent Feedback */}
              <Card>
                <CardHeader>
                  <CardTitle>Recent Feedback</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {feedbackAnalytics.recent_feedback.map((feedback, index) => (
                      <div key={index} className="border-b pb-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <p className="text-sm">{feedback.feedback}</p>
                            <div className="flex items-center gap-2 mt-2">
                              {feedback.rating && (
                                <Badge variant="outline">{feedback.rating}⭐</Badge>
                              )}
                              <Badge 
                                variant={
                                  feedback.sentiment.label === 'positive' ? 'default' :
                                  feedback.sentiment.label === 'negative' ? 'destructive' : 'secondary'
                                }
                              >
                                {feedback.sentiment.label}
                              </Badge>
                            </div>
                          </div>
                          <div className="text-right text-sm text-muted-foreground">
                            <p>{feedback.name || 'Anonymous'}</p>
                            <p>{new Date(feedback.created_at).toLocaleDateString()}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </>
          )}
        </TabsContent>

        <TabsContent value="subscribers" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Subscribers ({subscribers.length})</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {subscribers.map((subscriber, index) => (
                  <div key={index} className="flex items-center justify-between border-b pb-2">
                    <div>
                      <p className="font-medium">{subscriber.name || 'No name'}</p>
                      <p className="text-sm text-muted-foreground">{subscriber.email}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">{subscriber.website_source}</p>
                      <p className="text-xs text-muted-foreground">
                        Joined: {new Date(subscriber.created_at).toLocaleDateString()}
                      </p>
                      {subscriber.newsletter_signup && (
                        <Badge variant="secondary" className="text-xs">Newsletter</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="campaigns" className="space-y-6">
          {/* Campaign Form */}
          <Card>
            <CardHeader>
              <CardTitle>Send Email Campaign</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="text-sm font-medium">Subject</label>
                <Input
                  value={campaignForm.subject}
                  onChange={(e) => setCampaignForm({...campaignForm, subject: e.target.value})}
                  placeholder="Campaign subject"
                />
              </div>
              
              <div>
                <label className="text-sm font-medium">Message</label>
                <Textarea
                  value={campaignForm.message}
                  onChange={(e) => setCampaignForm({...campaignForm, message: e.target.value})}
                  placeholder="Campaign message (use {{name}} for personalization)"
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Website Source</label>
                  <Select 
                    value={campaignForm.website_source} 
                    onValueChange={(value) => setCampaignForm({...campaignForm, website_source: value})}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="All websites" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="">All websites</SelectItem>
                      {dashboardData?.website_sources.map((source) => (
                        <SelectItem key={source._id} value={source._id}>
                          {source._id}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium">Filter</label>
                  <Select 
                    value={campaignForm.filter} 
                    onValueChange={(value) => setCampaignForm({...campaignForm, filter: value})}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All subscribers</SelectItem>
                      <SelectItem value="newsletter_only">Newsletter subscribers only</SelectItem>
                      <SelectItem value="active_only">Active subscribers only</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <Button 
                onClick={sendCampaign} 
                disabled={sendingCampaign}
                className="w-full"
              >
                <Send className="w-4 h-4 mr-2" />
                {sendingCampaign ? 'Sending...' : 'Send Campaign'}
              </Button>

              {campaignResult && (
                <Alert>
                  <AlertDescription>
                    Campaign sent successfully! 
                    Sent to {campaignResult.stats.sent_count} of {campaignResult.stats.total_subscribers} subscribers
                    ({campaignResult.stats.success_rate.toFixed(1)}% success rate)
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>

          {/* Campaign History */}
          <Card>
            <CardHeader>
              <CardTitle>Campaign History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {campaigns.map((campaign, index) => (
                  <div key={index} className="border-b pb-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <p className="font-medium">{campaign.subject}</p>
                        <p className="text-sm text-muted-foreground">{campaign.message.substring(0, 100)}...</p>
                        <div className="flex items-center gap-2 mt-2">
                          <Badge variant="outline">
                            {campaign.sent_count}/{campaign.total_subscribers} sent
                          </Badge>
                          {campaign.website_source && (
                            <Badge variant="secondary">{campaign.website_source}</Badge>
                          )}
                        </div>
                      </div>
                      <div className="text-right text-sm text-muted-foreground">
                        <p>{new Date(campaign.sent_at).toLocaleDateString()}</p>
                        <p>{((campaign.sent_count / campaign.total_subscribers) * 100).toFixed(1)}% success</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default WebsiteAnalytics;

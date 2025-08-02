import React, { useState, useEffect, useRef } from 'react';
import { 
  Send, 
  Bot, 
  User, 
  MessageCircle, 
  Lightbulb, 
  TrendingUp, 
  Users, 
  Package,
  BarChart3,
  Globe,
  DollarSign,
  Loader2,
  Sparkles
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Badge } from '../ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { ScrollArea } from '../ui/scroll-area';
import { useToast } from '../ui/use-toast';
import { api } from '../../services/api';

const AIChatbot = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef(null);
  const { toast } = useToast();

  const quickHelpTopics = [
    { id: 'marketing', label: 'Marketing', icon: TrendingUp, color: 'bg-blue-100 text-blue-800' },
    { id: 'customers', label: 'Customers', icon: Users, color: 'bg-green-100 text-green-800' },
    { id: 'products', label: 'Products', icon: Package, color: 'bg-purple-100 text-purple-800' },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, color: 'bg-orange-100 text-orange-800' },
    { id: 'website', label: 'Website', icon: Globe, color: 'bg-cyan-100 text-cyan-800' },
    { id: 'finance', label: 'Finance', icon: DollarSign, color: 'bg-yellow-100 text-yellow-800' }
  ];

  useEffect(() => {
    fetchConversations();
    fetchSuggestions();
    fetchAnalytics();
    
    // Auto-scroll to bottom when new messages arrive
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchConversations = async () => {
    try {
      const response = await api.get('/chatbot/conversations');
      if (response.data.success) {
        setConversations(response.data.conversations);
      }
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const fetchSuggestions = async () => {
    try {
      const response = await api.get('/chatbot/suggestions');
      if (response.data.success) {
        setSuggestions(response.data.suggestions.slice(0, 3)); // Top 3 suggestions
      }
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/chatbot/analytics');
      if (response.data.success) {
        setAnalytics(response.data.analytics);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = inputMessage.trim();
    setInputMessage('');
    
    // Add user message to chat
    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, newMessage]);
    setIsLoading(true);
    setIsTyping(true);

    try {
      const response = await api.post('/chatbot/chat', {
        message: userMessage,
        conversation_id: conversationId
      });

      if (response.data.success) {
        // Set conversation ID if this is a new conversation
        if (!conversationId && response.data.conversation_id) {
          setConversationId(response.data.conversation_id);
        }

        // Add bot response to chat
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: response.data.response,
          timestamp: new Date().toISOString(),
          analysis: response.data.analysis
        };

        setMessages(prev => [...prev, botMessage]);

        // Refresh conversations list
        fetchConversations();
      } else {
        throw new Error(response.data.error || 'Failed to get response');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive"
      });

      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'bot',
        content: "I apologize, but I'm having trouble processing your request right now. Please try again or contact support.",
        timestamp: new Date().toISOString(),
        isError: true
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setIsTyping(false);
    }
  };

  const handleQuickHelp = async (topic) => {
    setIsLoading(true);

    try {
      const response = await api.post('/chatbot/quick-help', { topic });

      if (response.data.success) {
        const helpMessage = {
          id: Date.now(),
          type: 'bot',
          content: response.data.response,
          timestamp: new Date().toISOString(),
          topic: topic,
          isQuickHelp: true
        };

        setMessages(prev => [...prev, helpMessage]);
      }
    } catch (error) {
      console.error('Error getting quick help:', error);
      toast({
        title: "Error",
        description: "Failed to get help information.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
  };

  const trainChatbot = async () => {
    try {
      const response = await api.post('/chatbot/train');
      if (response.data.success) {
        toast({
          title: "Success",
          description: `Chatbot trained successfully! ${response.data.insights_count} insights processed.`,
        });
        fetchAnalytics(); // Refresh analytics to show updated training status
      } else {
        throw new Error(response.data.error);
      }
    } catch (error) {
      console.error('Error training chatbot:', error);
      toast({
        title: "Error",
        description: "Failed to train chatbot. Please try again.",
        variant: "destructive"
      });
    }
  };

  const loadConversation = async (convId) => {
    try {
      const response = await api.get(`/chatbot/conversations/${convId}/messages`);
      if (response.data.success) {
        const formattedMessages = [];
        
        response.data.messages.forEach(msg => {
          // Add user message
          formattedMessages.push({
            id: `${msg.id}_user`,
            type: 'user',
            content: msg.user_message,
            timestamp: msg.created_at
          });
          
          // Add bot response
          formattedMessages.push({
            id: `${msg.id}_bot`,
            type: 'bot',
            content: msg.bot_response,
            timestamp: msg.created_at
          });
        });

        setMessages(formattedMessages);
        setConversationId(convId);
      }
    } catch (error) {
      console.error('Error loading conversation:', error);
      toast({
        title: "Error",
        description: "Failed to load conversation.",
        variant: "destructive"
      });
    }
  };

  const startNewConversation = () => {
    setMessages([]);
    setConversationId(null);
    
    // Add welcome message
    const welcomeMessage = {
      id: 'welcome',
      type: 'bot',
      content: "Hello! I'm your AI business assistant. I can help you with marketing strategies, customer management, product optimization, analytics insights, and much more. What would you like to discuss today?",
      timestamp: new Date().toISOString(),
      isWelcome: true
    };
    
    setMessages([welcomeMessage]);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for bot messages
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');
  };

  return (
    <div className="h-full flex flex-col bg-gray-50">
      <Tabs defaultValue="chat" className="h-full flex flex-col">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="chat" className="flex items-center gap-2">
            <MessageCircle className="h-4 w-4" />
            Chat
          </TabsTrigger>
          <TabsTrigger value="suggestions" className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4" />
            Suggestions
          </TabsTrigger>
          <TabsTrigger value="analytics" className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        <TabsContent value="chat" className="flex-1 flex gap-4 p-4">
          {/* Conversations Sidebar */}
          <Card className="w-80 flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">Conversations</CardTitle>
                <Button size="sm" onClick={startNewConversation}>
                  New Chat
                </Button>
              </div>
            </CardHeader>
            <CardContent className="flex-1 p-0">
              <ScrollArea className="h-96">
                {conversations.length > 0 ? (
                  <div className="p-4 space-y-2">
                    {conversations.map((conv) => (
                      <div
                        key={conv.id}
                        className={`p-3 rounded-lg cursor-pointer transition-colors ${
                          conversationId === conv.id
                            ? 'bg-blue-100 border-blue-300'
                            : 'bg-white hover:bg-gray-50 border-gray-200'
                        } border`}
                        onClick={() => loadConversation(conv.id)}
                      >
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium">
                            {new Date(conv.created_at).toLocaleDateString()}
                          </span>
                          <Badge variant="secondary" className="text-xs">
                            {conv.message_count}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600 truncate">
                          {conv.last_message_preview}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 text-center text-gray-500">
                    <MessageCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
                    <p className="text-sm">No conversations yet</p>
                    <p className="text-xs">Start chatting to begin!</p>
                  </div>
                )}
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Chat Area */}
          <Card className="flex-1 flex flex-col">
            <CardHeader className="pb-3">
              <div className="flex items-center gap-2">
                <Bot className="h-5 w-5 text-blue-600" />
                <CardTitle className="text-lg">AI Business Assistant</CardTitle>
                <Badge variant="outline" className="ml-auto">
                  <Sparkles className="h-3 w-3 mr-1" />
                  Powered by Gemini AI
                </Badge>
              </div>
            </CardHeader>

            {/* Quick Help Topics */}
            {messages.length <= 1 && (
              <div className="px-6 pb-4">
                <p className="text-sm text-gray-600 mb-3">Quick help topics:</p>
                <div className="flex flex-wrap gap-2">
                  {quickHelpTopics.map((topic) => {
                    const IconComponent = topic.icon;
                    return (
                      <Button
                        key={topic.id}
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickHelp(topic.id)}
                        disabled={isLoading}
                        className="flex items-center gap-2"
                      >
                        <IconComponent className="h-3 w-3" />
                        {topic.label}
                      </Button>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Messages */}
            <CardContent className="flex-1 flex flex-col p-0">
              <ScrollArea className="flex-1 px-6">
                <div className="space-y-4 py-4">
                  {messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex gap-3 ${
                        message.type === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {message.type === 'bot' && (
                        <div className="flex-shrink-0">
                          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                            message.isError ? 'bg-red-100' : 'bg-blue-100'
                          }`}>
                            <Bot className={`h-4 w-4 ${
                              message.isError ? 'text-red-600' : 'text-blue-600'
                            }`} />
                          </div>
                        </div>
                      )}
                      
                      <div
                        className={`max-w-[70%] p-3 rounded-lg ${
                          message.type === 'user'
                            ? 'bg-blue-600 text-white ml-auto'
                            : message.isError
                            ? 'bg-red-50 text-red-800 border border-red-200'
                            : 'bg-white border border-gray-200'
                        }`}
                      >
                        <div
                          className="text-sm whitespace-pre-wrap"
                          dangerouslySetInnerHTML={{
                            __html: formatMessage(message.content)
                          }}
                        />
                        <div className={`text-xs mt-2 ${
                          message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                        }`}>
                          {new Date(message.timestamp).toLocaleTimeString()}
                        </div>
                      </div>

                      {message.type === 'user' && (
                        <div className="flex-shrink-0">
                          <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
                            <User className="h-4 w-4 text-white" />
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                  
                  {isTyping && (
                    <div className="flex gap-3 justify-start">
                      <div className="flex-shrink-0">
                        <div className="w-8 h-8 rounded-full bg-blue-100 flex items-center justify-center">
                          <Bot className="h-4 w-4 text-blue-600" />
                        </div>
                      </div>
                      <div className="bg-white border border-gray-200 p-3 rounded-lg">
                        <div className="flex items-center gap-1">
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                        </div>
                      </div>
                    </div>
                  )}
                  
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              {/* Message Input */}
              <div className="p-4 border-t border-gray-200">
                <div className="flex gap-2">
                  <Input
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me anything about your business..."
                    disabled={isLoading}
                    className="flex-1"
                  />
                  <Button 
                    onClick={sendMessage}
                    disabled={isLoading || !inputMessage.trim()}
                    size="icon"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <Send className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="suggestions" className="flex-1 p-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">AI Business Suggestions</h2>
              <Button onClick={trainChatbot} variant="outline">
                <Sparkles className="h-4 w-4 mr-2" />
                Update Training
              </Button>
            </div>

            {suggestions.length > 0 ? (
              <div className="grid gap-4">
                {suggestions.map((suggestion, index) => (
                  <Card key={index}>
                    <CardContent className="p-6">
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="font-semibold text-lg">{suggestion.title}</h3>
                        <div className="flex gap-2">
                          <Badge 
                            variant={suggestion.priority === 'high' ? 'destructive' : 
                                   suggestion.priority === 'medium' ? 'default' : 'secondary'}
                          >
                            {suggestion.priority} priority
                          </Badge>
                          <Badge variant="outline">{suggestion.category}</Badge>
                        </div>
                      </div>
                      <p className="text-gray-600 mb-4">{suggestion.description}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <span>Effort: {suggestion.effort}</span>
                        <span>Impact: {suggestion.impact}</span>
                        <span>Timeline: {suggestion.timeline}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <Lightbulb className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-semibold mb-2">No suggestions yet</h3>
                  <p className="text-gray-600 mb-4">Train the AI with your business data to get personalized suggestions.</p>
                  <Button onClick={trainChatbot}>
                    <Sparkles className="h-4 w-4 mr-2" />
                    Train AI Assistant
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        <TabsContent value="analytics" className="flex-1 p-4">
          <div className="space-y-6">
            <h2 className="text-2xl font-bold">Chatbot Analytics</h2>

            {analytics ? (
              <>
                {/* Overview Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Total Conversations</p>
                          <p className="text-2xl font-bold">{analytics.total_conversations}</p>
                        </div>
                        <MessageCircle className="h-8 w-8 text-blue-600" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Total Messages</p>
                          <p className="text-2xl font-bold">{analytics.total_messages}</p>
                        </div>
                        <Send className="h-8 w-8 text-green-600" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Avg Messages/Chat</p>
                          <p className="text-2xl font-bold">{analytics.avg_messages_per_conversation}</p>
                        </div>
                        <BarChart3 className="h-8 w-8 text-purple-600" />
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardContent className="p-6">
                      <div className="flex items-center justify-between">
                        <div>
                          <p className="text-sm font-medium text-gray-600">Avg Duration</p>
                          <p className="text-2xl font-bold">{analytics.avg_conversation_duration_minutes}m</p>
                        </div>
                        <TrendingUp className="h-8 w-8 text-orange-600" />
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {/* Training Status */}
                <Card>
                  <CardHeader>
                    <CardTitle>AI Training Status</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span>Training Status:</span>
                        <Badge variant={analytics.training_status.insights_available ? "default" : "secondary"}>
                          {analytics.training_status.insights_available ? "Trained" : "Not Trained"}
                        </Badge>
                      </div>
                      
                      {analytics.training_status.last_trained && (
                        <div className="flex items-center justify-between">
                          <span>Last Training:</span>
                          <span className="text-sm text-gray-600">
                            {new Date(analytics.training_status.last_trained).toLocaleString()}
                          </span>
                        </div>
                      )}
                      
                      <div className="flex items-center justify-between">
                        <span>Common Concerns:</span>
                        <span className="text-sm">{analytics.training_status.common_concerns_count}</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span>FAQs Identified:</span>
                        <span className="text-sm">{analytics.training_status.faq_count}</span>
                      </div>
                      
                      <Button onClick={trainChatbot} className="w-full">
                        <Sparkles className="h-4 w-4 mr-2" />
                        Update Training Data
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="p-6 text-center">
                  <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                  <h3 className="text-lg font-semibold mb-2">No analytics data yet</h3>
                  <p className="text-gray-600">Start chatting with the AI assistant to see analytics.</p>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default AIChatbot;

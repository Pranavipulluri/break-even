# Mini-Website Data Collection System

## Overview

This system provides a comprehensive solution for creating mini-websites that collect user data and feedback, which then feeds back into the main Break-Even application for email marketing and analytics.

## Architecture

### 1. Mini-Website Creation
- **Template-based websites** with integrated data collection forms  
- **Netlify deployment** with serverless functions for backend logic
- **Data collection forms** for user registration and feedback
- **Real-time sentiment analysis** of customer feedback

### 2. Data Flow
```
Mini Website → Netlify Functions → MongoDB → Main Application → Analytics Dashboard
```

### 3. Components

#### A. Netlify Functions (`/netlify-functions/`)

**register-user.js**
- Handles user registration from mini-websites
- Email validation and duplicate checking
- Stores subscriber data with metadata
- Newsletter subscription management

**submit-feedback.js**
- Collects customer feedback with ratings
- Performs sentiment analysis (positive/negative/neutral)
- Calculates sentiment scores and confidence levels
- Stores feedback with analytics metadata

**mini-website-template.html**
- Responsive HTML template with integrated forms
- Modern UI with gradient backgrounds and animations
- Rating system with interactive stars
- Form validation and success/error messaging

#### B. Backend Routes (`/backend/app/routes/`)

**analytics.py - New Features**
```python
GET /analytics/subscribers          # Get paginated subscriber list
GET /analytics/feedback-analytics   # Get sentiment analysis and feedback metrics
POST /analytics/send-campaign       # Send email campaigns to subscribers
GET /analytics/campaign-history     # Get email campaign history
GET /analytics/dashboard-summary    # Get dashboard overview metrics
```

**ai_tools.py - New Endpoint**
```python
POST /ai-tools/dev/create-data-website  # Create data collection website
```

#### C. Frontend Components

**WebsiteAnalytics.jsx**
- Comprehensive analytics dashboard
- Subscriber management and filtering
- Feedback sentiment analysis with charts
- Email campaign management interface
- Word cloud visualization
- Performance metrics and KPIs

**WebsiteBuilder.jsx - Enhanced**
- New "Create Data Collection Site" button
- Integrated with data collection template
- Automatic deployment tracking

### 4. Database Collections

#### website_subscribers
```javascript
{
  _id: ObjectId,
  email: String,
  name: String,
  phone: String,
  website_source: String,
  business_id: ObjectId,
  newsletter_signup: Boolean,
  registration_count: Number,
  created_at: Date,
  last_updated: Date,
  active: Boolean,
  tags: [String],
  source_ip: String
}
```

#### website_feedback
```javascript
{
  _id: ObjectId,
  feedback: String,
  rating: Number (1-5),
  email: String,
  name: String,
  website_source: String,
  business_id: ObjectId,
  feedback_type: String,
  sentiment: {
    label: String, // positive/negative/neutral
    score: Number, // -1 to 1
    confidence: Number
  },
  metadata: {
    word_count: Number,
    character_count: Number,
    has_email: Boolean,
    has_rating: Boolean
  },
  created_at: Date,
  source_ip: String,
  processed: Boolean
}
```

#### email_campaigns
```javascript
{
  _id: ObjectId,
  subject: String,
  message: String,
  website_source: String,
  filter_used: String,
  total_subscribers: Number,
  sent_count: Number,
  failed_count: Number,
  failed_emails: [String],
  sent_by: ObjectId,
  sent_at: Date
}
```

## Features

### 1. User Registration System
- ✅ Email validation and duplicate prevention
- ✅ Newsletter subscription opt-in/out
- ✅ Phone number collection (optional)
- ✅ Source tracking for multi-website deployments
- ✅ IP address and user agent logging

### 2. Feedback Collection
- ✅ Multi-type feedback (general, suggestion, complaint, compliment)
- ✅ 5-star rating system with interactive UI
- ✅ Real-time sentiment analysis
- ✅ Anonymous and identified feedback support
- ✅ Automatic word frequency analysis

### 3. Analytics Dashboard
- ✅ Subscriber growth tracking and metrics
- ✅ Sentiment analysis with pie charts and bar graphs
- ✅ Rating distribution visualization
- ✅ Word cloud from feedback text
- ✅ Recent activity feeds
- ✅ Website source performance comparison

### 4. Email Marketing System
- ✅ Targeted email campaigns
- ✅ Subscriber filtering (all, newsletter only, active only)
- ✅ Message personalization with {{name}} variables
- ✅ HTML and plain text email support
- ✅ Campaign performance tracking
- ✅ Failed delivery logging

### 5. Website Deployment
- ✅ One-click data collection website creation
- ✅ Automatic Netlify deployment with functions
- ✅ Template customization with business information
- ✅ QR code integration for easy access
- ✅ Mobile-responsive design

## Usage

### Creating a Data Collection Website

1. **Frontend (WebsiteBuilder.jsx)**
```javascript
// Click "Create Data Collection Site" button
createDataCollectionWebsite() {
  // Sends website data to backend
  // Automatically deploys to Netlify
  // Returns live website URL
}
```

2. **Backend Processing**
- Template replacement with business info
- Netlify Functions deployment
- Database tracking of deployment
- URL generation and return

3. **Mini-Website Functions**
- Users visit deployed website
- Fill registration and feedback forms
- Data sent to Netlify Functions
- Functions save to MongoDB
- Real-time analytics updates

### Accessing Analytics

Visit `/website-analytics` in the main application to view:
- Subscriber list with pagination
- Feedback sentiment analysis  
- Email campaign management
- Performance metrics and growth rates

### Sending Email Campaigns

```javascript
// Campaign data structure
{
  subject: "Newsletter Title",
  message: "Hello {{name}}, welcome to our community!",
  html_message: "<h1>Welcome {{name}}!</h1>",
  website_source: "specific-website.netlify.app",
  filter: "newsletter_only" // or "all" or "active_only"
}
```

## Environment Variables

### Backend (.env)
```
MONGODB_URI=mongodb://localhost:27017/breakeven
NETLIFY_API_KEY=your_netlify_api_key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your_email@example.com  
EMAIL_PASSWORD=your_app_password
```

### Netlify Functions
```
MONGODB_URI=your_mongodb_connection_string
```

## API Endpoints

### Registration
```http
POST https://your-site.netlify.app/.netlify/functions/register-user
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com", 
  "phone": "+1234567890",
  "website_source": "my-site.netlify.app",
  "newsletter_signup": true
}
```

### Feedback Submission  
```http
POST https://your-site.netlify.app/.netlify/functions/submit-feedback
Content-Type: application/json

{
  "feedback": "Great service, very satisfied!",
  "rating": 5,
  "email": "john@example.com",
  "name": "John Doe", 
  "website_source": "my-site.netlify.app",
  "feedback_type": "compliment"
}
```

## Security Features

- ✅ CORS protection for cross-origin requests
- ✅ Input validation and sanitization
- ✅ Email format validation
- ✅ Rate limiting through Netlify Functions
- ✅ IP address logging for security auditing
- ✅ Authentication required for admin functions

## Development vs Production

### Development Mode
- Uses `/dev/` endpoints that bypass authentication
- Localhost testing supported
- Console logging enabled
- Detailed error messages

### Production Mode
- JWT authentication required
- Secure HTTPS endpoints only
- Error logging to database
- Production email configuration

## Next Steps

### Planned Enhancements
1. **Advanced Analytics**
   - Geographic distribution of users
   - Device and browser analytics
   - Conversion funnel tracking

2. **Enhanced Email Marketing**
   - Email templates with drag-and-drop editor
   - A/B testing for campaigns
   - Automated drip campaigns

3. **AI-Powered Insights**
   - Advanced sentiment analysis with AI models
   - Automated response suggestions
   - Predictive analytics for user behavior

4. **Integration Expansion**
   - Slack/Discord notifications
   - Zapier webhook integration
   - CRM system connections

## Support

For questions or issues with the data collection system:
1. Check the console logs in browser developer tools
2. Verify environment variables are set correctly
3. Test Netlify Functions deployment status
4. Check MongoDB connection and collections

This system provides a complete pipeline from mini-website visitor to analyzed customer data, enabling businesses to grow their email lists, understand customer sentiment, and run targeted marketing campaigns.

# 🚀 How to Run Break-Even Application & Generate Websites

## 📋 Prerequisites

Before starting, make sure you have:
- ✅ Node.js (v14 or higher)
- ✅ Python (v3.8 or higher)
- ✅ MongoDB running locally or connection string
- ✅ Netlify account (free)
- ✅ Gemini AI API key

---

## 🔧 Step 1: Environment Setup

### 1.1 Backend Environment Setup
```bash
# Navigate to your break-even project
cd "c:\Users\sreen\OneDrive\Documents\Python Scripts\break-even"

# Go to backend directory
cd backend

# Create virtual environment (if not exists)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt
```

### 1.2 Frontend Environment Setup
```bash
# Open new terminal and navigate to frontend
cd "c:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\frontend"

# Install Node.js dependencies
npm install
```

### 1.3 Environment Variables
Create `.env` file in the `backend` directory:
```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/break_even_db

# JWT Configuration
JWT_SECRET_KEY=your-secret-key-here

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1000

# Netlify Configuration
NETLIFY_API_KEY=your-netlify-api-key-here

# Email Configuration (Optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
```

---

## 🚀 Step 2: Run the Application

### 2.1 Start MongoDB
```bash
# Make sure MongoDB is running
# If using local MongoDB:
mongod

# Or use MongoDB Compass to start your local instance
```

### 2.2 Start Backend Server
```bash
# Open Command Prompt
# Navigate to backend directory
cd "c:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\backend"

# Activate virtual environment (if using one)
venv\Scripts\activate

# Start the backend server
python run.py

# You should see:
# ✅ Gemini AI initialized successfully
#  * Running on all addresses (0.0.0.0)
#  * Running on http://127.0.0.1:5000
#  * Running on http://[your-local-ip]:5000
```

### 2.3 Start Frontend Server
```bash
# Open NEW Command Prompt (keep backend running)
# Navigate to frontend directory
cd "c:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\frontend"

# Install dependencies (first time only)
npm install

# Start the frontend server on port 3001
npm run start:3001

# You should see:
# Local:            http://localhost:3001
# On Your Network:  http://192.168.x.x:3001
```

### 2.4 Alternative: Use Batch Files
```bash
# You can also use the provided batch files:

# Start backend:
cd "c:\Users\sreen\OneDrive\Documents\Python Scripts\break-even\backend"
start-backend.bat

# Start frontend:
cd "c:\Users\sreen\OneDrive\Documents\Python Scripts\break-even"
start-dev.bat
```

### 2.5 Verify Setup
Open your browser and go to:
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:5000/health

---

## 🌍 Step 3: Generate Websites

### 3.1 Using the Web Interface

1. **Access Website Builder**:
   - Go to http://localhost:3001
   - Register a new account or log in
   - Navigate to "Website Builder" or "AI Tools" section

2. **Create Data Collection Website**:
   ```
   Fill out the website creation form:
   - Website Name: "My Bakery Website"
   - Business Type: "Bakery" 
   - Business Area: "Downtown Chicago"
   - Description: "Fresh baked goods daily"
   - Color Theme: Choose your preferred theme
   - Contact Info: Your phone, email, address
   ```

3. **Deploy to Netlify**:
   - Click "Create Website" or "Create Data Collection Site"
   - Select "Netlify" as deployment platform
   - Wait for AI to generate content (Gemini AI will create personalized content)
   - Wait for deployment to complete
   - Get your live website URL: `https://your-site-name.netlify.app`

### 3.2 Using API Directly

You can also create websites using the API:

```javascript
// Example API call to create website
const response = await fetch('http://localhost:5000/api/ai-tools/dev/create-data-website', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: JSON.stringify({
    title: "My Amazing Business",
    description: "Join our community and share your feedback",
    content: "Welcome to our business! We'd love to hear from you.",
    business_id: "your-business-id"
  })
});

const result = await response.json();
console.log("Website URL:", result.website_url);
```

---

## 📊 Step 4: Access Your Generated Website

### 4.1 What You Get
Your generated website includes:
- ✅ **Registration Forms**: Collect customer emails
- ✅ **Feedback System**: 5-star ratings with sentiment analysis
- ✅ **Customer Portal**: Login/register functionality
- ✅ **Product Display**: Show your products
- ✅ **Newsletter Signup**: Email marketing integration
- ✅ **Modern UI**: Professional responsive design

### 4.2 Website Features
```
Your Website URL: https://your-site-name.netlify.app

Features Available:
├── 📝 Customer Registration
├── ⭐ Feedback & Reviews
├── 🛍️ Product Interest Forms
├── 📧 Newsletter Subscription
├── 👤 Customer Dashboard
├── 📱 Mobile Responsive
└── 🔒 Secure Authentication
```

### 4.3 Data Collection Points
```
Data Flows From Website To Your Database:
├── website_subscribers (Email registrations)
├── customer_feedback (Reviews & ratings)
├── newsletter_subscribers (Email marketing)
├── customers (Authenticated users)
├── website_analytics (Performance data)
└── product_interests (Customer preferences)
```

---

## 🎯 Step 5: Monitor & Manage

### 5.1 Check Collected Data
```bash
# Access MongoDB to see collected data
mongo break_even_db

# Check collections:
db.website_subscribers.find().pretty()
db.customer_feedback.find().pretty()
db.website_analytics.find().pretty()
```

### 5.2 View Analytics Dashboard
- Go to http://localhost:3000/analytics
- View subscriber growth
- Check feedback sentiment
- Monitor website performance

### 5.3 Send Email Campaigns
- Navigate to Analytics → Email Campaigns
- Create targeted campaigns
- Send to collected email addresses

---

## 🔧 Step 6: AI Chatbot Integration

### 6.1 Enable AI Assistant
```bash
# Run AI chatbot setup
cd backend
python setup_ai_chatbot.py
```

### 6.2 Use AI Features
- **Chat with AI**: Get business advice
- **Analyze Data**: AI insights on collected data
- **Smart Campaigns**: AI-generated email content
- **Predictive Analytics**: Customer behavior predictions

---

## 🚨 Troubleshooting

### Common Issues:

**1. Backend won't start:**
```bash
# Check if port 5000 is busy
netstat -an | findstr :5000

# Try different port
export FLASK_RUN_PORT=5001
python run.py
```

**2. Frontend won't connect:**
```bash
# Check backend is running on http://localhost:5000
curl http://localhost:5000/health

# If you see connection errors, check:
# 1. Backend is actually running
# 2. Windows Firewall isn't blocking port 5000
# 3. Update frontend API URL if needed (in src/services/api.js)

# Make sure you're using the correct frontend port:
# Frontend should be on: http://localhost:3001
# Backend should be on: http://localhost:5000
```

**3. MongoDB connection issues:**
```bash
# Check MongoDB is running
mongod --version

# Test connection
mongo --eval "db.runCommand('ping')"
```

**4. Netlify deployment fails:**
- Check Netlify API key in .env
- Verify account has deployment permissions
- Check site name isn't already taken

---

## 🎉 Success! You Now Have:

✅ **Running Break-Even Application**
✅ **AI-Powered Website Generator**
✅ **Data Collection System**
✅ **Customer Analytics Dashboard**
✅ **Email Marketing Platform**
✅ **AI Business Assistant**

Your websites will be live at URLs like:
- https://your-business-name.netlify.app
- Data flows automatically to your main application
- AI analyzes everything for business insights

---

## 📞 Next Steps

1. **Create your first website** using the web interface at http://localhost:3001
2. **Share the URL** with potential customers (like https://your-business.netlify.app)
3. **Monitor data collection** in your analytics dashboard  
4. **Use AI insights** to improve your business (via the AI Chatbot)
5. **Send targeted emails** to collected subscribers
6. **Check your Netlify account** to see deployed websites

**Your website generation system is now ready! 🚀**

## 🔗 Important URLs to Remember

- **Main Application**: http://localhost:3001
- **Backend API**: http://localhost:5000  
- **Generated Websites**: https://your-site-name.netlify.app
- **MongoDB**: mongodb://localhost:27017/break_even_db
- **Your Netlify Dashboard**: https://app.netlify.com

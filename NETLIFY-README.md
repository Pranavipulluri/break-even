# Break-Even Application - Netlify Deployment Guide

## Overview
This enhanced Break-Even application now includes sophisticated child websites with customer authentication, product listings, and comprehensive feedback collection systems.

## Features
- **Customer Authentication**: JWT-based login/register system
- **Product Integration**: Child websites display products from main website
- **Customer Feedback**: Rating system with sentiment analysis
- **Email Collection**: Newsletter and interest submissions
- **Modern UI**: Enhanced templates with professional design
- **Serverless Backend**: Netlify Functions for all backend operations

## Quick Setup

### Prerequisites
- Node.js (v18 or higher)
- MongoDB database (local or cloud)
- Netlify account

### Development Setup
1. Run the setup script:
   ```cmd
   setup-dev.bat
   ```

2. Update the `.env` file with your configuration:
   ```
   MONGODB_URI=your-mongodb-connection-string
   JWT_SECRET=your-secure-jwt-secret
   ```

3. Start development server:
   ```cmd
   netlify dev
   ```

### Production Deployment
1. Run the deployment script:
   ```cmd
   deploy-netlify.bat
   ```

2. Set environment variables in Netlify dashboard:
   - `MONGODB_URI`: Your MongoDB connection string
   - `JWT_SECRET`: Secure secret for JWT tokens

## Netlify Functions

### Customer Authentication
- `customer-login.js`: Customer login with JWT tokens
- `customer-register.js`: Customer registration with password hashing

### Data Collection
- `submit-interest.js`: Product interest submissions
- `submit-newsletter.js`: Newsletter signups
- `submit-feedback.js`: Customer feedback with ratings

### Public APIs
- `get-products.js`: Retrieve products for child websites
- `get-recent-feedback.js`: Display positive customer testimonials

## Enhanced Child Website Template

The `enhanced-mini-website-template.html` includes:
- **Customer Portal**: Login/register forms with JWT authentication
- **Product Showcase**: Dynamic product listings from main website
- **Feedback System**: Star ratings with detailed feedback forms
- **Interest Collection**: Product interest tracking
- **Newsletter Signup**: Email marketing integration
- **Modern UI**: Professional design with responsive layout

## Database Collections

### customers
```javascript
{
  _id: ObjectId,
  customer_name: String,
  email: String,
  password_hash: String,
  phone: String,
  created_at: Date,
  last_login: Date,
  is_active: Boolean
}
```

### customer_feedback
```javascript
{
  _id: ObjectId,
  business_id: ObjectId,
  customer_id: ObjectId,
  customer_name: String,
  email: String,
  rating: Number,
  feedback_message: String,
  feedback_category: String,
  sentiment: String,
  created_at: Date
}
```

### products (existing)
```javascript
{
  _id: ObjectId,
  business_id: ObjectId,
  name: String,
  description: String,
  price: Number,
  category: String,
  image_url: String,
  is_active: Boolean
}
```

## API Endpoints

### Authentication
- `POST /api/customer/customer-login`: Customer login
- `POST /api/customer/customer-register`: Customer registration

### Data Collection
- `POST /api/submit-interest`: Submit product interest
- `POST /api/submit-newsletter`: Newsletter signup
- `POST /api/submit-feedback`: Submit customer feedback

### Public APIs
- `GET /api/public/get-products?business_id=ID`: Get products
- `GET /api/public/get-recent-feedback?business_id=ID`: Get testimonials

## Security Features
- **Password Hashing**: bcrypt for secure password storage
- **JWT Tokens**: Secure customer authentication
- **Input Validation**: Comprehensive data validation
- **CORS Protection**: Proper cross-origin resource sharing
- **Rate Limiting**: Built-in request throttling

## Deployment Configuration

The `netlify.toml` file configures:
- Build settings for frontend
- Function directory mapping
- API redirects
- Security headers
- Environment variables

## Environment Variables

Set these in your Netlify dashboard:

```
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/break_even_db
JWT_SECRET=your-super-secure-secret-key-min-32-characters
NODE_ENV=production
```

## Child Website Access

Access child websites at:
```
https://your-netlify-app.netlify.app/child/BUSINESS_ID
```

Replace `BUSINESS_ID` with the actual MongoDB ObjectId of the business.

## Support

For issues or questions:
1. Check the Netlify function logs in your dashboard
2. Verify environment variables are set correctly
3. Ensure MongoDB connection is active
4. Test API endpoints individually

## Development Commands

```cmd
# Setup development environment
setup-dev.bat

# Start development server
netlify dev

# Deploy to staging
netlify deploy

# Deploy to production
netlify deploy --prod

# View function logs
netlify functions:log
```

## File Structure
```
break-even/
├── netlify.toml              # Netlify configuration
├── setup-dev.bat            # Development setup script
├── deploy-netlify.bat       # Deployment script
├── frontend/                 # React frontend
├── netlify-functions/        # Serverless functions
│   ├── customer-login.js
│   ├── customer-register.js
│   ├── submit-interest.js
│   ├── submit-newsletter.js
│   ├── submit-feedback.js
│   ├── get-products.js
│   └── get-recent-feedback.js
└── child_website_template/
    └── enhanced-mini-website-template.html
```

The enhanced Break-Even application is now ready for deployment with full customer engagement capabilities!

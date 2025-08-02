#!/usr/bin/env python3
"""
AI Chatbot Setup Script for Break-Even Application
Sets up the Gemini AI-powered chatbot system with training capabilities
"""

import os
import sys
import subprocess
import json
from datetime import datetime

def print_header(text):
    """Print formatted header"""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_step(step, text):
    """Print formatted step"""
    print(f"\n🔹 Step {step}: {text}")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_warning(text):
    """Print warning message"""
    print(f"⚠️  {text}")

def check_requirements():
    """Check if required packages are installed"""
    print_step(1, "Checking Python requirements...")
    
    required_packages = [
        'flask',
        'flask-jwt-extended',
        'pymongo',
        'google-generativeai',
        'requests',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print_success(f"{package} is installed")
        except ImportError:
            missing_packages.append(package)
            print_error(f"{package} is NOT installed")
    
    if missing_packages:
        print_warning("Missing packages found. Installing...")
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + missing_packages)
        print_success("All required packages installed!")
    
    return True

def setup_environment():
    """Setup environment variables"""
    print_step(2, "Setting up environment variables...")
    
    env_file = '.env'
    env_example = '.env.example'
    
    # Check if .env exists
    if not os.path.exists(env_file):
        if os.path.exists(env_example):
            # Copy from example
            with open(env_example, 'r') as f:
                env_content = f.read()
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print_success("Created .env file from template")
        else:
            # Create basic .env file
            env_content = """# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=break_even_db

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production

# Gemini AI Configuration
GEMINI_API_KEY=your-gemini-api-key-here
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1000

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-flask-secret-key

# Email Configuration (optional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Redis Configuration (optional for caching)
REDIS_URL=redis://localhost:6379

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
"""
            
            with open(env_file, 'w') as f:
                f.write(env_content)
            
            print_success("Created basic .env file")
    
    # Check for Gemini API key
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key or gemini_key == 'your-gemini-api-key-here':
        print_warning("Gemini API key not set!")
        print("Please:")
        print("1. Go to https://makersuite.google.com/app/apikey")
        print("2. Create a new API key")
        print("3. Update GEMINI_API_KEY in your .env file")
        return False
    else:
        print_success("Gemini API key is configured")
    
    return True

def test_gemini_connection():
    """Test Gemini AI connection"""
    print_step(3, "Testing Gemini AI connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print_error("Gemini API key not found in environment")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content("Say 'Hello! Gemini AI is working correctly for the Break-Even chatbot!'")
        
        if response and response.text:
            print_success("Gemini AI connection successful!")
            print(f"Response: {response.text}")
            return True
        else:
            print_error("Gemini AI connection failed - no response")
            return False
            
    except Exception as e:
        print_error(f"Gemini AI connection failed: {str(e)}")
        return False

def setup_database_collections():
    """Setup MongoDB collections for chatbot"""
    print_step(4, "Setting up database collections...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from pymongo import MongoClient
        
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        database_name = os.getenv('DATABASE_NAME', 'break_even_db')
        
        client = MongoClient(mongodb_uri)
        db = client[database_name]
        
        # Collections needed for chatbot
        collections = [
            'chatbot_conversations',
            'chatbot_messages',
            'chatbot_training',
            'ai_generations'
        ]
        
        existing_collections = db.list_collection_names()
        
        for collection_name in collections:
            if collection_name not in existing_collections:
                db.create_collection(collection_name)
                print_success(f"Created collection: {collection_name}")
            else:
                print_success(f"Collection exists: {collection_name}")
        
        # Create indexes for better performance
        indexes = [
            ('chatbot_conversations', [('user_id', 1), ('created_at', -1)]),
            ('chatbot_messages', [('conversation_id', 1), ('created_at', 1)]),
            ('chatbot_messages', [('user_id', 1), ('created_at', -1)]),
            ('chatbot_training', [('user_id', 1)]),
            ('ai_generations', [('user_id', 1), ('created_at', -1)])
        ]
        
        for collection_name, index_spec in indexes:
            try:
                db[collection_name].create_index(index_spec)
                print_success(f"Created index on {collection_name}")
            except Exception as e:
                print_warning(f"Index creation warning for {collection_name}: {str(e)}")
        
        client.close()
        print_success("Database setup completed!")
        return True
        
    except Exception as e:
        print_error(f"Database setup failed: {str(e)}")
        return False

def create_sample_training_data():
    """Create sample training data for the chatbot"""
    print_step(5, "Creating sample training data...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        from pymongo import MongoClient
        from bson import ObjectId
        
        mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        database_name = os.getenv('DATABASE_NAME', 'break_even_db')
        
        client = MongoClient(mongodb_uri)
        db = client[database_name]
        
        # Sample FAQ data
        sample_faqs = [
            "How can I improve my customer response time?",
            "What marketing strategies work best for small businesses?",
            "How do I optimize my product listings?",
            "What should I do if I receive negative feedback?",
            "How can I increase my QR code scans?",
            "What's the best way to collect customer emails?",
            "How do I analyze my business performance?",
            "What pricing strategy should I use?",
            "How can I improve customer satisfaction?",
            "What are the best social media practices?"
        ]
        
        # Sample business concerns
        sample_concerns = [
            "slow customer response times",
            "low website traffic",
            "poor conversion rates",
            "negative customer reviews",
            "inventory management issues",
            "pricing competition",
            "social media engagement",
            "email marketing effectiveness",
            "customer retention",
            "seasonal sales fluctuations"
        ]
        
        # Sample business strengths
        sample_strengths = [
            "excellent product quality",
            "responsive customer service",
            "competitive pricing",
            "strong local presence",
            "innovative products",
            "reliable delivery",
            "knowledgeable staff",
            "user-friendly website",
            "positive customer reviews",
            "strong brand reputation"
        ]
        
        # Sample improvement areas
        sample_improvements = [
            "improve website loading speed",
            "enhance product descriptions",
            "streamline checkout process",
            "expand social media presence",
            "implement customer loyalty program",
            "optimize search engine visibility",
            "improve customer support response time",
            "enhance mobile user experience",
            "expand payment options",
            "improve inventory tracking"
        ]
        
        # Create sample training record
        sample_training = {
            'user_id': ObjectId(),  # This would be replaced with actual user IDs
            'common_customer_concerns': sample_concerns,
            'frequently_asked_questions': sample_faqs,
            'business_strengths': sample_strengths,
            'improvement_areas': sample_improvements,
            'generated_at': datetime.utcnow(),
            'is_sample': True
        }
        
        # Insert sample data
        db.chatbot_training.insert_one(sample_training)
        
        client.close()
        print_success("Sample training data created!")
        return True
        
    except Exception as e:
        print_error(f"Sample data creation failed: {str(e)}")
        return False

def run_tests():
    """Run basic tests for the chatbot system"""
    print_step(6, "Running system tests...")
    
    try:
        # Test 1: Import all required modules
        print("Testing imports...")
        from app.services.chatbot_service import get_chatbot_service
        from app.services.gemini_service import get_gemini_service
        from app.routes.chatbot import chatbot_bp
        print_success("All imports successful")
        
        # Test 2: Initialize services
        print("Testing service initialization...")
        gemini_service = get_gemini_service()
        chatbot_service = get_chatbot_service()
        print_success("Services initialized successfully")
        
        # Test 3: Test Gemini API call
        print("Testing Gemini API...")
        result = gemini_service.generate_content("Test message for chatbot setup", max_tokens=50)
        if result.get('success'):
            print_success("Gemini API test successful")
        else:
            print_error(f"Gemini API test failed: {result.get('error')}")
            return False
        
        print_success("All tests passed!")
        return True
        
    except Exception as e:
        print_error(f"Tests failed: {str(e)}")
        return False

def create_documentation():
    """Create documentation for the chatbot system"""
    print_step(7, "Creating documentation...")
    
    docs_content = """# AI Chatbot System Documentation

## Overview
The AI Chatbot system provides intelligent business assistance using Google's Gemini AI. It can be trained on your business data to provide personalized recommendations and support.

## Features
- **Intelligent Conversations**: Natural language understanding and response
- **Business Context**: Trained on your business data and customer interactions
- **Personalized Suggestions**: AI-powered business recommendations
- **Analytics Tracking**: Conversation performance and user engagement metrics
- **Training System**: Self-improving based on customer feedback and interactions

## API Endpoints

### Chat Endpoints
- `POST /api/chatbot/chat` - Send message to AI assistant
- `GET /api/chatbot/conversations` - Get user's conversations
- `GET /api/chatbot/conversations/{id}/messages` - Get conversation messages
- `GET /api/chatbot/conversations/{id}/summary` - Get conversation summary

### Training & Analytics
- `POST /api/chatbot/train` - Train chatbot with business data
- `GET /api/chatbot/analytics` - Get chatbot usage analytics
- `GET /api/chatbot/suggestions` - Get AI business suggestions
- `POST /api/chatbot/quick-help` - Get quick help for topics

### Enhanced Analytics
- `GET /api/analytics/ai-insights` - AI-powered business insights
- `GET /api/analytics/chatbot-performance` - Chatbot performance metrics

## Usage Examples

### Basic Chat
```javascript
const response = await fetch('/api/chatbot/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    message: 'How can I improve my customer satisfaction?',
    conversation_id: null // or existing conversation ID
  })
});
```

### Train Chatbot
```javascript
const response = await fetch('/api/chatbot/train', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

### Get Business Suggestions
```javascript
const response = await fetch('/api/chatbot/suggestions', {
  headers: {
    'Authorization': 'Bearer ' + token
  }
});
```

## Configuration

### Environment Variables
```bash
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_MAX_TOKENS=1000
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=break_even_db
```

### Database Collections
- `chatbot_conversations` - Conversation records
- `chatbot_messages` - Individual messages
- `chatbot_training` - Training data and insights
- `ai_generations` - AI generation history

## Training Data Sources
The chatbot learns from:
1. Customer feedback and reviews
2. Customer messages and inquiries
3. Business performance data
4. Product information and analytics
5. User interaction patterns

## Best Practices
1. **Regular Training**: Update training data weekly for best results
2. **Context Awareness**: Provide business context in conversations
3. **Feedback Loop**: Use conversation analytics to improve responses
4. **Privacy**: Training data is anonymized and secure
5. **Monitoring**: Track chatbot performance and user satisfaction

## Troubleshooting

### Common Issues
1. **API Key Issues**: Ensure Gemini API key is valid and has quota
2. **Database Connection**: Check MongoDB connection and credentials
3. **Import Errors**: Verify all required packages are installed
4. **Training Failures**: Check data quality and format

### Performance Optimization
1. **Conversation Limits**: Keep conversation history manageable
2. **Token Management**: Optimize prompt length for API efficiency
3. **Caching**: Use Redis for frequently accessed data
4. **Indexing**: Ensure proper database indexes for queries

## Support
For issues or questions:
1. Check logs in `logs/app.log`
2. Verify environment configuration
3. Test API endpoints individually
4. Review conversation analytics for patterns

## Version History
- v1.0: Initial release with basic chat functionality
- v1.1: Added training system and business insights
- v1.2: Enhanced analytics and performance tracking
"""
    
    try:
        os.makedirs('docs', exist_ok=True)
        with open('docs/ai-chatbot-documentation.md', 'w') as f:
            f.write(docs_content)
        
        print_success("Documentation created at docs/ai-chatbot-documentation.md")
        return True
        
    except Exception as e:
        print_error(f"Documentation creation failed: {str(e)}")
        return False

def main():
    """Main setup function"""
    print_header("AI Chatbot Setup for Break-Even Application")
    print("This script will set up the Gemini AI-powered chatbot system")
    print("Make sure you have a Gemini API key from Google AI Studio")
    
    # Run setup steps
    steps = [
        ("Check Requirements", check_requirements),
        ("Setup Environment", setup_environment),
        ("Test Gemini Connection", test_gemini_connection),
        ("Setup Database", setup_database_collections),
        ("Create Sample Data", create_sample_training_data),
        ("Run Tests", run_tests),
        ("Create Documentation", create_documentation)
    ]
    
    success_count = 0
    total_steps = len(steps)
    
    for step_name, step_func in steps:
        try:
            if step_func():
                success_count += 1
            else:
                print_error(f"Step failed: {step_name}")
                break
        except Exception as e:
            print_error(f"Step error ({step_name}): {str(e)}")
            break
    
    # Final summary
    print_header("Setup Summary")
    
    if success_count == total_steps:
        print_success("🎉 AI Chatbot setup completed successfully!")
        print("\nNext steps:")
        print("1. Update your .env file with proper API keys")
        print("2. Start your Flask application")
        print("3. Access the chatbot at /api/chatbot/chat")
        print("4. Train the chatbot with: POST /api/chatbot/train")
        print("5. Check documentation at docs/ai-chatbot-documentation.md")
        
        print("\n📚 Key Features Available:")
        print("• Intelligent business conversations")
        print("• Personalized recommendations")
        print("• Customer feedback analysis")
        print("• Business performance insights")
        print("• Conversation analytics")
        print("• Self-training capabilities")
        
    else:
        print_error(f"Setup incomplete: {success_count}/{total_steps} steps completed")
        print("Please fix the issues above and run the setup again.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    main()

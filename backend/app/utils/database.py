from app import mongo
from datetime import datetime
from bson import ObjectId

def init_database():
    """Initialize database with indexes and default data"""
    try:
        # Create indexes for better performance
        
        # Users collection
        mongo.db.users.create_index("email", unique=True)
        mongo.db.users.create_index("created_at")
        
        # Products collection
        mongo.db.products.create_index([("user_id", 1), ("is_active", 1)])
        mongo.db.products.create_index("category")
        mongo.db.products.create_index("created_at")
        
        # Messages collection
        mongo.db.messages.create_index([("recipient_id", 1), ("created_at", -1)])
        mongo.db.messages.create_index("is_read")
        mongo.db.messages.create_index("customer_email")
        
        # Child customers collection
        mongo.db.child_customers.create_index([("business_owner_id", 1), ("email", 1)], unique=True)
        mongo.db.child_customers.create_index("created_at")
        mongo.db.child_customers.create_index("is_subscribed")
        
        # Child websites collection
        mongo.db.child_websites.create_index("owner_id", unique=True)
        mongo.db.child_websites.create_index("is_active")
        
        # Analytics collections
        mongo.db.website_analytics.create_index([("business_owner_id", 1), ("visited_at", -1)])
        mongo.db.website_analytics.create_index("website_id")
        mongo.db.website_analytics.create_index("visitor_ip")
        
        mongo.db.qr_analytics.create_index("user_id", unique=True)
        
        # AI collections
        mongo.db.ai_generations.create_index([("user_id", 1), ("created_at", -1)])
        mongo.db.ai_image_generations.create_index([("user_id", 1), ("created_at", -1)])
        mongo.db.ai_suggestions.create_index([("user_id", 1), ("created_at", -1)])
        
        # Feedback collection
        mongo.db.customer_feedback.create_index([("business_owner_id", 1), ("created_at", -1)])
        mongo.db.customer_feedback.create_index("rating")
        
        # Email campaigns
        mongo.db.email_campaigns.create_index([("business_owner_id", 1), ("created_at", -1)])
        mongo.db.email_logs.create_index([("campaign_id", 1), ("sent_at", -1)])
        
        print("Database initialized successfully with indexes")
        
    except Exception as e:
        print(f"Error initializing database: {e}")

def create_sample_data():
    """Create sample data for development/testing"""
    try:
        # Check if sample data already exists
        if mongo.db.users.find_one({"email": "demo@breakeven.com"}):
            print("Sample data already exists")
            return
        
        # Create sample user
        from werkzeug.security import generate_password_hash
        
        sample_user = {
            "email": "demo@breakeven.com",
            "password_hash": generate_password_hash("password123"),
            "name": "Demo User",
            "business_name": "Demo Business",
            "phone": "(555) 123-4567",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_active": True,
            "has_website": False
        }
        
        user_result = mongo.db.users.insert_one(sample_user)
        user_id = user_result.inserted_id
        
        # Create sample products
        sample_products = [
            {
                "name": "Premium Service Package",
                "description": "Our comprehensive service package including consultation, implementation, and support.",
                "price": 299.99,
                "stock": 10,
                "category": "professional",
                "user_id": user_id,
                "sku": "PSP-001",
                "image": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            },
            {
                "name": "Basic Consultation",
                "description": "One-hour consultation session to discuss your business needs.",
                "price": 99.99,
                "stock": 20,
                "category": "professional",
                "user_id": user_id,
                "sku": "BC-001",
                "image": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "is_active": True
            }
        ]
        
        mongo.db.products.insert_many(sample_products)
        
        # Create sample QR analytics
        qr_analytics = {
            "user_id": user_id,
            "website_url": f"http://localhost:3001/{user_id}",
            "total_scans": 15,
            "scans_today": 3,
            "last_scan": datetime.utcnow(),
            "created_at": datetime.utcnow()
        }
        
        mongo.db.qr_analytics.insert_one(qr_analytics)
        
        print("Sample data created successfully")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")

def cleanup_old_data():
    """Clean up old analytics and log data"""
    try:
        from datetime import timedelta
        
        # Remove analytics data older than 1 year
        cutoff_date = datetime.utcnow() - timedelta(days=365)
        
        mongo.db.website_analytics.delete_many({"visited_at": {"$lt": cutoff_date}})
        mongo.db.ai_generations.delete_many({"created_at": {"$lt": cutoff_date}})
        mongo.db.ai_image_generations.delete_many({"created_at": {"$lt": cutoff_date}})
        
        print("Old data cleanup completed")
        
    except Exception as e:
        print(f"Error during data cleanup: {e}")

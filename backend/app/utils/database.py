"""
Database initialization — indexes, seed data, and retention policies.

IMPORTANT — Atlas Vector Search:
    The vector index for `business_memory` CANNOT be created via PyMongo.
    It must be created in the Atlas UI or via the Atlas Admin API:

        Index Name : "vector_index"
        Collection : "business_memory"
        Field      : "vector"
        Type       : "vector"
        Dimensions : 768
        Similarity : "cosine"
        Filter     : ["business_id", "industry_type", "patch_outcome"]
"""

import logging
from datetime import datetime, timezone, timedelta
from app import mongo

logger = logging.getLogger(__name__)


def init_database():
    """Initialize database with indexes, seed data, and retention policies."""
    try:
        # ── Users ──
        mongo.db.users.create_index("email", unique=True)
        mongo.db.users.create_index("created_at")

        # ── Products ──
        mongo.db.products.create_index([("user_id", 1), ("is_active", 1)])
        mongo.db.products.create_index("category")
        mongo.db.products.create_index("created_at")

        # ── Messages ──
        mongo.db.messages.create_index([("recipient_id", 1), ("created_at", -1)])
        mongo.db.messages.create_index("is_read")
        mongo.db.messages.create_index("customer_email")

        # ── Child Customers ──
        mongo.db.child_customers.create_index(
            [("business_owner_id", 1), ("email", 1)], unique=True
        )
        mongo.db.child_customers.create_index("created_at")
        mongo.db.child_customers.create_index("is_subscribed")

        # ── Child Websites ──
        mongo.db.child_websites.create_index("owner_id", unique=True)
        mongo.db.child_websites.create_index("is_active")
        mongo.db.child_websites.create_index("industry_type")

        # ── Website Analytics ──
        mongo.db.website_analytics.create_index(
            [("business_owner_id", 1), ("visited_at", -1)]
        )
        mongo.db.website_analytics.create_index("website_id")
        mongo.db.website_analytics.create_index("visitor_ip")

        # ── QR Analytics ──
        # NOT unique — allows time-series scan data per user
        mongo.db.qr_analytics.create_index([("user_id", 1), ("scanned_at", -1)])

        # ── AI Collections ──
        mongo.db.ai_generations.create_index([("user_id", 1), ("created_at", -1)])
        mongo.db.ai_image_generations.create_index([("user_id", 1), ("created_at", -1)])
        mongo.db.ai_suggestions.create_index([("user_id", 1), ("created_at", -1)])

        # ── MCP & Copilot ──
        mongo.db.website_schemas.create_index([("business_id", 1), ("is_active", 1)])
        mongo.db.website_history.create_index([("business_id", 1), ("timestamp", -1)])
        mongo.db.website_history.create_index([("business_id", 1), ("schema_version", -1)])
        mongo.db.business_memory.create_index("business_id")
        mongo.db.business_memory.create_index(
            [("industry_type", 1), ("patch_outcome", 1)]
        )
        mongo.db.pending_patches.create_index([("business_id", 1), ("is_applied", 1)])
        # TTL — expire unapplied patches after 24 hours
        mongo.db.pending_patches.create_index(
            "created_at", expireAfterSeconds=86400
        )

        # ── Analytics Events (Event Collector) ──
        mongo.db.analytics_events.create_index(
            [("business_id", 1), ("event_type", 1), ("timestamp", -1)]
        )
        mongo.db.analytics_events.create_index(
            [("business_id", 1), ("timestamp", -1)]
        )

        # ── Industry Benchmark Patterns ──
        mongo.db.industry_benchmark_patterns.create_index("industry")
        mongo.db.industry_benchmark_patterns.create_index(
            [("industry", 1), ("pattern_name", 1)], unique=True
        )

        # ── Translation Cache ──
        mongo.db.translation_cache.create_index(
            [("source_lang", 1), ("target_lang", 1), ("source_text", 1)], unique=True
        )
        # TTL — expire cached translations after 30 days
        mongo.db.translation_cache.create_index(
            "created_at", expireAfterSeconds=2592000
        )

        # ── Feedback ──
        mongo.db.customer_feedback.create_index(
            [("business_owner_id", 1), ("created_at", -1)]
        )
        mongo.db.customer_feedback.create_index("rating")

        # ── Email Campaigns ──
        mongo.db.email_campaigns.create_index(
            [("business_owner_id", 1), ("created_at", -1)]
        )
        mongo.db.email_logs.create_index([("campaign_id", 1), ("sent_at", -1)])

        logger.info("Database initialized successfully with indexes")

        # Seed industry benchmarks if empty
        _seed_industry_benchmarks_if_empty()

    except Exception as e:
        logger.error(f"Error initializing database: {e}")


# ====================================================================
# Industry Benchmark Seeding
# ====================================================================

def _seed_industry_benchmarks_if_empty():
    """Seed industry benchmark patterns for cold-start intelligence."""
    try:
        if mongo.db.industry_benchmark_patterns.count_documents({}) > 0:
            logger.info("Industry benchmarks already seeded — skipping.")
            return

        from app.services.industry_benchmarks import seed_benchmarks
        seed_benchmarks()
    except Exception as e:
        logger.warning(f"Could not seed industry benchmarks: {e}")


# ====================================================================
# Sample / Demo Data
# ====================================================================

def create_sample_data():
    """Create sample data for development/testing — includes MCP demo data."""
    try:
        if mongo.db.users.find_one({"email": "demo@breakeven.com"}):
            logger.info("Sample data already exists")
            return

        from werkzeug.security import generate_password_hash

        now = datetime.now(timezone.utc)

        sample_user = {
            "email": "demo@breakeven.com",
            "password_hash": generate_password_hash("password123"),
            "name": "Demo User",
            "business_name": "Demo Business",
            "phone": "(555) 123-4567",
            "created_at": now,
            "updated_at": now,
            "is_active": True,
            "has_website": False,
        }
        user_result = mongo.db.users.insert_one(sample_user)
        user_id = str(user_result.inserted_id)

        # Sample products
        sample_products = [
            {
                "name": "Premium Service Package",
                "description": "Our comprehensive service package including consultation, implementation, and support.",
                "price": 299.99,
                "stock": 10,
                "category": "professional",
                "user_id": user_result.inserted_id,
                "sku": "PSP-001",
                "image": None,
                "created_at": now,
                "updated_at": now,
                "is_active": True,
            },
            {
                "name": "Basic Consultation",
                "description": "One-hour consultation session to discuss your business needs.",
                "price": 99.99,
                "stock": 20,
                "category": "professional",
                "user_id": user_result.inserted_id,
                "sku": "BC-001",
                "image": None,
                "created_at": now,
                "updated_at": now,
                "is_active": True,
            },
        ]
        mongo.db.products.insert_many(sample_products)

        # Sample QR analytics (non-unique now)
        qr_analytics = {
            "user_id": user_result.inserted_id,
            "website_url": f"http://localhost:3001/{user_id}",
            "total_scans": 15,
            "scans_today": 3,
            "last_scan": now,
            "scanned_at": now,
            "created_at": now,
        }
        mongo.db.qr_analytics.insert_one(qr_analytics)

        # ── MCP Demo Data ──

        # Seed a default website schema so the Copilot drawer has something to demo
        from app.services.patch_engine import PatchEngine
        demo_schema = PatchEngine.create_default_schema(user_id)
        mongo.db.website_schemas.insert_one(demo_schema)

        # Seed one positive optimization memory
        from app.services.business_memory import BusinessMemory
        BusinessMemory.add_memory(
            business_id=user_id,
            patch_name="hero_cta_above_fold",
            reason="A/B test showed CTA visibility above fold increases bookings",
            layout_used="hero-split with prominent CTA button",
            metrics_before=4.2,
            metrics_after=7.8,
            conversion_gain=3.6,
            agent_name="BusinessCopilot",
            patch_outcome="success",
            industry_type="spa",
        )

        # Seed one failure memory so the failure gate has something to compare
        BusinessMemory.add_failure_memory(
            business_id=user_id,
            patch_name="footer_cta_experiment",
            reason="Hypothesized that adding a secondary CTA in footer would improve conversions",
            error_detail="Footer CTA caused layout shift on mobile breakpoints; conversion dropped 2.1%",
        )

        # Additional diverse memories for realistic RAG ranking tests
        BusinessMemory.add_memory(
            business_id=user_id,
            patch_name="testimonials_social_proof",
            reason="Adding client testimonials below hero section to build trust",
            layout_used="testimonials-grid variant with star ratings and avatars",
            metrics_before=5.0,
            metrics_after=6.8,
            conversion_gain=1.8,
            agent_name="BusinessCopilot",
            patch_outcome="success",
            industry_type="spa",
        )

        BusinessMemory.add_memory(
            business_id=user_id,
            patch_name="price_list_transparency",
            reason="Visible pricing reduces bounce rate by removing uncertainty",
            layout_used="pricing-card-grid layout with monthly/yearly toggle",
            metrics_before=4.8,
            metrics_after=7.3,
            conversion_gain=2.5,
            agent_name="BusinessCopilot",
            patch_outcome="success",
            industry_type="spa",
        )

        BusinessMemory.add_memory(
            business_id=user_id,
            patch_name="reservation_widget_placement",
            reason="Moving inline reservation widget above gallery section",
            layout_used="reservation-inline with date picker and service selector",
            metrics_before=6.1,
            metrics_after=8.8,
            conversion_gain=2.7,
            agent_name="BusinessCopilot",
            patch_outcome="success",
            industry_type="spa",
        )

        BusinessMemory.add_memory(
            business_id=user_id,
            patch_name="contact_button_sticky",
            reason="Adding a sticky contact button on mobile viewports",
            layout_used="sticky-bottom-bar with phone icon and WhatsApp link",
            metrics_before=5.5,
            metrics_after=6.9,
            conversion_gain=1.4,
            agent_name="BusinessCopilot",
            patch_outcome="success",
            industry_type="general",
        )

        logger.info("Sample data created successfully (including MCP demo data with 6 memory records)")

    except Exception as e:
        logger.error(f"Error creating sample data: {e}")


# ====================================================================
# Retention / Cleanup
# ====================================================================

def cleanup_old_data():
    """Clean up old analytics, log data, and unbounded memory collections."""
    try:
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=365)

        # Analytics & AI logs — older than 1 year
        mongo.db.website_analytics.delete_many({"visited_at": {"$lt": cutoff_date}})
        mongo.db.ai_generations.delete_many({"created_at": {"$lt": cutoff_date}})
        mongo.db.ai_image_generations.delete_many({"created_at": {"$lt": cutoff_date}})

        # Business memory — keep only the last 200 memories per business
        pipeline = [
            {"$group": {"_id": "$business_id", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 200}}},
        ]
        for group in mongo.db.business_memory.aggregate(pipeline):
            bid = group["_id"]
            keep_ids = [
                doc["_id"]
                for doc in mongo.db.business_memory.find(
                    {"business_id": bid}, {"_id": 1}
                ).sort("created_at", -1).limit(200)
            ]
            if keep_ids:
                mongo.db.business_memory.delete_many(
                    {"business_id": bid, "_id": {"$nin": keep_ids}}
                )

        # Website history — keep only the last 50 versions per business
        pipeline_hist = [
            {"$group": {"_id": "$business_id", "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 50}}},
        ]
        for group in mongo.db.website_history.aggregate(pipeline_hist):
            bid = group["_id"]
            keep_ids = [
                doc["_id"]
                for doc in mongo.db.website_history.find(
                    {"business_id": bid}, {"_id": 1}
                ).sort("timestamp", -1).limit(50)
            ]
            if keep_ids:
                mongo.db.website_history.delete_many(
                    {"business_id": bid, "_id": {"$nin": keep_ids}}
                )

        logger.info("Old data cleanup completed (analytics, memory, history)")

    except Exception as e:
        logger.error(f"Error during data cleanup: {e}")

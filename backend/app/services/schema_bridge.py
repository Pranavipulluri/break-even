"""
SchemaBridge — Converts deployed website data into website_schemas records.

This service bridges the gap between website creation (which deploys raw HTML
to Netlify/GitHub) and the AI Copilot optimization system (which reads/writes
JSON schemas in the website_schemas collection).

After a website is deployed, call create_schema_from_deployment() to:
    1. Generate a structured JSON schema from business_info
    2. Insert it into website_schemas (enabling Copilot optimization)
    3. Upsert child_websites with netlify_site_id (enabling PatchEngine re-deploy)
    4. Generate an API key for child→parent event tracking
"""

import logging
import secrets
from datetime import datetime, timezone
from app import mongo

logger = logging.getLogger(__name__)


# ====================================================================
# Color Theme Mapping — frontend themes → SchemaRenderer palettes
# ====================================================================

THEME_MAP = {
    # Blues
    "blue": "royal-navy",
    "modern": "royal-navy",
    "corporate": "royal-navy",
    "tech": "royal-navy",
    "futuristic": "royal-navy",
    "business": "royal-navy",
    # Greens
    "green": "emerald-gold",
    "fresh": "emerald-gold",
    "trust": "emerald-gold",
    # Purples / Elegance
    "elegant": "lavender-luxury",
    "soft": "lavender-luxury",
    "luxurious": "lavender-luxury",
    # Warm / Bold
    "warm": "rose-gold-luxury",
    "bold": "rose-gold-luxury",
    "friendly": "rose-gold-luxury",
    "classic": "rose-gold-luxury",
    # Neutral
    "neutral": "spa-serenity",
    "minimal": "spa-serenity",
}

DEFAULT_PALETTE = "spa-serenity"


class SchemaBridge:
    """Bridges website creation → schema system → Copilot optimization."""

    # ================================================================
    # Core: Build a schema dict from business data
    # ================================================================

    @classmethod
    def build_schema_dict(cls, business_id, business_info):
        """
        Pure function: converts business data into a website_schemas-compatible dict.

        Args:
            business_id: Owner's user/business ID.
            business_info: Dict with keys like website_name, business_type,
                          description, services_products, area, phone, email,
                          hero_title, hero_subtitle, about_us, contact_cta,
                          color_theme, unique_selling_points, etc.

        Returns:
            A dict ready for insertion into the website_schemas collection.
        """
        if not isinstance(business_info, dict):
            business_info = {}

        b_id_str = str(business_id)
        now = datetime.now(timezone.utc)

        # ── Extract fields with safe defaults ──
        biz_name = business_info.get("website_name") or business_info.get("site_name") or "My Business"
        biz_type = business_info.get("business_type") or "general"
        description = business_info.get("description") or business_info.get("about_us") or ""
        area = business_info.get("area") or business_info.get("location") or ""

        hero_title = business_info.get("hero_title") or biz_name
        hero_subtitle = business_info.get("hero_subtitle") or description or f"Welcome to {biz_name}"
        cta_text = business_info.get("contact_cta") or business_info.get("cta") or "Get Started"

        phone = business_info.get("phone") or ""
        email = business_info.get("email") or ""
        address = business_info.get("address") or area

        # ── Color theme ──
        raw_theme = str(business_info.get("color_theme") or business_info.get("theme") or "").lower().strip()
        palette = THEME_MAP.get(raw_theme, DEFAULT_PALETTE)

        # ── Build sections ──
        sections = []

        # 1. Hero section
        sections.append({
            "id": "hero_1",
            "type": "hero",
            "variant": "hero-split",
            "content": {
                "title": hero_title,
                "subtitle": hero_subtitle,
                "cta": cta_text,
                "image": cls._get_hero_image(biz_type),
            },
        })

        # 2. Services section (if services provided)
        services_raw = business_info.get("services_products") or business_info.get("services") or []
        if isinstance(services_raw, str):
            # Split comma-separated string
            services_raw = [s.strip() for s in services_raw.split(",") if s.strip()]

        if services_raw:
            service_items = []
            icons = ["fas fa-star", "fas fa-gem", "fas fa-hands", "fas fa-spa",
                     "fas fa-briefcase", "fas fa-heart", "fas fa-bolt", "fas fa-leaf"]
            for idx, svc in enumerate(services_raw[:6]):
                if isinstance(svc, dict):
                    service_items.append({
                        "name": svc.get("name", f"Service {idx+1}"),
                        "price": svc.get("price", ""),
                        "description": svc.get("description", ""),
                        "icon": svc.get("icon", icons[idx % len(icons)]),
                    })
                else:
                    service_items.append({
                        "name": str(svc),
                        "price": "",
                        "description": "",
                        "icon": icons[idx % len(icons)],
                    })

            sections.append({
                "id": "services_1",
                "type": "services",
                "variant": "services-grid",
                "content": {
                    "title": f"Our Services",
                    "items": service_items,
                },
            })

        # 3. CTA / USP section (if unique selling points provided)
        usps = business_info.get("unique_selling_points") or business_info.get("usps") or []
        if isinstance(usps, str):
            usps = [u.strip() for u in usps.split(",") if u.strip()]
        if usps:
            sections.append({
                "id": "cta_1",
                "type": "cta",
                "variant": "cta-banner",
                "content": {
                    "title": "Why Choose Us",
                    "subtitle": " | ".join(usps[:4]),
                    "cta": cta_text,
                },
            })

        # 4. Testimonials section (placeholder — populated by feedback later)
        sections.append({
            "id": "testimonials_1",
            "type": "testimonials",
            "variant": "testimonials-grid",
            "content": {
                "title": "What Our Clients Say",
                "items": [
                    {"name": "Happy Customer", "role": "Client",
                     "quote": "Excellent service and outstanding quality. Highly recommended!"},
                ],
            },
        })

        # 5. Booking section
        sections.append({
            "id": "booking_1",
            "type": "booking",
            "variant": "booking-embedded",
            "content": {
                "title": "Book an Appointment",
                "business_id": b_id_str,
                "services": [s.get("name", str(s)) if isinstance(s, dict) else str(s)
                             for s in (services_raw or ["Consultation"])[:5]],
            },
        })

        # 6. Contact section
        sections.append({
            "id": "contact_1",
            "type": "contact",
            "variant": "contact-split",
            "content": {
                "title": f"Contact {biz_name}",
                "business_id": b_id_str,
                "address": address,
                "phone": phone,
                "email": email,
            },
        })

        # 7. Footer
        sections.append({
            "id": "footer_1",
            "type": "footer",
            "variant": "footer-standard",
            "content": {},
        })

        # ── Assemble full schema ──
        schema = {
            "business_id": b_id_str,
            "schema_version": 1,
            "version": 1.0,
            "active_version": True,
            "deployment_id": None,
            "industry_type": biz_type,
            "theme": {
                "palette": palette,
                "font": "Inter",
            },
            "seo": {
                "title": biz_name,
                "description": description or f"{biz_name} — {biz_type} in {area}".strip(" —"),
                "keywords": f"{biz_type}, {biz_name}, {area}, booking, services".strip(", "),
            },
            "sections": sections,
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

        return schema

    # ================================================================
    # Persist: Create schema + link deployment info
    # ================================================================

    @classmethod
    def create_schema_from_deployment(cls, business_id, business_info,
                                      deploy_result, platform="netlify"):
        """
        After a website is deployed, creates the matching schema record
        and links deployment metadata for future re-deploys.

        Args:
            business_id: Owner's user/business ID.
            business_info: Dict of business data used to generate the website.
            deploy_result: Dict returned by NetlifyService or GitHubService
                          (contains website_url, site.id, etc.).
            platform: "netlify" or "github".

        Returns:
            The inserted/updated schema dict.
        """
        try:
            b_id_str = str(business_id)

            # 1. Build the schema
            schema = cls.build_schema_dict(b_id_str, business_info)

            # 2. Check if schema already exists for this business
            existing = mongo.db.website_schemas.find_one(
                {"business_id": b_id_str, "is_active": True}
            )

            if existing:
                # Update the existing schema with new deployment info
                mongo.db.website_schemas.update_one(
                    {"_id": existing["_id"]},
                    {"$set": {
                        "deployment_id": deploy_result.get("deploy", {}).get("id"),
                        "updated_at": datetime.now(timezone.utc),
                    }}
                )
                schema = existing
                logger.info(f"Updated existing schema for business {b_id_str}")
            else:
                # Insert new schema
                schema["deployment_id"] = deploy_result.get("deploy", {}).get("id")
                mongo.db.website_schemas.insert_one(schema)
                logger.info(f"✅ Created website_schema for business {b_id_str}")

            # 3. Extract deployment identifiers
            netlify_site_id = None
            website_url = deploy_result.get("website_url") or deploy_result.get("ssl_url", "")

            if platform == "netlify":
                site_info = deploy_result.get("site", {})
                netlify_site_id = site_info.get("id")
            elif platform == "github":
                website_url = deploy_result.get("website_url", "")

            # 4. Generate API key for child→parent event tracking
            api_key = f"be_{secrets.token_urlsafe(32)}"

            # 5. Upsert child_websites record
            child_update = {
                "owner_id": b_id_str,
                "website_name": business_info.get("website_name") or business_info.get("site_name", ""),
                "business_type": business_info.get("business_type", "general"),
                "website_url": website_url,
                "platform": platform,
                "api_key": api_key,
                "updated_at": datetime.now(timezone.utc),
            }

            if netlify_site_id:
                child_update["netlify_site_id"] = netlify_site_id

            mongo.db.child_websites.update_one(
                {"owner_id": b_id_str},
                {"$set": child_update,
                 "$setOnInsert": {"created_at": datetime.now(timezone.utc)}},
                upsert=True,
            )

            logger.info(
                f"✅ SchemaBridge complete: business={b_id_str}, "
                f"platform={platform}, url={website_url}, "
                f"netlify_site_id={netlify_site_id}"
            )

            return schema

        except Exception as e:
            logger.error(f"❌ SchemaBridge error for business {business_id}: {e}")
            return None

    # ================================================================
    # Helpers
    # ================================================================

    @staticmethod
    def _get_hero_image(business_type):
        """Returns an appropriate Unsplash hero image URL based on business type."""
        type_images = {
            "spa": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?auto=format&fit=crop&w=1200&q=80",
            "beauty": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1200&q=80",
            "salon": "https://images.unsplash.com/photo-1560066984-138dadb4c035?auto=format&fit=crop&w=1200&q=80",
            "restaurant": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80",
            "food": "https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=1200&q=80",
            "bakery": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=1200&q=80",
            "law": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80",
            "legal": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&w=1200&q=80",
            "fashion": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?auto=format&fit=crop&w=1200&q=80",
            "tech": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=1200&q=80",
            "fitness": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1200&q=80",
            "gym": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=1200&q=80",
        }
        biz_lower = str(business_type).lower()
        for key, url in type_images.items():
            if key in biz_lower:
                return url
        # Default professional image
        return "https://images.unsplash.com/photo-1497366216548-37526070297c?auto=format&fit=crop&w=1200&q=80"

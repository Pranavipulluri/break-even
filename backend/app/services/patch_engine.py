"""
PatchEngine — Controlled Website Evolution System.

CRITICAL RULE: AI should NEVER rewrite the full schema.
Only surgical, section-specific patches are allowed.

Supported patch actions:
    ✅ update_section      — Modify content/variant of an existing section
    ✅ swap_variant        — Change a section's layout variant
    ✅ move_section        — Relocate a section to a new position
    ✅ update_content      — Merge new content fields into a section
    ✅ reorder_sections    — Full reorder by ID list
    ✅ update_theme        — Modify color palette / font
    ✅ update_seo          — Modify title / description / keywords
    ✅ add_section         — Insert a new section
    ✅ delete_section      — Remove a section by ID

Each patch stores:
    before_metrics, expected_impact, trigger_reason, agent_name, confidence_score
    for optimization intelligence memory.
"""

import os
import logging
from datetime import datetime, timezone
from bson import ObjectId
from app import mongo
from app.services.patch_validator import PatchValidator
from app.services.schema_renderer import SchemaRenderer

logger = logging.getLogger(__name__)


class PatchEngine:

    # ================================================================
    # Schema retrieval
    # ================================================================

    @classmethod
    def get_active_schema(cls, business_id):
        """
        Retrieves the active website schema for a business.
        If none exists, creates a premium default and persists it.
        """
        b_id_str = str(business_id)
        schema_doc = mongo.db.website_schemas.find_one(
            {"business_id": b_id_str, "is_active": True}
        )

        if not schema_doc:
            schema_doc = cls.create_default_schema(b_id_str)
            mongo.db.website_schemas.insert_one(schema_doc)

        return schema_doc

    # ================================================================
    # Core patch application
    # ================================================================

    @classmethod
    def apply_patch(cls, business_id, patch, patch_metadata=None):
        """
        Applies a validated JSON patch to the active website schema.

        Flow:
            1. Validate patch
            2. Archive snapshot (for rollbacks)
            3. Apply surgical changes
            4. Increment schema_version
            5. Render HTML & write to disk
            6. Update child_websites collection

        Returns (success, updated_schema, error_message).
        """
        try:
            b_id_str = str(business_id)
            active_schema = cls.get_active_schema(b_id_str)
            active_schema.pop("_id", None)

            # 1. Validate
            is_valid, err_msg = PatchValidator.validate_patch(active_schema, patch)
            if not is_valid:
                return False, None, err_msg

            # 2. Archive snapshot for rollback
            current_version = active_schema.get("schema_version", active_schema.get("version", 1))

            default_metadata = {
                "patch_name": patch.get("action", "general_patch"),
                "trigger_reason": "AI continuous optimization",
                "agent_name": "BusinessCopilot",
                "affected_section": patch.get("section_id", "global"),
                "expected_impact": "+15% engagement",
                "confidence_score": 85,
                "before_metrics": {},
            }
            meta = {**default_metadata, **(patch_metadata or {})}

            history_record = {
                "business_id": b_id_str,
                "schema_version": current_version,
                "schema_snapshot": dict(active_schema),
                "timestamp": datetime.now(timezone.utc),
                "patch_applied": patch,
                "patch_metadata": meta,
            }
            mongo.db.website_history.insert_one(history_record)

            # 3. Apply the surgical changes
            action = patch.get("action")

            if action == "update_section":
                cls._apply_update_section(active_schema, patch)

            elif action == "swap_variant":
                cls._apply_swap_variant(active_schema, patch)

            elif action == "move_section":
                cls._apply_move_section(active_schema, patch)

            elif action == "update_content":
                cls._apply_update_content(active_schema, patch)

            elif action == "reorder_sections":
                cls._apply_reorder_sections(active_schema, patch)

            elif action == "update_theme":
                theme_changes = patch.get("changes", {})
                active_schema["theme"] = {**active_schema.get("theme", {}), **theme_changes}

            elif action == "update_seo":
                seo_changes = patch.get("changes", {})
                active_schema["seo"] = {**active_schema.get("seo", {}), **seo_changes}

            elif action == "add_section":
                section_data = patch.get("section_data", {})
                active_schema["sections"].append(section_data)

            elif action == "delete_section":
                section_id = patch.get("section_id")
                active_schema["sections"] = [
                    s for s in active_schema.get("sections", [])
                    if s.get("id") != section_id
                ]

            # 4. Increment version
            new_version = int(current_version) + 1
            active_schema["schema_version"] = new_version
            active_schema["updated_at"] = datetime.now(timezone.utc)
            # Keep legacy field for backward compat
            active_schema["version"] = float(new_version)

            # 5. Save to MongoDB
            mongo.db.website_schemas.update_one(
                {"business_id": b_id_str, "is_active": True},
                {"$set": active_schema}
            )

            # 6. Render & deploy
            rendered_html = SchemaRenderer.render(active_schema)
            cls.write_website_to_disk(b_id_str, rendered_html)

            # Update child website records
            mongo.db.child_websites.update_one(
                {"owner_id": b_id_str},
                {"$set": {
                    "generated_content": rendered_html,
                    "updated_at": datetime.now(timezone.utc),
                    "seo_settings": active_schema.get("seo", {}),
                }}
            )

            # 7. Push update to live Netlify site (best-effort)
            cls._deploy_to_netlify(b_id_str, rendered_html)

            logger.info(f"✅ Patch applied: v{current_version} → v{new_version} for business {b_id_str}")
            return True, active_schema, None

        except Exception as e:
            logger.error(f"Error applying website patch: {e}")
            return False, None, str(e)

    # ================================================================
    # Rollback
    # ================================================================

    @classmethod
    def rollback(cls, business_id):
        """
        1-click rollback to the preceding version in website_history.
        """
        try:
            b_id_str = str(business_id)

            history_entry = mongo.db.website_history.find_one(
                {"business_id": b_id_str},
                sort=[("timestamp", -1)]
            )

            if not history_entry:
                return False, None, "No rollback point found for this business website."

            restored_schema = history_entry["schema_snapshot"]
            mongo.db.website_history.delete_one({"_id": history_entry["_id"]})

            restored_schema["updated_at"] = datetime.now(timezone.utc)
            mongo.db.website_schemas.update_one(
                {"business_id": b_id_str, "is_active": True},
                {"$set": restored_schema}
            )

            rendered_html = SchemaRenderer.render(restored_schema)
            cls.write_website_to_disk(b_id_str, rendered_html)

            mongo.db.child_websites.update_one(
                {"owner_id": b_id_str},
                {"$set": {
                    "generated_content": rendered_html,
                    "updated_at": datetime.now(timezone.utc),
                    "seo_settings": restored_schema.get("seo", {}),
                }}
            )

            # Push rollback to live Netlify site (best-effort)
            cls._deploy_to_netlify(b_id_str, rendered_html)

            rolled_version = restored_schema.get("schema_version", restored_schema.get("version", "?"))
            logger.info(f"⏪ Rolled back to v{rolled_version} for business {b_id_str}")
            return True, restored_schema, None

        except Exception as e:
            logger.error(f"Error performing website schema rollback: {e}")
            return False, None, str(e)

    # ================================================================
    # Version history retrieval
    # ================================================================

    @classmethod
    def get_version_history(cls, business_id, limit=20):
        """Returns the version timeline for a business (most recent first)."""
        b_id_str = str(business_id)
        cursor = mongo.db.website_history.find(
            {"business_id": b_id_str},
            {"schema_snapshot": 0},  # Exclude heavy snapshot data
        ).sort("timestamp", -1).limit(limit)

        results = []
        for doc in cursor:
            doc.pop("_id", None)
            results.append(doc)
        return results

    # ================================================================
    # Disk writer
    # ================================================================

    @classmethod
    def write_website_to_disk(cls, business_id, html_content):
        """Saves compiled HTML into a static local folder for instant serving."""
        try:
            websites_dir = os.path.join(
                os.path.dirname(__file__), '..', '..', 'static', 'websites', f"business-{business_id}"
            )
            os.makedirs(websites_dir, exist_ok=True)
            index_path = os.path.join(websites_dir, 'index.html')
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"📄 Schema HTML written to disk: {index_path}")
        except Exception as e:
            logger.error(f"Error writing schema site to disk: {e}")

    @classmethod
    def _deploy_to_netlify(cls, business_id, html_content):
        """
        Best-effort push of the new HTML to the live Netlify site.
        Looks up the Netlify site_id stored in child_websites during initial deployment.
        Failures are logged but never block the patch — the local + MongoDB versions are always saved.
        """
        try:
            site_record = mongo.db.child_websites.find_one({"owner_id": business_id})
            if not site_record:
                logger.debug(f"No child_website record for {business_id}, skipping Netlify deploy.")
                return

            netlify_site_id = site_record.get("netlify_site_id")
            if not netlify_site_id:
                logger.debug(f"No netlify_site_id for {business_id}, skipping Netlify deploy.")
                return

            from app.services.netlify_service import NetlifyService
            netlify = NetlifyService()
            deploy_result = netlify.deploy_site(netlify_site_id, {"index.html": html_content})

            if deploy_result.get("success"):
                logger.info(f"🚀 Netlify re-deploy successful for business {business_id}")
            else:
                logger.warning(f"⚠️ Netlify re-deploy failed for {business_id}: {deploy_result.get('error')}")
        except Exception as e:
            logger.warning(f"⚠️ Netlify deploy error (non-blocking) for {business_id}: {e}")

    # ================================================================
    # Private helpers: surgical patch application
    # ================================================================

    @classmethod
    def _apply_update_section(cls, schema, patch):
        section_id = patch.get("section_id")
        changes = patch.get("changes", {})
        for section in schema.get("sections", []):
            if section.get("id") == section_id:
                if "content" in changes and isinstance(changes["content"], dict):
                    section["content"] = {**section.get("content", {}), **changes["content"]}
                if "variant" in changes:
                    section["variant"] = changes["variant"]
                for k, v in changes.items():
                    if k not in ("content", "variant", "id", "type"):
                        section[k] = v
                break

    @classmethod
    def _apply_swap_variant(cls, schema, patch):
        section_id = patch.get("section_id")
        new_variant = patch.get("variant")
        for section in schema.get("sections", []):
            if section.get("id") == section_id:
                section["variant"] = new_variant
                break

    @classmethod
    def _apply_move_section(cls, schema, patch):
        section_id = patch.get("section_id")
        position = patch.get("position", 0)
        sections = schema.get("sections", [])
        target = None
        target_idx = None
        for idx, sec in enumerate(sections):
            if sec.get("id") == section_id:
                target = sec
                target_idx = idx
                break
        if target is not None:
            sections.pop(target_idx)
            sections.insert(position, target)

    @classmethod
    def _apply_update_content(cls, schema, patch):
        section_id = patch.get("section_id")
        content_changes = patch.get("changes", {})
        for section in schema.get("sections", []):
            if section.get("id") == section_id:
                section["content"] = {**section.get("content", {}), **content_changes}
                break

    @classmethod
    def _apply_reorder_sections(cls, schema, patch):
        order = patch.get("order", [])
        section_map = {s.get("id"): s for s in schema.get("sections", []) if s.get("id")}
        schema["sections"] = [section_map[s_id] for s_id in order if s_id in section_map]

    # ================================================================
    # Default schema factory
    # ================================================================

    @classmethod
    def create_default_schema(cls, business_id):
        """Generates a premium baseline schema for a spa / wellness business."""
        now = datetime.now(timezone.utc)
        return {
            "business_id": str(business_id),
            "schema_version": 1,
            "version": 1.0,
            "active_version": True,
            "deployment_id": None,
            "theme": {
                "palette": "spa-serenity",
                "font": "Inter",
            },
            "seo": {
                "title": "Aura Spa Serenity Center",
                "description": "Indulge in premium wellness, facials, and therapeutic massage treatments tailored for elegance.",
                "keywords": "spa, wellness, massage, facial, booking, beauty",
            },
            "sections": [
                {
                    "id": "hero_1",
                    "type": "hero",
                    "variant": "hero-split",
                    "content": {
                        "title": "Elevate Your Inner & Outer Well-Being",
                        "subtitle": "Discover luxury therapeutic treatments designed to restore balance, calm, and vital energy.",
                        "cta": "Schedule Priority Appointment",
                        "image": "https://images.unsplash.com/photo-1540555700478-4be289fbecef?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80",
                    },
                },
                {
                    "id": "services_1",
                    "type": "services",
                    "variant": "services-grid",
                    "content": {
                        "title": "Bespoke Wellness Therapies",
                        "items": [
                            {"name": "Deep Tissue Release", "price": "$120", "description": "Focused trigger point strokes and muscle alignment designed for complete decompression.", "icon": "fas fa-hands"},
                            {"name": "Rejuvenating Facial", "price": "$95", "description": "Custom enzyme treatments and collagen therapy to restore facial vitality and skin clarity.", "icon": "fas fa-spa"},
                            {"name": "Signature Spa Ritual", "price": "$210", "description": "Full-body luxury hot stone therapy and botanical exfoliation including head massage.", "icon": "fas fa-gem"},
                        ],
                    },
                },
                {
                    "id": "testimonials_1",
                    "type": "testimonials",
                    "variant": "testimonials-grid",
                    "content": {
                        "title": "Reflections of Serenity",
                        "items": [
                            {"name": "Clara Higgins", "role": "VIP Client", "quote": "The absolute highlight of my week. The deep tissue ritual is simply restorative!"},
                            {"name": "John Harrison", "role": "Premium Member", "quote": "Stunning aesthetics, highly professional staff, and impeccable attention to wellness details."},
                        ],
                    },
                },
                {
                    "id": "team_1",
                    "type": "team",
                    "variant": "team-cards",
                    "content": {
                        "title": "Master Practitioners",
                        "members": [
                            {"name": "Sophia Lauren", "role": "Bespoke Facial Specialist", "bio": "Over 12 years of hands-on expertise delivering custom enzyme skin vitalization.", "photo": "https://images.unsplash.com/photo-1494790108755-2616b612b786?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80"},
                            {"name": "Julian Hayes", "role": "Lead Massage Therapist", "bio": "Specialized in structural integration, aromatherapy, and hot-stone muscle release.", "photo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80"},
                        ],
                    },
                },
                {
                    "id": "booking_1",
                    "type": "booking",
                    "variant": "booking-embedded",
                    "content": {
                        "title": "Schedule Serenity",
                        "business_id": str(business_id),
                        "services": ["Deep Tissue Release", "Rejuvenating Facial", "Signature Spa Ritual"],
                    },
                },
                {
                    "id": "contact_1",
                    "type": "contact",
                    "variant": "contact-split",
                    "content": {
                        "title": "Connect With Aura Spa",
                        "business_id": str(business_id),
                        "address": "452 Botanical Circle, Serenity Suite 10",
                        "phone": "(555) 019-8234",
                        "email": "concierge@auraspa.com",
                    },
                },
                {
                    "id": "footer_1",
                    "type": "footer",
                    "variant": "footer-standard",
                    "content": {},
                },
            ],
            "is_active": True,
            "created_at": now,
            "updated_at": now,
        }

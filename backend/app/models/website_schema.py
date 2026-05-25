"""
WebsiteSchema — Dynamic Component Graph Model.

This is the HEART of the platform. Every website is stored as a structured JSON
document with immutable section IDs. The AI never generates raw HTML — it operates
on this schema, and the deterministic SchemaRenderer compiles it to HTML.

Fields:
    business_id         — Owner business ObjectId (str)
    schema_version      — Semantic integer version counter (1, 2, 3...)
    active_version      — Whether this is the live schema for the business
    deployment_id       — The Netlify/GitHub deployment ID linked to this version
    theme               — Color palette, fonts, spacing presets
    seo                 — Page title, description, keywords, favicon
    sections            — Ordered list of component dicts, each with immutable "id"
    created_at          — First creation timestamp
    updated_at          — Last modification timestamp
"""

from datetime import datetime, timezone
from bson import ObjectId


class WebsiteSchema:
    def __init__(
        self,
        business_id,
        sections,
        theme,
        seo,
        schema_version=1,
        active_version=True,
        deployment_id=None,
        is_active=True,
    ):
        self.business_id = str(business_id) if isinstance(business_id, (ObjectId,)) else str(business_id)
        self.sections = sections          # [{id: "hero_1", type: "hero", variant: "hero-split", content: {...}}, ...]
        self.theme = theme                # {palette, font, primary, accent, ...}
        self.seo = seo                    # {title, description, keywords, favicon}
        self.schema_version = int(schema_version)
        self.active_version = active_version
        self.deployment_id = deployment_id
        self.is_active = is_active
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        return {
            "business_id": self.business_id,
            "sections": self.sections,
            "theme": self.theme,
            "seo": self.seo,
            "schema_version": self.schema_version,
            "active_version": self.active_version,
            "deployment_id": self.deployment_id,
            "is_active": self.is_active,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @staticmethod
    def from_dict(data):
        schema = WebsiteSchema(
            business_id=data["business_id"],
            sections=data.get("sections", []),
            theme=data.get("theme", {}),
            seo=data.get("seo", {}),
            schema_version=data.get("schema_version", data.get("version", 1)),
            active_version=data.get("active_version", True),
            deployment_id=data.get("deployment_id"),
            is_active=data.get("is_active", True),
        )
        schema.created_at = data.get("created_at", datetime.now(timezone.utc))
        schema.updated_at = data.get("updated_at", datetime.now(timezone.utc))
        return schema

    # ------------------------------------------------------------------
    # Validation helpers
    # ------------------------------------------------------------------

    def get_section_ids(self):
        """Returns the set of all immutable section IDs in this schema."""
        return {s.get("id") for s in self.sections if s.get("id")}

    def get_section_by_id(self, section_id):
        """Lookup a single section by its immutable ID."""
        for s in self.sections:
            if s.get("id") == section_id:
                return s
        return None

    def validate_immutable_ids(self):
        """Ensures every section has a unique, non-empty 'id' field."""
        seen = set()
        for idx, sec in enumerate(self.sections):
            sid = sec.get("id")
            if not sid:
                return False, f"Section at index {idx} is missing an immutable 'id'."
            if sid in seen:
                return False, f"Duplicate section ID: '{sid}'."
            seen.add(sid)
        return True, None

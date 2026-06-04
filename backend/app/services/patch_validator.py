"""
PatchValidator — Security & Layout Safety Sandbox.

Validates EVERY incoming patch BEFORE it touches the schema or deployment.
Enforces:
    - Component type compatibility
    - Allowed variants per component type
    - Missing required content fields
    - Responsive safety (locked design system cores)
    - Duplicate section ID prevention
    - Broken layout detection
    - Raw code / JS injection blocking
    - AI cannot modify base types, animations, grids, or responsive breakpoints
"""

import re


class PatchValidator:

    # ================================================================
    # STRICT DESIGN CONSTRAINTS — AI operates INSIDE these only
    # ================================================================

    ALLOWED_VARIANTS = {
        "hero": ["hero-split", "hero-centered", "hero-minimal", "hero-luxury"],
        "services": ["services-grid", "services-list", "services-carousel"],
        "testimonials": ["testimonials-grid", "testimonials-carousel"],
        "team": ["team-cards", "team-list"],
        "booking": ["booking-embedded", "booking-modal"],
        "contact": ["contact-split", "contact-centered"],
        "footer": ["footer-standard", "footer-minimal"],
        "gallery": ["gallery-grid", "gallery-masonry", "gallery-carousel"],
        "cta": ["cta-banner", "cta-card", "cta-floating"],
        "pricing": ["pricing-cards", "pricing-table", "pricing-toggle"],
    }

    ALLOWED_COLORS = {
        "rose-gold-luxury": ["#b76e79", "#faf3f3", "#3d3234", "#e4b4b8"],
        "spa-serenity": ["#8fa89b", "#f4f7f6", "#2c3b35", "#d0dfd8"],
        "lavender-luxury": ["#a799b7", "#fdfbfd", "#2d2430", "#d6cbd9"],
        "royal-navy": ["#1d2a44", "#f5f7fa", "#0c1524", "#3b5998"],
        "emerald-gold": ["#044a27", "#fcfbf7", "#112217", "#d4af37"],
    }

    # Required content fields per section type
    REQUIRED_CONTENT_FIELDS = {
        "hero": ["title"],
        "services": ["title"],
        "testimonials": ["title"],
        "team": ["title"],
        "booking": ["title", "business_id"],
        "contact": ["title", "business_id"],
        "cta": ["title", "cta"],
        "pricing": ["title"],
    }

    # Locked design system keys that AI must NEVER touch
    LOCKED_DESIGN_KEYS = frozenset([
        "responsive_breakpoints",
        "grid_system",
        "animation_engine",
        "base_font_size",
        "line_height_scale",
    ])

    # Supported patch actions
    SUPPORTED_ACTIONS = frozenset([
        "update_section",
        "reorder_sections",
        "update_theme",
        "update_seo",
        "add_section",
        "delete_section",
        "swap_variant",
        "move_section",
        "update_content",
    ])

    # Forbidden HTML/JS injection patterns
    FORBIDDEN_PATTERNS = [
        r"<script\b[^>]*>",
        r"javascript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
        r"onmouseover\s*=",
        r"onfocus\s*=",
        r"style\s*=\s*['\"]?[^'\"]*expression\(",
        r"behavior\s*:",
        r"document\.write",
        r"document\.cookie",
        r"eval\s*\(",
        r"Function\s*\(",
        r"<iframe\b",
        r"<object\b",
        r"<embed\b",
        r"<link\b[^>]*rel\s*=\s*['\"]?import",
        r"@import\s+url",
    ]

    # ================================================================
    # Full schema validation
    # ================================================================

    @classmethod
    def validate_schema(cls, schema_dict):
        """
        Validates a full website schema dictionary.
        Returns (is_valid: bool, error_message: str | None).
        """
        if not isinstance(schema_dict, dict):
            return False, "Schema must be a JSON dictionary."

        # Required top-level fields
        for field in ["business_id", "sections", "theme", "seo"]:
            if field not in schema_dict:
                return False, f"Missing required top-level field: '{field}'"

        # Validate SEO
        seo = schema_dict.get("seo", {})
        if not isinstance(seo, dict) or "title" not in seo:
            return False, "SEO config must contain a 'title'."

        # Validate Theme
        theme = schema_dict.get("theme", {})
        if not isinstance(theme, dict):
            return False, "Theme config must be a dictionary."

        # Validate Sections — immutable IDs, types, variants, duplicates
        sections = schema_dict.get("sections", [])
        if not isinstance(sections, list):
            return False, "Sections must be a list of component blocks."

        seen_ids = set()
        for idx, section in enumerate(sections):
            if not isinstance(section, dict):
                return False, f"Section at index {idx} must be a dictionary object."

            section_id = section.get("id")
            if not section_id:
                return False, f"Section at index {idx} is missing an immutable 'id'."

            if section_id in seen_ids:
                return False, f"Duplicate section ID detected: '{section_id}'."
            seen_ids.add(section_id)

            section_type = section.get("type")
            if not section_type:
                return False, f"Section '{section_id}' is missing its component 'type'."

            if section_type not in cls.ALLOWED_VARIANTS:
                return False, f"Unsupported section type '{section_type}' in section '{section_id}'."

            variant = section.get("variant")
            if variant and variant not in cls.ALLOWED_VARIANTS[section_type]:
                return False, f"Unsupported variant '{variant}' for type '{section_type}' in section '{section_id}'."

            # Validate required content fields
            content = section.get("content", {})
            required_fields = cls.REQUIRED_CONTENT_FIELDS.get(section_type, [])
            for rf in required_fields:
                if rf not in content:
                    return False, f"Section '{section_id}' ({section_type}) missing required content field: '{rf}'."

        return True, None

    # ================================================================
    # Patch validation — runs BEFORE schema saves, rendering, deployment
    # ================================================================

    @classmethod
    def validate_patch(cls, active_schema, patch):
        """
        Validates an incoming JSON patch against the active schema.
        Checks: actions, security injections, layout breaks, variant bounds.
        Returns (is_valid: bool, error_message: str | None).
        """
        if not isinstance(patch, dict):
            return False, "Patch must be a dictionary object."

        action = patch.get("action")
        if action not in cls.SUPPORTED_ACTIONS:
            return False, f"Unsupported patch action: '{action}'"

        # ---- Security: Block raw code injection ----
        str_patch = str(patch).lower()
        for pattern in cls.FORBIDDEN_PATTERNS:
            if re.search(pattern, str_patch, re.IGNORECASE):
                return False, "Security threat blocked: Arbitrary JavaScript or stylesheet injection detected."

        # ---- Action-specific validation ----
        if action == "update_section":
            return cls._validate_update_section(active_schema, patch)

        elif action == "swap_variant":
            return cls._validate_swap_variant(active_schema, patch)

        elif action == "move_section":
            return cls._validate_move_section(active_schema, patch)

        elif action == "update_content":
            return cls._validate_update_content(active_schema, patch)

        elif action == "reorder_sections":
            order = patch.get("order", [])
            if not isinstance(order, list):
                return False, "Action 'reorder_sections' must provide an 'order' list of section IDs."
            current_ids = {s.get("id") for s in active_schema.get("sections", []) if s.get("id")}
            if set(order) != current_ids:
                return False, "Reordering mismatch: the list of IDs must match active section IDs exactly."

        elif action == "update_theme":
            theme_changes = patch.get("changes", {})
            if not isinstance(theme_changes, dict):
                return False, "Theme update 'changes' must be a dictionary."
            for locked_key in cls.LOCKED_DESIGN_KEYS:
                if locked_key in theme_changes:
                    return False, f"Altering design system core setting '{locked_key}' is forbidden."

        elif action == "update_seo":
            seo_changes = patch.get("changes", {})
            if not isinstance(seo_changes, dict):
                return False, "SEO update 'changes' must be a dictionary."

        elif action == "add_section":
            section_data = patch.get("section_data", {})
            if not isinstance(section_data, dict):
                return False, "add_section requires a 'section_data' dictionary."
            new_id = section_data.get("id")
            if not new_id:
                return False, "New section must have an immutable 'id'."
            existing_ids = {s.get("id") for s in active_schema.get("sections", []) if s.get("id")}
            if new_id in existing_ids:
                return False, f"Section ID '{new_id}' already exists. IDs must be unique."
            new_type = section_data.get("type")
            if new_type and new_type not in cls.ALLOWED_VARIANTS:
                return False, f"Unsupported section type '{new_type}'."

        elif action == "delete_section":
            section_id = patch.get("section_id")
            if not section_id:
                return False, "delete_section requires a 'section_id'."

        return True, None

    # ================================================================
    # Private helpers for specific action types
    # ================================================================

    @classmethod
    def _validate_update_section(cls, active_schema, patch):
        section_id = patch.get("section_id")
        if not section_id:
            return False, "Action 'update_section' is missing 'section_id'."

        target_sec = cls._find_section(active_schema, section_id)
        if not target_sec:
            return False, f"Target section '{section_id}' not found in active website schema."

        changes = patch.get("changes", {})
        if not isinstance(changes, dict):
            return False, "Section 'changes' must be a dictionary of properties to update."

        # Block base type mutation
        if "type" in changes and changes["type"] != target_sec["type"]:
            return False, "Altering the base 'type' of a section is blocked. Delete and create a new section instead."

        # Validate variant
        new_variant = changes.get("variant")
        if new_variant and new_variant not in cls.ALLOWED_VARIANTS.get(target_sec["type"], []):
            return False, f"Variant '{new_variant}' is not supported for component type '{target_sec['type']}'."

        return True, None

    @classmethod
    def _validate_swap_variant(cls, active_schema, patch):
        section_id = patch.get("section_id")
        new_variant = patch.get("variant")
        if not section_id or not new_variant:
            return False, "swap_variant requires 'section_id' and 'variant'."

        target_sec = cls._find_section(active_schema, section_id)
        if not target_sec:
            return False, f"Target section '{section_id}' not found."

        if new_variant not in cls.ALLOWED_VARIANTS.get(target_sec["type"], []):
            return False, f"Variant '{new_variant}' is not supported for type '{target_sec['type']}'."

        return True, None

    @classmethod
    def _validate_move_section(cls, active_schema, patch):
        section_id = patch.get("section_id")
        position = patch.get("position")
        if not section_id:
            return False, "move_section requires 'section_id'."
        if position is None or not isinstance(position, int):
            return False, "move_section requires an integer 'position'."

        target_sec = cls._find_section(active_schema, section_id)
        if not target_sec:
            return False, f"Target section '{section_id}' not found."

        max_pos = len(active_schema.get("sections", []))
        if position < 0 or position >= max_pos:
            return False, f"Position {position} is out of bounds (0–{max_pos - 1})."

        return True, None

    @classmethod
    def _validate_update_content(cls, active_schema, patch):
        section_id = patch.get("section_id")
        content_changes = patch.get("changes", {})
        if not section_id:
            return False, "update_content requires 'section_id'."
        if not isinstance(content_changes, dict):
            return False, "Content 'changes' must be a dictionary."

        target_sec = cls._find_section(active_schema, section_id)
        if not target_sec:
            return False, f"Target section '{section_id}' not found."

        return True, None

    @classmethod
    def _find_section(cls, schema, section_id):
        for sec in schema.get("sections", []):
            if sec.get("id") == section_id:
                return sec
        return None

    # ================================================================
    # Structured validation report (for MCP tool consumption)
    # ================================================================

    @classmethod
    def validate_and_report(cls, schema_dict, patch):
        """
        Returns a structured validation report dict:
        {
            "valid": bool,
            "errors": [...],
            "warnings": [...],
            "security_flags": [...]
        }

        This output is what the validate_patch_sandbox MCP tool wraps,
        making validation results machine-readable for the orchestrator.
        """
        report = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "security_flags": [],
        }

        if not isinstance(patch, dict):
            report["valid"] = False
            report["errors"].append("Patch must be a dictionary object.")
            return report

        action = patch.get("action")
        if action not in cls.SUPPORTED_ACTIONS:
            report["valid"] = False
            report["errors"].append(f"Unsupported patch action: '{action}'")
            return report

        # ── Security scan ──
        str_patch = str(patch).lower()
        for pattern in cls.FORBIDDEN_PATTERNS:
            import re
            if re.search(pattern, str_patch, re.IGNORECASE):
                report["valid"] = False
                report["security_flags"].append(
                    f"Blocked pattern detected: {pattern}"
                )
                report["errors"].append(
                    "Security threat blocked: Arbitrary JavaScript or stylesheet injection detected."
                )

        if not report["valid"]:
            return report

        # ── Standard validation ──
        is_valid, err_msg = cls.validate_patch(schema_dict, patch)
        if not is_valid:
            report["valid"] = False
            report["errors"].append(err_msg)

        # ── Advisory warnings (non-blocking) ──
        if action in ("update_section", "update_content"):
            section_id = patch.get("section_id")
            if section_id and section_id.startswith("hero_"):
                report["warnings"].append(
                    "Modifying hero sections impacts first-impression metrics. "
                    "Ensure A/B baseline is captured before deploying."
                )

        if action == "reorder_sections":
            order = patch.get("order", [])
            if order and order[0] != "hero_1":
                report["warnings"].append(
                    "Hero section is not first in the proposed order. "
                    "This may increase bounce rate on landing page."
                )

        if action == "swap_variant":
            report["warnings"].append(
                "Variant swap changes the visual layout structure. "
                "Verify mobile responsiveness after deployment."
            )

        return report

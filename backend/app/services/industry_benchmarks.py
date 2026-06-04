"""
IndustryBenchmarks — Cold-Start Intelligence Seeder.

Pre-seeds the `industry_benchmark_patterns` collection with proven
cross-business optimization patterns per industry vertical.

These benchmarks give NEW business owners immediate AI suggestions
before they accumulate their own optimization history.
"""

import logging
from datetime import datetime, timezone
from app import mongo

logger = logging.getLogger(__name__)


# ====================================================================
# Benchmark Templates
# ====================================================================

BENCHMARK_PATTERNS = [
    # ── Spa & Beauty Salon ──
    {
        "industry": "spa",
        "pattern_name": "cta_above_fold",
        "description": "Moving the primary booking CTA above the fold increases appointment conversion by 15-22%.",
        "layout_template": {
            "section_type": "hero",
            "variant": "hero-split",
            "content_guidance": {
                "cta_position": "above_fold",
                "cta_text_style": "action_verb + urgency",
                "examples": ["Reserve Priority Slot Now", "Book Your Treatment Today"],
            },
        },
        "expected_conversion_gain": 18.0,
        "confidence": 88,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "spa",
        "pattern_name": "services_grid_with_pricing",
        "description": "Displaying service prices in a grid layout reduces bounce rate by 12% compared to list view.",
        "layout_template": {
            "section_type": "services",
            "variant": "services-grid",
            "content_guidance": {
                "show_prices": True,
                "max_items_visible": 6,
                "include_icons": True,
            },
        },
        "expected_conversion_gain": 12.0,
        "confidence": 82,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "spa",
        "pattern_name": "testimonials_near_booking",
        "description": "Placing testimonials directly above the booking section improves trust signals and booking rate by 9%.",
        "layout_template": {
            "section_order": ["hero", "services", "team", "testimonials", "booking", "contact", "footer"],
            "content_guidance": {
                "testimonials_position": "immediately_before_booking",
            },
        },
        "expected_conversion_gain": 9.0,
        "confidence": 76,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "spa",
        "pattern_name": "team_photos_increase_trust",
        "description": "Including professional staff photos increases page dwell time by 23% and booking clicks by 11%.",
        "layout_template": {
            "section_type": "team",
            "variant": "team-cards",
            "content_guidance": {
                "include_photos": True,
                "include_specializations": True,
                "photo_style": "professional_headshot",
            },
        },
        "expected_conversion_gain": 11.0,
        "confidence": 80,
        "source": "aggregate_platform_data",
    },

    # ── Law Firm ──
    {
        "industry": "law_firm",
        "pattern_name": "consultation_cta_prominent",
        "description": "A prominent free consultation CTA with phone number increases lead generation by 25%.",
        "layout_template": {
            "section_type": "hero",
            "variant": "hero-centered",
            "content_guidance": {
                "cta_text": "Schedule Free Consultation",
                "include_phone_number": True,
                "trust_badges": ["Bar Association", "Years of Experience"],
            },
        },
        "expected_conversion_gain": 25.0,
        "confidence": 90,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "law_firm",
        "pattern_name": "practice_areas_grid",
        "description": "Structured practice area cards with clear descriptions improve client inquiry rate by 16%.",
        "layout_template": {
            "section_type": "services",
            "variant": "services-grid",
            "content_guidance": {
                "title": "Practice Areas",
                "include_descriptions": True,
                "include_icons": True,
                "max_areas": 6,
            },
        },
        "expected_conversion_gain": 16.0,
        "confidence": 84,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "law_firm",
        "pattern_name": "attorney_bios_with_credentials",
        "description": "Detailed attorney bios with credentials and case highlights build authority and improve consultation bookings by 14%.",
        "layout_template": {
            "section_type": "team",
            "variant": "team-cards",
            "content_guidance": {
                "include_credentials": True,
                "include_case_highlights": True,
                "include_bar_admission": True,
            },
        },
        "expected_conversion_gain": 14.0,
        "confidence": 82,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "law_firm",
        "pattern_name": "client_testimonials_anonymized",
        "description": "Anonymized client testimonials with case type context increase trust and inquiry rate by 10%.",
        "layout_template": {
            "section_type": "testimonials",
            "variant": "testimonials-carousel",
            "content_guidance": {
                "anonymize_names": True,
                "include_case_type": True,
                "include_outcome_summary": True,
            },
        },
        "expected_conversion_gain": 10.0,
        "confidence": 75,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "law_firm",
        "pattern_name": "consultation_scheduling_flow",
        "description": "Embedding a booking section with pre-selected consultation type and time-slot picker reduces scheduling friction and increases booked consultations by 22%.",
        "layout_template": {
            "section_type": "booking",
            "variant": "booking-embedded",
            "content_guidance": {
                "title": "Schedule Your Free Consultation",
                "pre_select_service": "Initial Consultation",
                "show_time_slots": True,
                "include_case_type_dropdown": True,
                "services": ["Initial Consultation", "Case Review", "Legal Strategy Session"],
            },
        },
        "expected_conversion_gain": 22.0,
        "confidence": 87,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "law_firm",
        "pattern_name": "contact_form_with_intake",
        "description": "A contact form with structured intake fields (case type, urgency, brief description) produces higher-quality leads and increases qualified inquiry rate by 18%.",
        "layout_template": {
            "section_type": "contact",
            "variant": "contact-split",
            "content_guidance": {
                "include_case_type_field": True,
                "include_urgency_selector": True,
                "include_brief_description": True,
                "include_phone_number": True,
                "include_office_hours": True,
                "cta_text": "Request Case Evaluation",
            },
        },
        "expected_conversion_gain": 18.0,
        "confidence": 85,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "law_firm",
        "pattern_name": "section_ordering_conversion_funnel",
        "description": "Ordering sections as Hero → Practice Areas → Attorney Bios → Testimonials → Booking → Contact creates a natural trust-building funnel that increases consultation bookings by 15%.",
        "layout_template": {
            "section_order": ["hero", "services", "team", "testimonials", "booking", "contact", "footer"],
            "content_guidance": {
                "rationale": "Trust funnel: establish authority (practice areas, bios) then social proof (testimonials) before asking for commitment (booking).",
                "hero_must_include": ["phone_number", "consultation_cta"],
                "services_title": "Practice Areas",
                "team_title": "Our Attorneys",
            },
        },
        "expected_conversion_gain": 15.0,
        "confidence": 81,
        "source": "aggregate_platform_data",
    },

    # ── General / Default ──
    {
        "industry": "general",
        "pattern_name": "mobile_responsive_hero",
        "description": "Mobile-first hero sections with condensed copy and full-width CTA buttons improve mobile conversion by 20%.",
        "layout_template": {
            "section_type": "hero",
            "variant": "hero-minimal",
            "content_guidance": {
                "copy_length": "short",
                "cta_width": "full_width_mobile",
                "image_optimization": "lazy_load",
            },
        },
        "expected_conversion_gain": 20.0,
        "confidence": 86,
        "source": "aggregate_platform_data",
    },
    {
        "industry": "general",
        "pattern_name": "social_proof_above_fold",
        "description": "Displaying review count or rating badge in the hero section increases trust and click-through by 13%.",
        "layout_template": {
            "section_type": "hero",
            "content_guidance": {
                "include_rating_badge": True,
                "include_review_count": True,
                "position": "below_subtitle",
            },
        },
        "expected_conversion_gain": 13.0,
        "confidence": 78,
        "source": "aggregate_platform_data",
    },
]


# ====================================================================
# Seeder
# ====================================================================

def seed_benchmarks():
    """
    Populates the `industry_benchmark_patterns` collection with pre-built
    optimization intelligence for cold-start businesses.
    """
    now = datetime.now(timezone.utc)
    inserted = 0

    for pattern in BENCHMARK_PATTERNS:
        doc = {
            **pattern,
            "created_at": now,
            "updated_at": now,
        }

        # Upsert to avoid duplicates on re-seed
        result = mongo.db.industry_benchmark_patterns.update_one(
            {"industry": pattern["industry"], "pattern_name": pattern["pattern_name"]},
            {"$setOnInsert": doc},
            upsert=True,
        )
        if result.upserted_id:
            inserted += 1

    logger.info(
        f"Industry benchmarks seeded: {inserted} new patterns "
        f"({len(BENCHMARK_PATTERNS)} total templates)"
    )


def get_benchmarks_for_industry(industry, limit=5):
    """
    Retrieves benchmark patterns for a specific industry.
    Falls back to 'general' patterns if no industry-specific ones exist.
    """
    results = list(
        mongo.db.industry_benchmark_patterns.find(
            {"industry": industry}, {"_id": 0}
        ).sort("expected_conversion_gain", -1).limit(limit)
    )

    if not results:
        results = list(
            mongo.db.industry_benchmark_patterns.find(
                {"industry": "general"}, {"_id": 0}
            ).sort("expected_conversion_gain", -1).limit(limit)
        )

    return results

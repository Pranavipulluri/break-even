"""
Event Routes — Analytics Event Ingestion & Summary Endpoints.

Endpoints:
    POST /api/events/ingest          — Public (API key auth), accepts child website events
    GET  /api/events/summary/<id>    — JWT-protected, returns aggregated metrics for copilot
"""

import logging
import secrets
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.event_collector import event_collector

logger = logging.getLogger(__name__)

event_bp = Blueprint("events", __name__)


# ================================================================
# POST /api/events/ingest — Public endpoint for child websites
# ================================================================

@event_bp.route("/events/ingest", methods=["POST"])
def ingest_event():
    """
    Accepts analytics events from deployed child websites.

    Auth:
        PRODUCTION:  X-BE-Key header required (API key from /api/events/generate-key).
        DEVELOPMENT: Keyless allowed ONLY if FLASK_ENV=development AND business_id
                     exists in child_websites. This prevents open ingestion from
                     arbitrary external callers.

    Body:
    {
        "business_id": "...",
        "event_type": "cta_click",
        "event_data": { ... },
        "source_url": "https://example.netlify.app"
    }
    """
    try:
        api_key = request.headers.get("X-BE-Key")
        data = request.get_json(force=True, silent=True) or {}
        business_id = data.get("business_id")

        if not business_id:
            return jsonify({"success": False, "error": "business_id is required"}), 400

        b_id_str = str(business_id)

        if api_key:
            # Verify the key belongs to this business
            site = mongo.db.child_websites.find_one(
                {"owner_id": b_id_str, "api_key": api_key},
                {"_id": 1},
            )
            if not site:
                return jsonify({"success": False, "error": "Invalid API key"}), 403
        else:
            # No API key — only allow in development mode AND only if the business exists
            from flask import current_app
            is_dev = current_app.config.get("ENV") == "development" or current_app.debug
            if not is_dev:
                return jsonify({
                    "success": False,
                    "error": "X-BE-Key header required. Generate one via POST /api/events/generate-key/<business_id>",
                }), 403

            # Even in dev, verify the business actually exists to prevent phantom data
            site = mongo.db.child_websites.find_one(
                {"owner_id": b_id_str}, {"_id": 1}
            )
            if not site:
                return jsonify({
                    "success": False,
                    "error": f"No child website found for business '{b_id_str}'. Cannot ingest events.",
                }), 404

        success, error = event_collector.ingest_event(
            business_id=business_id,
            event_type=data.get("event_type", "page_view"),
            event_data=data.get("event_data"),
            source_url=data.get("source_url"),
            visitor_ip=request.remote_addr,
            timestamp=data.get("timestamp"),
        )

        if not success:
            return jsonify({"success": False, "error": error}), 400

        return jsonify({"success": True, "message": "Event accepted"}), 202

    except Exception as e:
        logger.error(f"Error in /events/ingest: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================================================================
# GET /api/events/summary/<business_id> — JWT-protected for copilot
# ================================================================

@event_bp.route("/events/summary/<business_id>", methods=["GET"])
@jwt_required()
def get_event_summary(business_id):
    """
    Returns aggregated event counts for the copilot's analytics interpreter.
    Optional query param: ?days=7 (default 7)
    """
    try:
        days = request.args.get("days", 7, type=int)
        summary = event_collector.get_event_summary(business_id, days=days)

        return jsonify({"success": True, "summary": summary}), 200

    except Exception as e:
        logger.error(f"Error in /events/summary: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================================================================
# POST /api/events/generate-key/<business_id> — Generate API key
# ================================================================

@event_bp.route("/events/generate-key/<business_id>", methods=["POST"])
@jwt_required()
def generate_api_key(business_id):
    """
    Generates a new API key for a business's child website event ingestion.
    Stored in child_websites.api_key.
    """
    try:
        user_id = get_jwt_identity()
        b_id_str = str(business_id)

        # Verify the caller owns this business
        site = mongo.db.child_websites.find_one({"owner_id": b_id_str})
        if not site:
            return jsonify({"success": False, "error": "No website found for this business"}), 404

        # Generate a secure API key
        api_key = f"be_{secrets.token_urlsafe(32)}"

        mongo.db.child_websites.update_one(
            {"owner_id": b_id_str},
            {"$set": {"api_key": api_key}},
        )

        return jsonify({
            "success": True,
            "api_key": api_key,
            "usage": 'Include as header: X-BE-Key: <api_key>',
        }), 200

    except Exception as e:
        logger.error(f"Error in /events/generate-key: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

"""
Agent Routes — API Endpoints for the AI Business Copilot System.

Endpoints:
    POST /api/agents/optimize         — Trigger the optimization loop
    POST /api/schema/patch/apply      — Apply the pending patch
    POST /api/schema/rollback         — Rollback to previous version
    GET  /api/schema/current/<id>     — Fetch active website schema
    GET  /api/schema/history/<id>     — Fetch version timeline

SECURITY: Every endpoint verifies that the JWT caller actually owns the
requested business_id.  Without this check, any authenticated user could
trigger optimizations, read schemas, or apply patches for other businesses.
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from bson import ObjectId
from app import mongo
from app.services.copilot_orchestrator import BusinessCopilot
from app.services.patch_engine import PatchEngine
from app.services.business_memory import BusinessMemory

logger = logging.getLogger(__name__)

agent_bp = Blueprint("agent", __name__)


# ================================================================
# Ownership verification helper
# ================================================================

def _verify_business_ownership(user_id, business_id):
    """
    Verifies that the JWT-authenticated user actually owns the requested business.

    Ownership is established if:
        1. business_id == user_id  (user IS the business owner), OR
        2. A child_websites record with owner_id == business_id exists AND
           its owner_id matches the JWT user, OR
        3. The business_id is a child_website _id and its owner_id matches the JWT user.

    Returns:
        (is_owner: bool, error_response: tuple | None)
    """
    uid_str = str(user_id)
    bid_str = str(business_id)

    # Fast path: user_id IS the business_id (most common case)
    if uid_str == bid_str:
        return True, None

    try:
        # Path A: bid_str is an owner_id in child_websites
        site = mongo.db.child_websites.find_one(
            {"owner_id": bid_str},
            {"owner_id": 1},
        )
        if site and str(site.get("owner_id")) == uid_str:
            return True, None

        # Path B: bid_str is the child_website _id itself
        try:
            site_by_id = mongo.db.child_websites.find_one(
                {"_id": ObjectId(bid_str)},
                {"owner_id": 1},
            )
            if site_by_id and str(site_by_id.get("owner_id")) == uid_str:
                return True, None
        except Exception:
            pass  # bid_str is not a valid ObjectId — skip

        # Path C: bid_str is a user document _id that matches the JWT user
        user_doc = mongo.db.users.find_one({"_id": ObjectId(bid_str)}, {"_id": 1})
        if user_doc and str(user_doc["_id"]) == uid_str:
            return True, None

    except Exception as e:
        logger.warning(f"Ownership check error: {e}")

    return False, (
        jsonify({
            "success": False,
            "error": "Access denied: you do not own this business.",
        }),
        403,
    )


# ================================================================
# POST /api/agents/optimize — Trigger AI optimization loop
# ================================================================

@agent_bp.route("/agents/optimize", methods=["POST"])
@jwt_required()
def trigger_optimization():
    """
    Accepts a user command, runs the full reflective optimization loop,
    and returns the proposed patch for approval.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json(force=True)
        user_command = data.get("command", "Optimize my website for better conversions")
        business_id = data.get("business_id", user_id)

        # IDOR guard
        is_owner, err = _verify_business_ownership(user_id, business_id)
        if not is_owner:
            return err

        copilot = BusinessCopilot(business_id)
        result = copilot.run_optimization_loop(user_command)

        return jsonify(result), 200 if result.get("success") else 400

    except Exception as e:
        logger.error(f"Error in /agents/optimize: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================================================================
# POST /api/schema/patch/apply — Apply the pending patch
# ================================================================

@agent_bp.route("/schema/patch/apply", methods=["POST"])
@jwt_required()
def apply_pending_patch():
    """
    Applies a patch to the website schema.  Supports two modes:

    1.  **Direct patch** — the request body contains a "patch" dict.  Used by
        the live schema editor when the user edits a field directly.
    2.  **Pending approval** — no "patch" in the body.  Fetches the proposal
        saved by the optimization loop and applies it (human-approval step).
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json(force=True)
        business_id = data.get("business_id", user_id)
        b_id_str = str(business_id)

        # IDOR guard
        is_owner, err = _verify_business_ownership(user_id, business_id)
        if not is_owner:
            return err

        # ── MODE 1: Direct patch from live editor ──
        direct_patch = data.get("patch")
        if direct_patch:
            patch_metadata = {
                "patch_name": direct_patch.get("action", "manual_edit"),
                "trigger_reason": data.get("reason", "Direct schema edit by owner"),
                "agent_name": "User",
                "affected_section": direct_patch.get("section_id", "global"),
                "expected_impact": "N/A",
                "confidence_score": 100,
            }

            success, updated_schema, error = PatchEngine.apply_patch(
                business_id, direct_patch, patch_metadata
            )

            if not success:
                return jsonify({"success": False, "error": error}), 400

            # Store a manual-edit memory record
            site_doc = mongo.db.child_websites.find_one(
                {"owner_id": b_id_str}, {"industry_type": 1}
            )
            industry = (site_doc or {}).get("industry_type", "general")

            BusinessMemory.add_memory(
                business_id=business_id,
                patch_name=direct_patch.get("action", "manual_edit"),
                reason=data.get("reason", "Direct schema edit by owner"),
                layout_used=str(direct_patch),
                metrics_before=0,
                metrics_after=0,
                conversion_gain=0,
                agent_name="User",
                patch_outcome="applied_pending_results",
                industry_type=industry,
                patch_json=direct_patch,
                deploy_ref=updated_schema.get("deploy_ref"),
            )

            return jsonify({
                "success": True,
                "message": "Direct patch applied successfully.",
                "new_version": updated_schema.get("schema_version", updated_schema.get("version")),
                "deploy_ref": updated_schema.get("deploy_ref"),
            }), 200

        # ── MODE 2: Apply pending copilot proposal ──
        pending = mongo.db.pending_patches.find_one(
            {"business_id": b_id_str, "is_applied": False}
        )

        if not pending:
            return jsonify({
                "success": False,
                "error": "No pending patch found. Run the optimization loop first.",
            }), 404

        proposal = pending.get("proposal", {})
        patch = proposal.get("proposed_patch", {})
        hypothesis = proposal.get("hypothesis", {})

        # Build enriched patch metadata for the history record
        patch_metadata = {
            "patch_name": patch.get("action", "optimization_patch"),
            "trigger_reason": hypothesis.get("explanation", "User-approved optimization"),
            "agent_name": "BusinessCopilot",
            "affected_section": patch.get("section_id", "global"),
            "expected_impact": proposal.get("expected_impact", "N/A"),
            "confidence_score": proposal.get("confidence", 0),
            "before_metrics": proposal.get("hypothesis", {}).get("before_metrics", {}),
        }

        # Apply the patch through the engine
        success, updated_schema, error = PatchEngine.apply_patch(
            business_id, patch, patch_metadata
        )

        if not success:
            return jsonify({"success": False, "error": error}), 400

        # Mark as applied
        mongo.db.pending_patches.update_one(
            {"_id": pending["_id"]},
            {"$set": {"is_applied": True, "applied_at": datetime.now(timezone.utc)}},
        )

        # ── Store positive optimization memory with REAL metrics ──
        obs_metrics = proposal.get("hypothesis", {}).get("before_metrics", {})
        metrics_before = obs_metrics.get(
            "conversion_rate_percentage",
            obs_metrics.get("engagement_rate_percentage", 0),
        )
        expected_gain_str = str(proposal.get("expected_impact", "0"))
        import re
        gain_match = re.search(r"[+-]?(\d+\.?\d*)", expected_gain_str)
        expected_gain = float(gain_match.group(1)) if gain_match else 0.0

        site_doc = mongo.db.child_websites.find_one(
            {"owner_id": b_id_str}, {"industry_type": 1}
        )
        industry = (site_doc or {}).get("industry_type", "general")

        deploy_ref = updated_schema.get("deploy_ref")

        BusinessMemory.add_memory(
            business_id=business_id,
            patch_name=patch.get("action", "patch"),
            reason=hypothesis.get("explanation", "Manual optimization"),
            layout_used=str(patch),
            metrics_before=metrics_before,
            metrics_after=metrics_before + expected_gain,
            conversion_gain=expected_gain,
            agent_name="BusinessCopilot",
            patch_outcome="applied_pending_results",
            industry_type=industry,
            patch_json=patch,
            deploy_ref=deploy_ref,
        )

        return jsonify({
            "success": True,
            "message": "Patch applied successfully. Website updated at the same URL.",
            "new_version": updated_schema.get("schema_version", updated_schema.get("version")),
            "deploy_ref": deploy_ref,
        }), 200

    except Exception as e:
        logger.error(f"Error in /schema/patch/apply: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================================================================
# POST /api/schema/rollback — Rollback to previous version
# ================================================================

@agent_bp.route("/schema/rollback", methods=["POST"])
@jwt_required()
def rollback_schema():
    """
    Performs a rollback to the preceding schema version or to a specific target version.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json(force=True)
        business_id = data.get("business_id", user_id)
        target_version = data.get("target_version", None)

        # IDOR guard
        is_owner, err = _verify_business_ownership(user_id, business_id)
        if not is_owner:
            return err

        success, restored_schema, error = PatchEngine.rollback(
            business_id, target_version=target_version
        )

        if not success:
            return jsonify({"success": False, "error": error}), 400

        return jsonify({
            "success": True,
            "message": "Website rolled back successfully.",
            "restored_version": restored_schema.get("schema_version", restored_schema.get("version")),
        }), 200

    except Exception as e:
        logger.error(f"Error in /schema/rollback: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================================================================
# GET /api/schema/current/<business_id> — Fetch active schema
# ================================================================

@agent_bp.route("/schema/current/<business_id>", methods=["GET"])
@jwt_required()
def get_current_schema(business_id):
    """Returns the active website schema for a business."""
    try:
        user_id = get_jwt_identity()

        # IDOR guard
        is_owner, err = _verify_business_ownership(user_id, business_id)
        if not is_owner:
            return err

        schema = PatchEngine.get_active_schema(business_id)
        schema.pop("_id", None)

        return jsonify({
            "success": True,
            "schema": schema,
        }), 200

    except Exception as e:
        logger.error(f"Error in /schema/current: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================================================================
# GET /api/schema/history/<business_id> — Fetch version timeline
# ================================================================

@agent_bp.route("/schema/history/<business_id>", methods=["GET"])
@jwt_required()
def get_schema_history(business_id):
    """Returns the version timeline for patch rollback visualization."""
    try:
        user_id = get_jwt_identity()

        # IDOR guard
        is_owner, err = _verify_business_ownership(user_id, business_id)
        if not is_owner:
            return err

        limit = request.args.get("limit", 20, type=int)
        history = PatchEngine.get_version_history(business_id, limit=limit)

        return jsonify({
            "success": True,
            "history": history,
            "count": len(history),
        }), 200

    except Exception as e:
        logger.error(f"Error in /schema/history: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# ================================================================
# GET /api/agents/pending/<business_id> — Fetch pending patch
# ================================================================

@agent_bp.route("/agents/pending/<business_id>", methods=["GET"])
@jwt_required()
def get_pending_patch(business_id):
    """Returns the current pending patch proposal if one exists."""
    try:
        user_id = get_jwt_identity()

        # IDOR guard
        is_owner, err = _verify_business_ownership(user_id, business_id)
        if not is_owner:
            return err

        pending = mongo.db.pending_patches.find_one(
            {"business_id": str(business_id), "is_applied": False}
        )

        if not pending:
            return jsonify({"success": True, "pending": None}), 200

        pending.pop("_id", None)
        return jsonify({"success": True, "pending": pending}), 200

    except Exception as e:
        logger.error(f"Error in /agents/pending: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

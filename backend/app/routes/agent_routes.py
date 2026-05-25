"""
Agent Routes — API Endpoints for the AI Business Copilot System.

Endpoints:
    POST /api/agents/optimize         — Trigger the optimization loop
    POST /api/schema/patch/apply      — Apply the pending patch
    POST /api/schema/rollback         — Rollback to previous version
    GET  /api/schema/current/<id>     — Fetch active website schema
    GET  /api/schema/history/<id>     — Fetch version timeline
"""

import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import mongo
from app.services.copilot_orchestrator import BusinessCopilot
from app.services.patch_engine import PatchEngine
from app.services.business_memory import BusinessMemory

logger = logging.getLogger(__name__)

agent_bp = Blueprint("agent", __name__)


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
    Applies the pending patch stored in MongoDB by the optimization loop.
    This is the human-approval step — the user clicks "Apply Patch" in the drawer.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json(force=True)
        business_id = data.get("business_id", user_id)
        b_id_str = str(business_id)

        # Fetch the pending proposal
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

        # Store positive optimization memory
        BusinessMemory.add_memory(
            business_id=business_id,
            patch_name=patch.get("action", "patch"),
            reason=hypothesis.get("explanation", "Manual optimization"),
            layout_used=str(patch),
            metrics_before=0,
            metrics_after=0,
            conversion_gain=0,
            agent_name="BusinessCopilot",
            patch_outcome="applied",
        )

        return jsonify({
            "success": True,
            "message": "Patch applied successfully. Website updated at the same URL.",
            "new_version": updated_schema.get("schema_version", updated_schema.get("version")),
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
    Performs a 1-click rollback to the preceding schema version.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json(force=True)
        business_id = data.get("business_id", user_id)

        success, restored_schema, error = PatchEngine.rollback(business_id)

        if not success:
            return jsonify({"success": False, "error": error}), 400

        return jsonify({
            "success": True,
            "message": "Website rolled back to previous version successfully.",
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

"""
MongoDB Model Context Protocol (MCP) Server for Break-Even.

Exposes a formal typed tool registry to any MCP Client (e.g. Claude Desktop, Cursor).
Every tool enforces tenant isolation via a mandatory tenant_id parameter
that maps directly to business_id in every MongoDB query.

Tools (8 total):
    ── Core CRUD ──
    1. get_website_schema         — Read active schema
    2. apply_website_patch        — Validate + apply + deploy + capture deploy_ref
    3. rollback_website_schema    — Targeted or single-step rollback

    ── Memory & Intelligence ──
    4. query_business_memory      — RAG retrieval (tenant-isolated)
    5. add_business_memory        — Store optimization event with full patch context
    6. retrieve_conversion_patterns — Cross-business via industry benchmarks
    7. search_layout_successes    — Tenant-scoped success history

    ── Validation & Analysis ──
    8. validate_patch_sandbox     — Standalone sandbox validation (composable)
    9. compare_hypothesis_to_failures — Failure pattern matching
    10. get_business_metrics      — Live analytics + real event data
    11. get_patch_history_by_range — Version range query for rollback analysis
"""

import sys
import os
import json
import logging
from dotenv import load_dotenv

# Load .env before any app imports that read Config
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

from mcp.server.fastmcp import FastMCP

# Ensure the backend root is in the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import create_app
from app.services.patch_engine import PatchEngine
from app.services.patch_validator import PatchValidator
from app.services.business_memory import BusinessMemory

# Initialize logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("breakeven-mcp-server")

# 1. Initialize FastMCP Server
mcp = FastMCP("breakeven-mongodb-mcp")

# 2. Push Flask App Context to access MongoDB PyMongo instance
# Temporarily redirect stdout to stderr to prevent print noise from corrupting standard JSON-RPC transport
sys.stdout = sys.stderr
try:
    logger.info("Initializing Flask app context for MongoDB access...")
    flask_app = create_app()
    # Keep app context active for the lifetime of the process
    ctx = flask_app.app_context()
    ctx.push()
    logger.info("Flask app context successfully pushed.")
except Exception as e:
    logger.error(f"Failed to push Flask app context: {e}")
    sys.exit(1)
finally:
    # Restore standard output stream for clean FastMCP stdio JSON-RPC transport
    sys.stdout = sys.__stdout__


# ====================================================================
# HELPER: Tenant validation
# ====================================================================

def _validate_tenant(tenant_id: str) -> str:
    """Normalizes and validates a tenant/business ID."""
    if not tenant_id or not str(tenant_id).strip():
        raise ValueError("tenant_id (business_id) is required and cannot be empty.")
    return str(tenant_id).strip()


# ====================================================================
# 1. get_website_schema
# ====================================================================

@mcp.tool()
def get_website_schema(tenant_id: str) -> str:
    """
    Retrieves the active website schema (JSON graph representing sections,
    styles, theme, and SEO) for a given business.

    Args:
        tenant_id: The business owner's unique identifier (business_id).
                   Used to scope the query — only returns schemas belonging to this tenant.

    Returns:
        JSON string with the active schema, including schema_version and all sections.
    """
    logger.info(f"MCP Tool called: get_website_schema for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        schema = PatchEngine.get_active_schema(bid)
        schema_copy = dict(schema)
        schema_copy.pop("_id", None)
        if "created_at" in schema_copy:
            schema_copy["created_at"] = str(schema_copy["created_at"])
        if "updated_at" in schema_copy:
            schema_copy["updated_at"] = str(schema_copy["updated_at"])

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "schema": schema_copy
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in get_website_schema: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 2. apply_website_patch
# ====================================================================

@mcp.tool()
def apply_website_patch(tenant_id: str, patch_json: str, patch_metadata_json: str = "{}") -> str:
    """
    Applies a surgical JSON patch to the active website schema.

    The patch is automatically passed through a strict Sandboxed Validator
    to block JavaScript injections, responsive layout corruption, or
    base configuration overrides. Automatically increments version,
    compiles static HTML to disk, deploys to Netlify, and captures deploy_ref.

    Args:
        tenant_id:          Business owner's unique identifier. Scopes schema lookup.
        patch_json:         JSON string of the patch. Example:
                            {"action": "swap_variant", "section_id": "hero_1", "variant": "hero-luxury"}
        patch_metadata_json: Optional metadata. Example:
                            {"trigger_reason": "Low mobile bookings", "agent_name": "PerformanceAgent"}

    Returns:
        JSON with success status, new schema_version, and deploy_ref (if Netlify deployed).
    """
    logger.info(f"MCP Tool called: apply_website_patch for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        patch = json.loads(patch_json)
        metadata = json.loads(patch_metadata_json)

        success, updated_schema, err_msg = PatchEngine.apply_patch(
            business_id=bid,
            patch=patch,
            patch_metadata=metadata
        )

        if not success:
            logger.warning(f"Patch rejected: {err_msg}")
            return json.dumps({
                "success": False,
                "error": f"Patch Validation Rejected: {err_msg}"
            })

        updated_copy = dict(updated_schema)
        updated_copy.pop("_id", None)
        if "created_at" in updated_copy:
            updated_copy["created_at"] = str(updated_copy["created_at"])
        if "updated_at" in updated_copy:
            updated_copy["updated_at"] = str(updated_copy["updated_at"])

        return json.dumps({
            "success": True,
            "message": "Surgical patch validated and applied successfully. Website deployed.",
            "schema_version": updated_copy.get("schema_version"),
            "deploy_ref": updated_copy.get("deploy_ref"),
            "schema": updated_copy
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in apply_website_patch: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 3. rollback_website_schema
# ====================================================================

@mcp.tool()
def rollback_website_schema(tenant_id: str, target_version: int = None) -> str:
    """
    Reverts the active website schema to a specific version or the preceding one.

    Args:
        tenant_id:      Business owner's unique identifier.
        target_version: If provided, restores that exact version number.
                        If omitted, performs single-step undo to the most recent version.

    Returns:
        JSON with success status and the restored schema_version.
    """
    logger.info(f"MCP Tool called: rollback_website_schema for {tenant_id} (target={target_version})")
    try:
        bid = _validate_tenant(tenant_id)
        success, restored_schema, err_msg = PatchEngine.rollback(bid, target_version=target_version)
        if not success:
            return json.dumps({"success": False, "error": err_msg})

        restored_copy = dict(restored_schema)
        restored_copy.pop("_id", None)
        if "created_at" in restored_copy:
            restored_copy["created_at"] = str(restored_copy["created_at"])
        if "updated_at" in restored_copy:
            restored_copy["updated_at"] = str(restored_copy["updated_at"])

        return json.dumps({
            "success": True,
            "message": f"Rollback complete to v{restored_copy.get('schema_version')}.",
            "schema_version": restored_copy.get("schema_version"),
            "schema": restored_copy
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in rollback_website_schema: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 4. query_business_memory
# ====================================================================

@mcp.tool()
def query_business_memory(tenant_id: str, query_phrase: str, limit: int = 3) -> str:
    """
    Queries the vector database for historical high-performing website
    optimization events, layout changes, and conversion deltas.

    Tenant-isolated: only returns memories belonging to this tenant_id.
    If no tenant memories exist, returns industry benchmark patterns.

    Args:
        tenant_id:    Business owner's unique identifier.
        query_phrase: Natural language search query (e.g., "improve booking conversion").
        limit:        Maximum number of results to return (default: 3).

    Returns:
        JSON with matching memories and their similarity scores.
    """
    logger.info(f"MCP Tool called: query_business_memory for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        memories = BusinessMemory.retrieve_relevant_memory(
            business_id=bid,
            query_phrase=query_phrase,
            limit=limit
        )
        for mem in memories:
            if "created_at" in mem:
                mem["created_at"] = str(mem["created_at"])

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "query": query_phrase,
            "memories": memories
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in query_business_memory: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 5. add_business_memory
# ====================================================================

@mcp.tool()
def add_business_memory(
    tenant_id: str,
    patch_name: str,
    reason: str,
    layout_used: str,
    metrics_before: float,
    metrics_after: float,
    conversion_gain: float,
    patch_outcome: str = "success",
    industry_type: str = "general",
    patch_json_str: str = "{}",
    git_ref: str = None,
    deploy_ref: str = None,
) -> str:
    """
    Logs an optimization event outcome in the database memory
    to enable the AI's continuous learning.

    Args:
        tenant_id:       Business owner's unique identifier.
        patch_name:      Short name of the patch (e.g., "hero_cta_above_fold").
        reason:          Why this patch was applied.
        layout_used:     Description of the layout configuration used.
        metrics_before:  Conversion percentage before the patch.
        metrics_after:   Conversion percentage after the patch.
        conversion_gain: The delta improvement.
        patch_outcome:   "success" or "FAILED: <reason>".
        industry_type:   Business vertical ("spa", "law_firm", "general").
        patch_json_str:  JSON string of the actual patch that was applied.
        git_ref:         GitHub commit SHA if versioned.
        deploy_ref:      Netlify deploy ID if published.

    Returns:
        JSON with success status.
    """
    logger.info(f"MCP Tool called: add_business_memory for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        patch_json = json.loads(patch_json_str) if patch_json_str else None

        success = BusinessMemory.add_memory(
            business_id=bid,
            patch_name=patch_name,
            reason=reason,
            layout_used=layout_used,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            conversion_gain=conversion_gain,
            patch_outcome=patch_outcome,
            industry_type=industry_type,
            patch_json=patch_json,
            git_ref=git_ref,
            deploy_ref=deploy_ref,
        )
        return json.dumps({"success": success, "message": "Optimization memory event stored successfully."})
    except Exception as e:
        logger.error(f"Error in add_business_memory: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 6. retrieve_conversion_patterns
# ====================================================================

@mcp.tool()
def retrieve_conversion_patterns(tenant_id: str, industry_type: str = None, limit: int = 5) -> str:
    """
    Returns high-performing conversion patterns: first from this business's
    successful history, then augmented with industry benchmark patterns.

    This is the cold-start intelligence tool — new businesses get proven
    patterns from their industry even before accumulating their own data.

    Args:
        tenant_id:     Business owner's unique identifier.
        industry_type: Industry vertical to query benchmarks for (optional).
        limit:         Maximum results (default: 5).

    Returns:
        JSON with conversion patterns and their sources (own_history or industry_benchmark).
    """
    logger.info(f"MCP Tool called: retrieve_conversion_patterns for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        patterns = BusinessMemory.retrieve_conversion_patterns(
            business_id=bid,
            industry_type=industry_type,
            limit=limit,
        )
        for p in patterns:
            if "created_at" in p:
                p["created_at"] = str(p["created_at"])

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "patterns": patterns,
            "count": len(patterns),
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in retrieve_conversion_patterns: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 7. search_layout_successes
# ====================================================================

@mcp.tool()
def search_layout_successes(tenant_id: str, query_phrase: str, limit: int = 5) -> str:
    """
    Searches for historically successful layout configurations matching the query.
    Tenant-isolated — only returns this business's successful optimization events.

    Args:
        tenant_id:    Business owner's unique identifier.
        query_phrase: Natural language layout query (e.g., "hero with booking CTA").
        limit:        Maximum results (default: 5).

    Returns:
        JSON with matching successful layouts and similarity scores.
    """
    logger.info(f"MCP Tool called: search_layout_successes for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        successes = BusinessMemory.search_layout_successes(
            business_id=bid,
            query_phrase=query_phrase,
            limit=limit,
        )
        for s in successes:
            if "created_at" in s:
                s["created_at"] = str(s["created_at"])

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "query": query_phrase,
            "results": successes,
            "count": len(successes),
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in search_layout_successes: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 8. validate_patch_sandbox
# ====================================================================

@mcp.tool()
def validate_patch_sandbox(tenant_id: str, patch_json: str) -> str:
    """
    Pre-validates a proposed patch WITHOUT applying it.

    This is a standalone composable tool — the orchestrator can call this
    to check a hypothesis BEFORE committing to apply_website_patch.

    Returns a structured report with:
        - valid: bool
        - errors: list of blocking issues
        - warnings: list of advisory notices
        - security_flags: list of detected injection patterns

    Args:
        tenant_id:  Business owner's unique identifier (used to look up active schema).
        patch_json: JSON string of the proposed patch to validate.

    Returns:
        JSON validation report.
    """
    logger.info(f"MCP Tool called: validate_patch_sandbox for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        patch = json.loads(patch_json)

        schema = PatchEngine.get_active_schema(bid)
        schema.pop("_id", None)

        report = PatchValidator.validate_and_report(schema, patch)

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "validation_report": report,
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in validate_patch_sandbox: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 9. compare_hypothesis_to_failures
# ====================================================================

@mcp.tool()
def compare_hypothesis_to_failures(tenant_id: str, hypothesis_text: str, threshold: float = 0.7) -> str:
    """
    Checks whether a proposed hypothesis matches any known FAILED patches.

    The orchestrator calls this BEFORE generating a patch to reject
    hypotheses that resemble previously failed optimizations.

    Args:
        tenant_id:       Business owner's unique identifier.
        hypothesis_text: Natural language description of the proposed change.
        threshold:       Similarity threshold (0.0–1.0). Default 0.7.

    Returns:
        JSON with matching failures (if any) and their similarity scores.
        Empty matches list means the hypothesis is safe to proceed.
    """
    logger.info(f"MCP Tool called: compare_hypothesis_to_failures for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        matches = BusinessMemory.compare_to_failures(
            business_id=bid,
            hypothesis_text=hypothesis_text,
            threshold=threshold,
        )

        for m in matches:
            if "created_at" in m:
                m["created_at"] = str(m["created_at"])

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "hypothesis": hypothesis_text,
            "threshold": threshold,
            "is_safe": len(matches) == 0,
            "failure_matches": matches,
            "match_count": len(matches),
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in compare_hypothesis_to_failures: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 10. get_business_metrics
# ====================================================================

@mcp.tool()
def get_business_metrics(tenant_id: str) -> str:
    """
    Returns aggregated business analytics including QR scans, appointments,
    orders, conversion rates, and real child website engagement data
    from the event collector.

    Args:
        tenant_id: Business owner's unique identifier.

    Returns:
        JSON with comprehensive business metrics and real engagement data.
    """
    logger.info(f"MCP Tool called: get_business_metrics for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)

        from app.services.copilot_orchestrator import BusinessCopilot
        copilot = BusinessCopilot(bid)
        metrics = copilot._tools_analytics_interpreter()

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "metrics": metrics,
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in get_business_metrics: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 11. get_patch_history_by_range
# ====================================================================

@mcp.tool()
def get_patch_history_by_range(tenant_id: str, from_version: int, to_version: int) -> str:
    """
    Returns all patches applied between two version numbers (inclusive).

    Useful for rollback analysis queries like:
    "Show me every patch deployed between v3 and v7 and their conversion outcomes."

    Args:
        tenant_id:    Business owner's unique identifier.
        from_version: Start version number (inclusive).
        to_version:   End version number (inclusive).

    Returns:
        JSON with the list of patches, their metadata, and deploy_refs.
    """
    logger.info(f"MCP Tool called: get_patch_history_by_range for {tenant_id} (v{from_version}–v{to_version})")
    try:
        bid = _validate_tenant(tenant_id)
        patches = PatchEngine.get_patches_by_version_range(bid, from_version, to_version)

        for p in patches:
            if "timestamp" in p:
                p["timestamp"] = str(p["timestamp"])

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "from_version": from_version,
            "to_version": to_version,
            "patches": patches,
            "count": len(patches),
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in get_patch_history_by_range: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 12. create_website
# ====================================================================

@mcp.tool()
def create_website(tenant_id: str, business_info_json: str, platform: str = "netlify") -> str:
    """
    Creates and deploys a new website for a business.

    Generates a JSON schema from the business info, renders premium HTML
    via SchemaRenderer, deploys to Netlify (or GitHub), and stores all
    records (deployed_sites, website_schemas, child_websites).

    Args:
        tenant_id:          Business owner's unique identifier.
        business_info_json: JSON string with business data. Example:
                           {"website_name": "My Spa", "business_type": "spa",
                            "description": "Premium wellness center",
                            "services_products": ["Massage", "Facial"],
                            "phone": "555-0123", "email": "info@myspa.com"}
        platform:           Deployment platform: "netlify" (default) or "github".

    Returns:
        JSON with success status, website_url, and schema_version.
    """
    logger.info(f"MCP Tool called: create_website for {tenant_id} (platform={platform})")
    try:
        bid = _validate_tenant(tenant_id)
        business_info = json.loads(business_info_json)

        from app.services.schema_bridge import SchemaBridge
        from app.services.schema_renderer import SchemaRenderer
        from app.services.tracking_snippet import TrackingSnippet

        # 1. Build schema
        schema = SchemaBridge.build_schema_dict(bid, business_info)

        # 2. Render HTML
        html = SchemaRenderer.render(schema)
        html = TrackingSnippet.inject(html, business_id=bid)

        # 3. Deploy
        deploy_result = {"success": False}
        if platform == "netlify":
            from app.services.netlify_service import NetlifyService
            netlify = NetlifyService()
            site_name = business_info.get("website_name", "mcp-site").lower().replace(" ", "-")
            deploy_result = netlify.create_and_deploy_website(site_name, business_info)
        elif platform == "github":
            from app.services.github_service import GitHubService
            github = GitHubService()
            site_name = business_info.get("website_name", "mcp-site")
            deploy_result = github.create_website_repository(site_name, business_info)

        if not deploy_result.get("success"):
            return json.dumps({
                "success": False,
                "error": f"Deployment failed: {deploy_result.get('error', 'Unknown error')}"
            })

        # 4. Bridge: create schema + child_websites records
        SchemaBridge.create_schema_from_deployment(
            business_id=bid,
            business_info=business_info,
            deploy_result=deploy_result,
            platform=platform,
        )

        # 5. Store in deployed_sites
        from app import mongo
        from datetime import datetime, timezone
        mongo.db.deployed_sites.insert_one({
            "owner_id": bid,
            "website_name": business_info.get("website_name", ""),
            "website_url": deploy_result.get("website_url", ""),
            "platform": platform,
            "deployment_info": deploy_result,
            "business_info": business_info,
            "created_at": datetime.now(timezone.utc),
            "source": "mcp_server",
        })

        return json.dumps({
            "success": True,
            "message": f"Website created and deployed to {platform}.",
            "website_url": deploy_result.get("website_url"),
            "schema_version": 1,
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in create_website: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# 13. get_deployed_sites
# ====================================================================

@mcp.tool()
def get_deployed_sites(tenant_id: str) -> str:
    """
    Returns all deployed websites for a business, with their URLs,
    platforms, schema status, and API keys.

    Args:
        tenant_id: Business owner's unique identifier.

    Returns:
        JSON list of deployed sites with metadata.
    """
    logger.info(f"MCP Tool called: get_deployed_sites for {tenant_id}")
    try:
        bid = _validate_tenant(tenant_id)
        from app import mongo

        sites = list(mongo.db.deployed_sites.find(
            {"$or": [{"owner_id": bid}, {"business_id": bid}]},
            {"deployment_info": 0},  # Exclude heavy deploy data
        ).sort("created_at", -1).limit(20))

        # Check if each site has a matching schema
        has_schema = mongo.db.website_schemas.find_one(
            {"business_id": bid, "is_active": True}
        ) is not None

        results = []
        for s in sites:
            s.pop("_id", None)
            if "created_at" in s:
                s["created_at"] = str(s["created_at"])
            results.append(s)

        return json.dumps({
            "success": True,
            "tenant_id": bid,
            "sites": results,
            "count": len(results),
            "has_active_schema": has_schema,
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in get_deployed_sites: {e}")
        return json.dumps({"success": False, "error": str(e)})


# ====================================================================
# Entry Point
# ====================================================================

if __name__ == "__main__":
    logger.info("Starting breakeven-mongodb-mcp Server stdio loop (13 tools registered)...")
    mcp.run()

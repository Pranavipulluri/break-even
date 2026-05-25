"""
MongoDB Model Context Protocol (MCP) Server for Break-Even.

Exposes standard operational tools to any MCP Client (e.g. Claude Desktop, Cursor).
Allows safe, sandboxed reading, patching, rolling back, and RAG retrieval
for autonomous self-improving websites.
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
# MCP Operational Tools Exposing Python Services
# ====================================================================

@mcp.tool()
def get_website_schema(business_id: str) -> str:
    """
    Retrieves the active website schema (JSON graph representing sections, styles, theme, and SEO)
    for a given business. If no schema exists, a premium default is generated.
    """
    logger.info(f"MCP Tool called: get_website_schema for {business_id}")
    try:
        schema = PatchEngine.get_active_schema(business_id)
        # Convert BSON ObjectIds & Datetimes to JSON compatible structures
        schema_copy = dict(schema)
        schema_copy.pop("_id", None)
        if "created_at" in schema_copy:
            schema_copy["created_at"] = str(schema_copy["created_at"])
        if "updated_at" in schema_copy:
            schema_copy["updated_at"] = str(schema_copy["updated_at"])
        
        return json.dumps({
            "success": True,
            "business_id": business_id,
            "schema": schema_copy
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in get_website_schema: {e}")
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def apply_website_patch(business_id: str, patch_json: str, patch_metadata_json: str = "{}") -> str:
    """
    Applies a surgical JSON patch to the active website schema.
    
    The patch is automatically passed through a strict Sandboxed Validator to block any JavaScript injections,
    responsive layout corruption, or base configuration settings overrides.
    Automatically increments version, compiles static HTML to disk, and retains original URL/QR.
    
    Arguments:
        business_id: Unique business identifier.
        patch_json: JSON string representing the surgical update. e.g. {"action": "swap_variant", "section_id": "hero_1", "variant": "hero-luxury"}
        patch_metadata_json: Optional metadata, e.g. {"trigger_reason": "Low mobile bookings", "agent_name": "PerformanceAgent"}
    """
    logger.info(f"MCP Tool called: apply_website_patch for {business_id}")
    try:
        patch = json.loads(patch_json)
        metadata = json.loads(patch_metadata_json)
        
        success, updated_schema, err_msg = PatchEngine.apply_patch(
            business_id=business_id,
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
            "schema": updated_copy
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in apply_website_patch: {e}")
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def rollback_website_schema(business_id: str) -> str:
    """
    Reverts the active website schema to the immediately preceding version in the historical record.
    Forces static compilation and redeployments automatically.
    """
    logger.info(f"MCP Tool called: rollback_website_schema for {business_id}")
    try:
        success, restored_schema, err_msg = PatchEngine.rollback(business_id)
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
            "message": "Successful 1-click rollback to preceding version complete.",
            "schema_version": restored_copy.get("schema_version"),
            "schema": restored_copy
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in rollback_website_schema: {e}")
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def query_business_memory(business_id: str, query_phrase: str, limit: int = 3) -> str:
    """
    Queries the vector database for historical high-performing website optimization events, layout changes,
    and conversion deltas to help the AI form high-probability success hypotheses.
    """
    logger.info(f"MCP Tool called: query_business_memory for {business_id}")
    try:
        memories = BusinessMemory.retrieve_relevant_memory(
            business_id=business_id,
            query_phrase=query_phrase,
            limit=limit
        )
        # Convert created_at datetimes
        for mem in memories:
            if "created_at" in mem:
                mem["created_at"] = str(mem["created_at"])
                
        return json.dumps({
            "success": True,
            "query": query_phrase,
            "memories": memories
        }, indent=2)
    except Exception as e:
        logger.error(f"Error in query_business_memory: {e}")
        return json.dumps({"success": False, "error": str(e)})

@mcp.tool()
def add_business_memory(
    business_id: str,
    patch_name: str,
    reason: str,
    layout_used: str,
    metrics_before: float,
    metrics_after: float,
    conversion_gain: float,
    patch_outcome: str = "success"
) -> str:
    """
    Logs an optimization event outcome (metrics progress or validation failures) in the database memory 
    to enable the AI's continuous learning.
    """
    logger.info(f"MCP Tool called: add_business_memory for {business_id}")
    try:
        success = BusinessMemory.add_memory(
            business_id=business_id,
            patch_name=patch_name,
            reason=reason,
            layout_used=layout_used,
            metrics_before=metrics_before,
            metrics_after=metrics_after,
            conversion_gain=conversion_gain,
            patch_outcome=patch_outcome
        )
        return json.dumps({"success": success, "message": "Optimization memory event stored successfully."})
    except Exception as e:
        logger.error(f"Error in add_business_memory: {e}")
        return json.dumps({"success": False, "error": str(e)})

if __name__ == "__main__":
    logger.info("Starting breakeven-mongodb-mcp Server stdio loop...")
    mcp.run()

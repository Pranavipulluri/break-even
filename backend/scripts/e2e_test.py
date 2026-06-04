"""
Break-Even End-to-End Flow Test
================================
Tests all 8 subsystems in sequence against the local stack.
Requires: Backend running on port 5000, MongoDB on port 27017.

Usage:
    cd backend
    python ../scripts/e2e_test.py
"""

import requests
import json
import time
import sys
from datetime import datetime
from pymongo import MongoClient

# ================================================================
# Configuration
# ================================================================

BASE_URL = "http://localhost:5000/api"
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "breakeven"

# Test user credentials
TEST_EMAIL = f"e2e_test_{int(time.time())}@breakeven.test"
TEST_PASSWORD = "TestPass123!"
TEST_NAME = "E2E Test Owner"

# Track state across steps
state = {}
results = {"passed": 0, "failed": 0, "errors": []}


def section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def check(label, condition, detail=""):
    if condition:
        print(f"  ✅ {label}")
        results["passed"] += 1
    else:
        print(f"  ❌ {label}")
        if detail:
            print(f"     → {detail}")
        results["failed"] += 1
        results["errors"].append(f"{label}: {detail}")


def api(method, path, data=None, token=None, expect_status=None):
    """Make an API call and return (status_code, response_json)."""
    url = f"{BASE_URL}{path}"
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            r = requests.post(url, json=data, headers=headers, timeout=60)
        elif method == "PUT":
            r = requests.put(url, json=data, headers=headers, timeout=30)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, timeout=30)
        else:
            return None, {"error": f"Unknown method {method}"}

        try:
            body = r.json()
        except Exception:
            body = {"_raw": r.text[:500]}

        if expect_status and r.status_code != expect_status:
            print(f"  ⚠️  Expected HTTP {expect_status}, got {r.status_code}")
            print(f"     Response: {json.dumps(body, indent=2)[:300]}")

        return r.status_code, body
    except requests.exceptions.ConnectionError:
        print(f"  💥 Connection refused — is the backend running on port 5000?")
        return None, {"error": "Connection refused"}
    except Exception as e:
        return None, {"error": str(e)}


# ================================================================
# Pre-flight: Check MongoDB and Backend
# ================================================================

def preflight():
    section("PRE-FLIGHT CHECKS")

    # MongoDB
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        client.server_info()
        db = client[DB_NAME]
        collections = db.list_collection_names()
        print(f"  ✅ MongoDB connected — {len(collections)} collections in '{DB_NAME}'")
        state["db"] = db
        state["mongo_client"] = client
    except Exception as e:
        print(f"  💥 MongoDB connection failed: {e}")
        print("     Start MongoDB: mongod --dbpath <your_path>")
        sys.exit(1)

    # Backend
    status, body = api("GET", "/auth/health")
    if status is None:
        # Try a simpler endpoint
        try:
            r = requests.get(f"{BASE_URL.replace('/api', '')}/", timeout=5)
            print(f"  ✅ Backend reachable (root: {r.status_code})")
        except Exception:
            print(f"  💥 Backend not reachable on port 5000")
            print("     Start it: cd backend && python run.py")
            sys.exit(1)
    else:
        print(f"  ✅ Backend API reachable (status={status})")


# ================================================================
# Step 0: Register + Login
# ================================================================

def step0_register_and_login():
    section("STEP 0 — Register & Login Demo Business Owner")

    # Register
    status, body = api("POST", "/auth/register", {
        "name": TEST_NAME,
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD,
        "business_name": "Serenity Day Spa",
        "business_type": "spa",
    })

    if status == 201 and body.get("token"):
        state["token"] = body["token"]
        state["user_id"] = body.get("user", {}).get("_id", "")
        print(f"  ✅ Registered: {TEST_EMAIL}")
        print(f"     user_id: {state['user_id']}")
    elif status == 400 and "exists" in str(body.get("error", "")).lower():
        # Already exists, try login
        print(f"  ⚠️  User exists, logging in...")
        status, body = api("POST", "/auth/login", {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        })
        if body.get("token"):
            state["token"] = body["token"]
            state["user_id"] = body.get("user", {}).get("_id", "")
            print(f"  ✅ Logged in: {TEST_EMAIL}")
            print(f"     user_id: {state['user_id']}")
        else:
            print(f"  ❌ Login failed: {body}")
            sys.exit(1)
    else:
        print(f"  ❌ Register failed: status={status}, body={json.dumps(body)[:300]}")
        sys.exit(1)

    check("Token obtained", bool(state.get("token")))
    check("User ID obtained", bool(state.get("user_id")))


# ================================================================
# Step 1: Child Website Creation
# ================================================================

def step1_child_website():
    section("STEP 1 — Child Website Creation (spa)")

    token = state["token"]
    user_id = state["user_id"]

    # Create website via the dev-create endpoint first (no auth issues)
    business_info = {
        "website_name": "Serenity Day Spa",
        "business_type": "spa",
        "color_theme": "elegant",
        "description": "Premium wellness and beauty center offering luxury spa treatments",
        "area": "Downtown LA",
        "contact_info": {
            "email": TEST_EMAIL,
            "phone": "555-0199",
            "address": "123 Spa Lane",
        },
        "services_products": "Swedish Massage, Deep Tissue Massage, Aromatherapy Facial, Hot Stone Therapy",
        "unique_selling_points": "Organic products, Expert therapists, Luxury ambiance",
    }

    # Try the JWT-protected endpoint first
    status, body = api("POST", "/website-builder/create", business_info, token=token)

    print(f"  API /website-builder/create: status={status}")
    if status == 500 or status is None:
        # Fallback: use the deploy endpoint which creates via SchemaBridge
        print(f"  ⚠️  Create endpoint error: {body.get('error', 'unknown')[:100]}")
        print(f"  ℹ️  Falling back to /ai-tools/dev/netlify-deploy...")
        status, body = api("POST", "/ai-tools/dev/netlify-deploy", {
            "site_name": "Serenity Day Spa",
            "business_info": business_info,
        }, token=token)
        print(f"  API /ai-tools/dev/netlify-deploy: status={status}")

    if body.get("error"):
        err_msg = body['error']
        if isinstance(err_msg, str) and ("already" in err_msg.lower() or "exists" in err_msg.lower()):
            print(f"  ℹ️  Website already exists — checking DB directly")
        else:
            print(f"  ⚠️  Error: {err_msg[:150]}")

    # Verify in MongoDB
    db = state["db"]

    child = db.child_websites.find_one({"owner_id": user_id})
    if not child:
        # Try with ObjectId
        from bson import ObjectId
        try:
            child = db.child_websites.find_one({"owner_id": ObjectId(user_id)})
        except Exception:
            pass

    check("child_websites document exists", child is not None,
          f"owner_id={user_id}" if not child else "")

    if child:
        check("owner_id matches", str(child.get("owner_id")) == user_id or str(child.get("owner_id")) == str(user_id))
        check("has website_name", bool(child.get("website_name")))
        print(f"     website_name: {child.get('website_name')}")
        print(f"     business_type: {child.get('business_type')}")
        print(f"     website_url: {child.get('website_url', 'N/A')}")
        print(f"     netlify_site_id: {child.get('netlify_site_id', 'N/A')}")
        print(f"     api_key: {child.get('api_key', 'N/A')[:20]}..." if child.get('api_key') else "     api_key: N/A")

    # Check website_schemas
    schema = db.website_schemas.find_one({"business_id": user_id, "is_active": True})
    if not schema:
        schema = db.website_schemas.find_one({"business_id": str(user_id), "is_active": True})

    check("website_schemas document exists", schema is not None)

    if schema:
        check("schema has sections", len(schema.get("sections", [])) > 0,
              f"sections count: {len(schema.get('sections', []))}")
        check("schema has theme", bool(schema.get("theme")))
        check("schema has seo", bool(schema.get("seo")))
        check("schema is_active = True", schema.get("is_active") == True)
        print(f"     schema_version: {schema.get('schema_version', schema.get('version', '?'))}")
        print(f"     palette: {schema.get('theme', {}).get('palette', '?')}")
        print(f"     sections: {[s.get('type') for s in schema.get('sections', [])]}")

        # Check if services made it into the schema
        services_section = next((s for s in schema.get("sections", []) if s.get("type") == "services"), None)
        if services_section:
            items = services_section.get("content", {}).get("items", [])
            check("services_products parsed into schema",
                  len(items) > 0,
                  f"Found {len(items)} service items: {[i.get('name') for i in items[:3]]}")
        else:
            check("services section exists in schema", False, "No services section found")

    state["schema"] = schema


# ================================================================
# Step 2: Dashboard Data Flow
# ================================================================

def step2_dashboard():
    section("STEP 2 — Dashboard Data Flow")

    token = state["token"]

    status, body = api("GET", "/dashboard/stats", token=token)

    check("Dashboard endpoint responds", status == 200, f"status={status}")

    if status == 200:
        print(f"  Response keys: {list(body.keys())[:10]}")
        # Check what fields are returned
        for key in ["revenue", "total_revenue", "qr_scans", "total_scans", "customers",
                     "total_customers", "products", "total_products", "stats"]:
            if key in body:
                print(f"     {key}: {body[key]}")

        # Even if values are 0, the endpoint should return structured data
        check("Returns structured data", isinstance(body, dict) and len(body) > 0)


# ================================================================
# Step 3: Products
# ================================================================

def step3_products():
    section("STEP 3 — Products CRUD")

    token = state["token"]
    user_id = state["user_id"]

    # Add product 1
    status1, body1 = api("POST", "/products", {
        "name": "Swedish Massage - 60min",
        "price": 89.99,
        "stock": 100,
        "description": "Full body relaxation massage with essential oils",
        "category": "massage",
    }, token=token)

    check("Product 1 created", status1 in [200, 201],
          f"status={status1}, body={json.dumps(body1)[:200]}")

    if isinstance(body1, dict):
        state["product1_id"] = body1.get("product", {}).get("_id") or body1.get("_id")

    # Add product 2
    status2, body2 = api("POST", "/products", {
        "name": "Hot Stone Therapy - 90min",
        "price": 129.99,
        "stock": 50,
        "description": "Therapeutic heated stone placement and massage",
        "category": "therapy",
    }, token=token)

    check("Product 2 created", status2 in [200, 201],
          f"status={status2}")

    # Fetch products
    status3, body3 = api("GET", "/products", token=token)
    check("GET /products responds", status3 == 200, f"status={status3}")

    if status3 == 200:
        if isinstance(body3, list):
            products = body3
        elif isinstance(body3, dict):
            products = body3.get("products", [])
        else:
            products = []
        check("At least 2 products returned",
              len(products) >= 2,
              f"Got {len(products)} products")

    # Verify in MongoDB
    db = state["db"]
    from bson import ObjectId
    mongo_products = list(db.products.find({"user_id": user_id}))
    if not mongo_products:
        try:
            mongo_products = list(db.products.find({"user_id": ObjectId(user_id)}))
        except Exception:
            pass

    check("Products in MongoDB with correct user_id",
          len(mongo_products) >= 2,
          f"Found {len(mongo_products)} products for user {user_id}")


# ================================================================
# Step 4: MCP Optimization Loop (Agent)
# ================================================================

def step4_agent_optimize():
    section("STEP 4 — AI Copilot Optimization Loop")

    token = state["token"]
    user_id = state["user_id"]

    print("  ⏳ Triggering optimization (this may take 15-30s for Gemini)...")

    status, body = api("POST", "/agents/optimize", {
        "command": "Optimize the spa website hero section for better booking conversions",
        "business_id": user_id,
    }, token=token)

    check("Optimization endpoint responds", status in [200, 400],
          f"status={status}")

    if body.get("success"):
        check("Optimization successful", True)
        check("Has hypothesis", bool(body.get("hypothesis")))
        check("Has proposed_patch", bool(body.get("proposed_patch")))
        check("Has delta", bool(body.get("delta")))
        check("Has expected_impact", bool(body.get("expected_impact")))
        check("Has confidence score", body.get("confidence") is not None)

        print(f"     hypothesis: {body.get('hypothesis', {}).get('explanation', 'N/A')[:100]}")
        print(f"     expected_impact: {body.get('expected_impact')}")
        print(f"     confidence: {body.get('confidence')}")
        print(f"     patch action: {body.get('proposed_patch', {}).get('action', 'N/A')}")

        delta = body.get("delta", {})
        if delta:
            print(f"     delta section: {delta.get('section_id', 'N/A')}")
            if delta.get("before"):
                print(f"     before title: {delta['before'].get('content', {}).get('title', 'N/A')[:60]}")
            if delta.get("after"):
                print(f"     after title: {delta['after'].get('content', {}).get('title', 'N/A')[:60]}")

        state["optimization_result"] = body
    else:
        check("Optimization successful", False,
              f"Error: {body.get('error', 'Unknown')[:200]}")

    # Check pending_patches in MongoDB
    db = state["db"]
    pending = db.pending_patches.find_one({"business_id": user_id})
    check("pending_patches document created", pending is not None)
    if pending:
        check("pending is_applied = False", pending.get("is_applied") == False)
        print(f"     pending patch timestamp: {pending.get('timestamp', 'N/A')}")


# ================================================================
# Step 5: Apply Patch
# ================================================================

def step5_apply_patch():
    section("STEP 5 — Apply Pending Patch")

    token = state["token"]
    user_id = state["user_id"]
    db = state["db"]

    # Get current version before apply
    schema_before = db.website_schemas.find_one({"business_id": user_id, "is_active": True})
    version_before = schema_before.get("schema_version", schema_before.get("version", 1)) if schema_before else 0
    print(f"  Schema version before: {version_before}")

    # Apply (no patch body = pending approval mode)
    status, body = api("POST", "/schema/patch/apply", {
        "business_id": user_id,
    }, token=token)

    check("Patch apply endpoint responds", status in [200, 400],
          f"status={status}")

    if body.get("success"):
        check("Patch applied successfully", True)
        new_version = body.get("updated_schema", {}).get("schema_version",
                       body.get("updated_schema", {}).get("version", "?"))
        check("Version incremented",
              new_version is not None and new_version != version_before,
              f"v{version_before} → v{new_version}")
        state["version_before_rollback"] = version_before

        print(f"     new schema_version: {new_version}")
        print(f"     deploy_ref: {body.get('updated_schema', {}).get('deploy_ref', 'N/A')}")
    else:
        check("Patch applied successfully", False,
              f"Error: {body.get('error', 'Unknown')[:200]}")

    # Verify pending_patches marked as applied
    pending = db.pending_patches.find_one({"business_id": user_id})
    if pending:
        check("pending_patches is_applied = True", pending.get("is_applied") == True,
              f"is_applied={pending.get('is_applied')}")

    # Check website_history
    history_count = db.website_history.count_documents({"business_id": user_id})
    check("website_history has records", history_count > 0,
          f"Found {history_count} history entries")

    # Check business_memory
    memory = db.business_memory.find_one({"business_id": user_id})
    if memory:
        check("business_memory record exists", True)
        check("business_memory has industry_type",
              bool(memory.get("industry_type")),
              f"industry_type={memory.get('industry_type')}")
        check("business_memory has patch_json",
              memory.get("patch_json") is not None)

        metrics_before = memory.get("metrics_before", {})
        print(f"     industry_type: {memory.get('industry_type')}")
        print(f"     patch_name: {memory.get('patch_name')}")
        print(f"     metrics_before: {metrics_before}")
    else:
        check("business_memory record exists", False,
              "No business_memory found — memory may be stored under different key")
        # Check alternate locations
        alt_memory = list(db.business_memory.find().limit(3))
        if alt_memory:
            print(f"     ℹ️  Found {len(alt_memory)} total memory records")
            for m in alt_memory:
                print(f"        bid={m.get('business_id')}, type={m.get('memory_type')}")


# ================================================================
# Step 6: Rollback
# ================================================================

def step6_rollback():
    section("STEP 6 — Schema Rollback")

    token = state["token"]
    user_id = state["user_id"]
    db = state["db"]

    # Get current version
    schema_now = db.website_schemas.find_one({"business_id": user_id, "is_active": True})
    current_version = schema_now.get("schema_version", schema_now.get("version", 1)) if schema_now else 0
    target_version = state.get("version_before_rollback", current_version - 1)

    print(f"  Current version: {current_version}")
    print(f"  Rollback target: {target_version}")

    status, body = api("POST", "/schema/rollback", {
        "business_id": user_id,
        "target_version": target_version,
    }, token=token)

    check("Rollback endpoint responds", status in [200, 400],
          f"status={status}")

    if body.get("success"):
        check("Rollback successful", True)
        restored_version = body.get("restored_schema", {}).get("schema_version",
                            body.get("restored_schema", {}).get("version", "?"))
        print(f"     Restored to version: {restored_version}")
    else:
        check("Rollback successful", False,
              f"Error: {body.get('error', 'Unknown')[:200]}")

    # Verify in MongoDB
    schema_after = db.website_schemas.find_one({"business_id": user_id, "is_active": True})
    if schema_after:
        final_version = schema_after.get("schema_version", schema_after.get("version", "?"))
        print(f"     Final schema version in DB: {final_version}")

    # Check website_history has the rollback entry
    history_count = db.website_history.count_documents({"business_id": user_id})
    check("website_history has rollback entry", history_count > 0,
          f"Total history entries: {history_count}")


# ================================================================
# Step 7: Analytics Events
# ================================================================

def step7_analytics_events():
    section("STEP 7 — Analytics Event Ingestion")

    user_id = state["user_id"]
    db = state["db"]

    # Check if child_websites has an API key for this business
    child = db.child_websites.find_one({"owner_id": user_id})
    api_key = child.get("api_key") if child else None
    headers_extra = {}
    if api_key:
        headers_extra["X-BE-Key"] = api_key

    events = [
        {"event_type": "page_view", "event_data": {"page": "/"}},
        {"event_type": "cta_click", "event_data": {"text": "Book Now", "element": "BUTTON"}},
        {"event_type": "bounce", "event_data": {"time_on_page_seconds": 3}},
    ]

    for ev in events:
        payload = {
            "business_id": user_id,
            "event_type": ev["event_type"],
            "event_data": ev["event_data"],
            "source_url": "https://test-spa.netlify.app",
            "timestamp": datetime.utcnow().isoformat(),
        }

        url = f"{BASE_URL}/events/ingest"
        h = {"Content-Type": "application/json"}
        h.update(headers_extra)
        try:
            r = requests.post(url, json=payload, headers=h, timeout=10)
            check(f"Ingest {ev['event_type']}", r.status_code == 200,
                  f"status={r.status_code}, body={r.text[:100]}")
        except Exception as e:
            check(f"Ingest {ev['event_type']}", False, str(e))

    # Wait for flush (EventCollector has 10s buffer)
    print("  ⏳ Waiting 12s for EventCollector flush...")
    time.sleep(12)

    # Verify in MongoDB
    events_count = db.analytics_events.count_documents({"business_id": user_id})
    # Also check 'events' collection as alternate name
    if events_count == 0:
        events_count = db.events.count_documents({"business_id": user_id})

    check("Events stored in MongoDB", events_count >= 3,
          f"Found {events_count} events")

    # Get summary
    token = state["token"]
    status, body = api("GET", f"/events/summary/{user_id}", token=token)

    check("Summary endpoint responds", status == 200, f"status={status}")

    if status == 200 and body.get("success"):
        summary = body.get("summary", body)
        print(f"     Summary: {json.dumps(summary, indent=2)[:300]}")
        check("page_view count > 0",
              summary.get("page_view", 0) > 0,
              f"page_view={summary.get('page_view', 0)}")
        check("cta_click count > 0",
              summary.get("cta_click", 0) > 0,
              f"cta_click={summary.get('cta_click', 0)}")
        check("bounce count > 0",
              summary.get("bounce", 0) > 0,
              f"bounce={summary.get('bounce', 0)}")
    elif status == 200:
        print(f"     Raw response: {json.dumps(body)[:300]}")


# ================================================================
# Step 8: RAG Memory Check
# ================================================================

def step8_rag_memory():
    section("STEP 8 — RAG Business Memory Check")

    user_id = state["user_id"]
    db = state["db"]

    memories = list(db.business_memory.find({"business_id": user_id}))

    check("business_memory has records", len(memories) > 0,
          f"Found {len(memories)} records")

    if memories:
        latest = memories[-1]  # Most recent

        check("metrics_before is not empty/zero",
              bool(latest.get("metrics_before")),
              f"metrics_before={latest.get('metrics_before')}")

        check("patch_json is not null",
              latest.get("patch_json") is not None,
              f"patch_json type: {type(latest.get('patch_json'))}")

        check("industry_type is 'spa'",
              latest.get("industry_type") == "spa",
              f"industry_type={latest.get('industry_type')}")

        # Check vector field
        vector = latest.get("vector")
        if vector and isinstance(vector, list):
            check("vector field has 768 dimensions",
                  len(vector) == 768,
                  f"vector dimensions: {len(vector)}")
        else:
            check("vector field exists",
                  vector is not None,
                  f"vector type: {type(vector)}, value: {str(vector)[:50] if vector else 'None'}")

        print(f"     memory_type: {latest.get('memory_type')}")
        print(f"     patch_name: {latest.get('patch_name')}")
        print(f"     industry_type: {latest.get('industry_type')}")
        print(f"     metrics_before: {latest.get('metrics_before')}")
        if vector:
            print(f"     vector dims: {len(vector) if isinstance(vector, list) else 'N/A'}")
    else:
        print("  ℹ️  No business_memory records. This could mean:")
        print("     - The optimization loop used the fallback (no Gemini API key)")
        print("     - Memory is stored in a different collection")

        # Check alternate memory locations
        for coll_name in ["optimization_memory", "agent_memory", "patch_memory"]:
            count = db[coll_name].count_documents({"business_id": user_id})
            if count > 0:
                print(f"     Found {count} records in '{coll_name}'")


# ================================================================
# Cleanup helper (optional)
# ================================================================

def cleanup():
    """Remove test data. Call manually if needed."""
    db = state.get("db")
    if not db:
        return
    user_id = state.get("user_id", "")
    from bson import ObjectId

    for coll in ["child_websites", "website_schemas", "pending_patches",
                 "website_history", "business_memory", "deployed_sites",
                 "analytics_events", "events", "products"]:
        db[coll].delete_many({"business_id": user_id})
        db[coll].delete_many({"owner_id": user_id})
        try:
            db[coll].delete_many({"user_id": user_id})
            db[coll].delete_many({"user_id": ObjectId(user_id)})
        except Exception:
            pass

    try:
        db.users.delete_one({"_id": ObjectId(user_id)})
    except Exception:
        pass

    print(f"\n  🧹 Cleaned up test data for user {user_id}")


# ================================================================
# Main
# ================================================================

def main():
    print("\n" + "🔬 " * 20)
    print("  BREAK-EVEN END-TO-END FLOW TEST")
    print("🔬 " * 20)

    start = time.time()

    try:
        preflight()
        step0_register_and_login()
        step1_child_website()
        step2_dashboard()
        step3_products()
        step4_agent_optimize()
        step5_apply_patch()
        step6_rollback()
        step7_analytics_events()
        step8_rag_memory()
    except KeyboardInterrupt:
        print("\n\n  ⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n  💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()

    elapsed = round(time.time() - start, 1)

    # Summary
    section("RESULTS")
    total = results["passed"] + results["failed"]
    print(f"  ✅ Passed: {results['passed']}/{total}")
    print(f"  ❌ Failed: {results['failed']}/{total}")
    print(f"  ⏱️  Time:   {elapsed}s")

    if results["errors"]:
        print(f"\n  Failures:")
        for err in results["errors"]:
            print(f"    → {err}")

    print()

    # Close MongoDB
    if state.get("mongo_client"):
        state["mongo_client"].close()

    return 0 if results["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

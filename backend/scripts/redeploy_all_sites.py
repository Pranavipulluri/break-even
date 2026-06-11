"""
Redeploy All Sites Script: Force compiles and deploys all active schemas to Netlify and disk.

Usage:
    cd backend
    python -m scripts.redeploy_all_sites
"""

import sys
import os

# Ensure the backend root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.services.schema_renderer import SchemaRenderer
from app.services.patch_engine import PatchEngine


def redeploy_sites():
    app = create_app()

    with app.app_context():
        from app import mongo

        # Find all active schemas
        schemas = list(mongo.db.website_schemas.find({"is_active": True}))
        print(f"\n📊 Found {len(schemas)} active schemas to redeploy")

        success_count = 0
        error_count = 0

        for schema in schemas:
            business_id = schema.get("business_id")
            if not business_id:
                continue

            try:
                print(f"🔄 Redeploying website for business {business_id}...")
                rendered_html = SchemaRenderer.render(schema)

                # Write to disk
                PatchEngine.write_website_to_disk(business_id, rendered_html)

                # Deploy to Netlify
                deploy_ref = PatchEngine._deploy_to_netlify(business_id, rendered_html)
                if deploy_ref:
                    print(f"  ✅ Netlify deploy successful for business {business_id} (ref={deploy_ref})")
                    success_count += 1
                else:
                    print(f"  ⚠️  Netlify deploy skipped/failed for business {business_id}")
                    success_count += 1
            except Exception as e:
                print(f"  ❌ Error redeploying business {business_id}: {e}")
                error_count += 1

        print(f"\nRedeploy complete: {success_count} succeeded, {error_count} failed.\n")


if __name__ == "__main__":
    redeploy_sites()

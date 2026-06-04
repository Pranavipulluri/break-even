"""
Migration Script: Backfill website_schemas for existing deployed_sites.

Usage:
    cd backend
    python -m scripts.migrate_schemas

For each deployed_sites record that has no matching website_schemas entry:
1. Extract business_info from the deployed_sites record
2. Call SchemaBridge.build_schema_dict() to generate a schema
3. Insert into website_schemas
4. Update child_websites with netlify_site_id if available
"""

import sys
import os

# Ensure the backend root is in the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

from app import create_app
from app.services.schema_bridge import SchemaBridge


def run_migration():
    """Backfill website_schemas for all existing deployed_sites."""
    app = create_app()

    with app.app_context():
        from app import mongo

        # Find all deployed sites
        deployed_sites = list(mongo.db.deployed_sites.find())
        print(f"\n📊 Found {len(deployed_sites)} deployed sites")

        migrated = 0
        skipped = 0
        errors = 0

        for site in deployed_sites:
            try:
                # Determine the business_id
                business_id = (
                    site.get("owner_id")
                    or site.get("business_id")
                    or str(site.get("_id", ""))
                )

                if not business_id:
                    print(f"  ⚠️  Skip: no business_id for site '{site.get('website_name', 'unknown')}'")
                    skipped += 1
                    continue

                b_id_str = str(business_id)

                # Check if schema already exists
                existing_schema = mongo.db.website_schemas.find_one(
                    {"business_id": b_id_str, "is_active": True}
                )
                if existing_schema:
                    print(f"  ⏭️  Skip: schema already exists for business {b_id_str}")
                    skipped += 1
                    continue

                # Extract business_info
                business_info = site.get("business_info") or {}
                if not business_info:
                    # Try to reconstruct from other fields
                    business_info = {
                        "website_name": site.get("website_name") or site.get("title") or site.get("site_name", ""),
                        "description": site.get("description", ""),
                    }

                # Build deploy_result equivalent
                deploy_result = site.get("deployment_info") or {}
                deploy_result.setdefault("website_url", site.get("website_url", ""))

                platform = site.get("platform", "netlify")

                # Create the schema via SchemaBridge
                result = SchemaBridge.create_schema_from_deployment(
                    business_id=b_id_str,
                    business_info=business_info,
                    deploy_result=deploy_result,
                    platform=platform,
                )

                if result:
                    site_name = business_info.get("website_name") or site.get("website_name", "unknown")
                    print(f"  ✅ Migrated: {site_name} (business={b_id_str})")
                    migrated += 1
                else:
                    print(f"  ❌ Failed: business {b_id_str}")
                    errors += 1

            except Exception as e:
                print(f"  ❌ Error: {e}")
                errors += 1

        print(f"\n{'='*50}")
        print(f"Migration complete!")
        print(f"  ✅ Migrated: {migrated}")
        print(f"  ⏭️  Skipped:  {skipped}")
        print(f"  ❌ Errors:   {errors}")
        print(f"  📊 Total:    {len(deployed_sites)}")
        print(f"{'='*50}\n")


if __name__ == "__main__":
    run_migration()

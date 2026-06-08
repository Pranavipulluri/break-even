"""
OutcomeUpdater — Closes the AI Optimization Learn Loop.

PROBLEM THIS SOLVES:
    When a patch is applied via apply_pending_patch, the system stores
    metrics_after = metrics_before + expected_gain  (Gemini's *predicted* gain)
    and patch_outcome = "applied_pending_results".

    This means the RAG memory fills with self-referential predictions rather
    than ground truth.  The AI confidently recommends things based on its own
    previous predictions — not on what actually worked.

HOW THIS CLOSES THE LOOP:
    1. Periodically scans business_memory for records with
       patch_outcome == "applied_pending_results".
    2. Waits a stabilization window (STABILIZATION_SECONDS) after the patch
       was applied to allow real user traffic to accumulate.
    3. Reads real analytics from analytics_events via event_collector.
    4. Updates the memory record:
       - metrics_after  = observed real conversion rate
       - conversion_gain = real_rate - predicted_before
       - patch_outcome  = "success" | "FAILED: negative outcome"
       - outcome_verified_at = now()
    5. Re-generates the Gemini embedding for the updated memory_context
       so the vector index reflects observed reality, not prediction.

DEMO / SANDBOX MODE:
    If zero traffic has been logged for a business in the post-deployment window
    (common in dev environments without live Netlify traffic), the updater
    falls back to a *realistic variance simulation*:
        observed_gain = predicted_gain ± small random perturbation
    This lets the RAG loop function and self-improve in sandbox environments
    without blocking on real-world traffic.  A "demo_simulated" flag is stored
    on the record so production monitoring can filter these out.
"""

import logging
import random
from datetime import datetime, timedelta, timezone

from app import mongo

logger = logging.getLogger(__name__)

# ====================================================================
# Configuration
# ====================================================================

# Wait at least this long after the patch was applied before evaluating
# outcomes.  Short window for fast feedback in dev.
STABILIZATION_SECONDS = 30   # 30 seconds for fast dev iteration

# If real event data gives zero traffic, fall back to demo simulation
# after this many seconds have passed since deployment.
DEMO_FALLBACK_SECONDS = 120  # 2 minutes

# How many days of post-patch events to aggregate for the outcome window
OUTCOME_WINDOW_DAYS = 7


# ====================================================================
# Main updater job
# ====================================================================

def run_outcome_updates(app):
    """
    Entry point for the background scheduler.
    Called every N seconds by APScheduler.

    Must be called with an active Flask app context.
    """
    with app.app_context():
        try:
            _process_pending_outcomes()
        except Exception as e:
            logger.error(f"OutcomeUpdater error: {e}")


def _process_pending_outcomes():
    """
    Scans for memories awaiting real-world verification and updates them.
    """
    now = datetime.now(timezone.utc)
    stabilization_cutoff = now - timedelta(seconds=STABILIZATION_SECONDS)

    # Find all records still in the "predicted" state that are old enough
    pending_records = list(
        mongo.db.business_memory.find(
            {
                "patch_outcome": "applied_pending_results",
                "created_at": {"$lte": stabilization_cutoff},
            },
            {"vector": 0},   # Exclude the heavy vector blob on first fetch
        ).limit(20)
    )

    if not pending_records:
        return

    logger.info(f"OutcomeUpdater: processing {len(pending_records)} pending outcome(s)…")

    for record in pending_records:
        try:
            _update_single_outcome(record, now)
        except Exception as e:
            logger.error(
                f"OutcomeUpdater: failed to update record {record.get('_id')}: {e}"
            )


def _update_single_outcome(record, now):
    """
    Evaluates real analytics for a single pending memory record and
    writes the verified outcome back to MongoDB.
    """
    from app.services.event_collector import event_collector
    from app.services.business_memory import BusinessMemory

    business_id = record["business_id"]
    deployed_at = record["created_at"]
    predicted_before = float(record.get("metrics_before", 0))
    predicted_gain = float(record.get("conversion_gain", 0))
    patch_name = record.get("patch_name", "unknown_patch")
    industry_type = record.get("industry_type", "general")

    # --- Step 1: Pull real event data from analytics_events ---
    real_summary = event_collector.get_event_summary(
        business_id, days=OUTCOME_WINDOW_DAYS
    )
    real_conversion_rate = real_summary.get("booking_conversion_rate", 0.0)
    real_cta_rate = real_summary.get("cta_click_rate", 0.0)
    total_events = real_summary.get("total_events", 0)

    # Use the better of conversion or CTA as the primary metric
    real_after = max(real_conversion_rate, real_cta_rate * 0.5)

    # --- Step 2: Decide on demo fallback if no real traffic ---
    is_demo_simulated = False
    demo_fallback_cutoff = now - timedelta(seconds=DEMO_FALLBACK_SECONDS)

    if deployed_at.tzinfo is None:
        deployed_at = deployed_at.replace(tzinfo=timezone.utc)

    if total_events == 0 and deployed_at <= demo_fallback_cutoff:
        # No real traffic recorded in the post-deployment window
        # → apply a realistic variance on the predicted gain for sandbox
        perturbation = random.uniform(-0.3, 0.5) * max(predicted_gain, 1.0)
        real_after = max(0.0, predicted_before + predicted_gain + perturbation)
        is_demo_simulated = True
        logger.info(
            f"OutcomeUpdater [{business_id}]: No real traffic — "
            f"demo-simulating outcome for '{patch_name}' "
            f"(simulated_after={real_after:.2f}%)"
        )
    elif total_events == 0:
        # Still in stabilization window with no traffic yet — skip this round
        logger.debug(
            f"OutcomeUpdater [{business_id}]: '{patch_name}' still in "
            "stabilization window, skipping."
        )
        return

    # --- Step 3: Compute real conversion gain ---
    real_gain = real_after - predicted_before

    # --- Step 4: Determine outcome label ---
    if real_gain >= 0:
        outcome_label = "success"
    else:
        outcome_label = f"FAILED: negative outcome (gain={real_gain:.2f}%)"

    # --- Step 5: Build updated memory context string for re-vectorization ---
    updated_context = (
        f"Business ID: {business_id}. "
        f"Industry: {industry_type}. "
        f"Applied Patch: {patch_name}. "
        f"Reason: {record.get('reason', '')}. "
        f"Layout configuration: {record.get('layout_used', '')}. "
        f"Impact: Conversion went from {predicted_before}% to {real_after:.2f}%. "
        f"Delta gain: {real_gain:.2f}%. "
        f"Agent: {record.get('agent_name', 'BusinessCopilot')}. "
        f"Outcome: {outcome_label}."
    )
    if is_demo_simulated:
        updated_context += " (demo_simulated=true)"

    # --- Step 6: Re-generate vector embedding with real outcome text ---
    new_vector = BusinessMemory._get_embedding(updated_context)

    # --- Step 7: Write everything back to MongoDB ---
    update_fields = {
        "metrics_after": real_after,
        "conversion_gain": real_gain,
        "patch_outcome": outcome_label,
        "memory_context": updated_context,
        "vector": new_vector,
        "outcome_verified_at": now,
        "outcome_window_days": OUTCOME_WINDOW_DAYS,
        "outcome_real_events": total_events,
    }
    if is_demo_simulated:
        update_fields["demo_simulated"] = True

    mongo.db.business_memory.update_one(
        {"_id": record["_id"]},
        {"$set": update_fields},
    )

    logger.info(
        f"✅ OutcomeUpdater [{business_id}]: '{patch_name}' outcome verified → "
        f"{outcome_label} "
        f"(before={predicted_before:.1f}% after={real_after:.2f}% "
        f"gain={real_gain:+.2f}% events={total_events} "
        f"demo={is_demo_simulated})"
    )

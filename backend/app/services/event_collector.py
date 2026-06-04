"""
EventCollector — Lightweight Analytics Event Ingestion Service.

Closes the feedback loop between live child websites (deployed to Netlify)
and MongoDB.  Without this service, the self-improving loop has nothing
real to observe — it only sees internal DB counts.

Supported event types:
    page_view, qr_scan, form_submit, booking_click,
    cta_click, bounce, scroll_depth, time_on_page

Write buffer:
    Events are batched in memory and flushed to MongoDB every
    FLUSH_INTERVAL_SECONDS or when the buffer reaches MAX_BUFFER_SIZE,
    whichever comes first.
"""

import hashlib
import logging
import threading
from datetime import datetime, timezone
from app import mongo

logger = logging.getLogger(__name__)

# ====================================================================
# Configuration
# ====================================================================

FLUSH_INTERVAL_SECONDS = 10
MAX_BUFFER_SIZE = 50

SUPPORTED_EVENT_TYPES = frozenset([
    "page_view",
    "qr_scan",
    "form_submit",
    "booking_click",
    "cta_click",
    "bounce",
    "scroll_depth",
    "time_on_page",
])


class EventCollector:
    """Thread-safe event buffer that periodically flushes to MongoDB."""

    def __init__(self):
        self._buffer = []
        self._lock = threading.Lock()
        self._timer = None
        self._start_flush_timer()

    # ================================================================
    # Public API
    # ================================================================

    def ingest_event(self, business_id, event_type, event_data=None,
                     source_url=None, visitor_ip=None, timestamp=None):
        """
        Validates and buffers an analytics event.

        Args:
            business_id:  Owner business identifier.
            event_type:   One of SUPPORTED_EVENT_TYPES.
            event_data:   Arbitrary dict of event-specific payload.
            source_url:   The child website URL that generated the event.
            visitor_ip:   Raw IP (hashed before storage for privacy).
            timestamp:    ISO string or datetime; defaults to now.

        Returns:
            (success: bool, error_message: str | None)
        """
        if not business_id:
            return False, "business_id is required."

        if event_type not in SUPPORTED_EVENT_TYPES:
            return False, (
                f"Unsupported event type '{event_type}'. "
                f"Allowed: {', '.join(sorted(SUPPORTED_EVENT_TYPES))}"
            )

        if timestamp:
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                except ValueError:
                    timestamp = datetime.now(timezone.utc)
        else:
            timestamp = datetime.now(timezone.utc)

        # Hash visitor IP for privacy
        visitor_id = None
        if visitor_ip:
            visitor_id = hashlib.sha256(
                f"{visitor_ip}:{business_id}".encode()
            ).hexdigest()[:16]

        event_doc = {
            "business_id": str(business_id),
            "event_type": event_type,
            "event_data": event_data or {},
            "source_url": source_url,
            "visitor_id": visitor_id,
            "timestamp": timestamp,
            "ingested_at": datetime.now(timezone.utc),
        }

        with self._lock:
            self._buffer.append(event_doc)
            if len(self._buffer) >= MAX_BUFFER_SIZE:
                self._flush()

        return True, None

    def get_event_summary(self, business_id, days=7):
        """
        Returns aggregated event counts for the copilot's analytics interpreter.
        """
        from datetime import timedelta
        b_id_str = str(business_id)
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)

        pipeline = [
            {
                "$match": {
                    "business_id": b_id_str,
                    "timestamp": {"$gte": cutoff},
                }
            },
            {
                "$group": {
                    "_id": "$event_type",
                    "count": {"$sum": 1},
                }
            },
        ]

        results = list(mongo.db.analytics_events.aggregate(pipeline))

        summary = {et: 0 for et in SUPPORTED_EVENT_TYPES}
        for r in results:
            summary[r["_id"]] = r["count"]

        # Compute derived metrics
        total_views = summary.get("page_view", 0)
        total_bounces = summary.get("bounce", 0)
        total_cta = summary.get("cta_click", 0)
        total_bookings = summary.get("booking_click", 0)

        summary["total_events"] = sum(summary.values())
        summary["bounce_rate"] = (
            round((total_bounces / total_views) * 100, 1)
            if total_views > 0 else 0.0
        )
        summary["cta_click_rate"] = (
            round((total_cta / total_views) * 100, 1)
            if total_views > 0 else 0.0
        )
        summary["booking_conversion_rate"] = (
            round((total_bookings / total_views) * 100, 1)
            if total_views > 0 else 0.0
        )
        summary["period_days"] = days

        return summary

    def flush_now(self):
        """Force an immediate flush of the buffer."""
        with self._lock:
            self._flush()

    # ================================================================
    # Private helpers
    # ================================================================

    def _flush(self):
        """Write buffered events to MongoDB. Called under lock."""
        if not self._buffer:
            return

        try:
            mongo.db.analytics_events.insert_many(self._buffer)
            logger.info(f"📊 Flushed {len(self._buffer)} analytics events to MongoDB")
            self._buffer = []
        except Exception as e:
            logger.error(f"Error flushing analytics events: {e}")

    def _start_flush_timer(self):
        """Periodic flush timer (runs in background thread)."""
        def _tick():
            with self._lock:
                self._flush()
            self._start_flush_timer()

        self._timer = threading.Timer(FLUSH_INTERVAL_SECONDS, _tick)
        self._timer.daemon = True
        self._timer.start()

    def shutdown(self):
        """Flush remaining events and cancel the timer."""
        if self._timer:
            self._timer.cancel()
        with self._lock:
            self._flush()


# ====================================================================
# Module-level singleton
# ====================================================================

event_collector = EventCollector()

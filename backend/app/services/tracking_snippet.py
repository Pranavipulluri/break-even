"""
TrackingSnippet — Lightweight analytics tracker for deployed child websites.

Generates a <script> tag that, when embedded in any deployed child website,
automatically sends analytics events back to the main Break-Even backend
via POST /api/events/ingest.

Events tracked:
    page_view      — on DOMContentLoaded
    cta_click      — click on buttons/links with cta/btn/book classes
    booking_click  — click on booking form elements
    scroll_depth   — at 25%, 50%, 75%, 100% thresholds
    bounce         — on beforeunload if time_on_page < 10s
    time_on_page   — on beforeunload with elapsed seconds

The snippet is ~2KB minified and runs without any external dependencies.
"""

import logging

logger = logging.getLogger(__name__)


class TrackingSnippet:
    """Generates and injects the child→parent analytics tracking script."""

    @staticmethod
    def generate(business_id, api_key=None, backend_url=None):
        """
        Returns a <script> tag string for embedding in child websites.

        Args:
            business_id: The business owner's ID (sent with every event).
            api_key:     Optional API key for authenticated event ingestion.
            backend_url: The main backend URL. Defaults to production-friendly
                        relative path (the child site's own Netlify function or
                        the main backend).
        """
        # Default to the production backend — override via env in deployment
        if not backend_url:
            backend_url = "https://break-even-backend.onrender.com"

        api_key_header = ""
        if api_key:
            api_key_header = f'"X-BE-Key": "{api_key}",'

        return f'''<!-- Break-Even Analytics Tracker -->
<script>
(function() {{
  "use strict";
  var BID = "{business_id}";
  var API = "{backend_url}/api/events/ingest";
  var HEADERS = {{
    "Content-Type": "application/json",
    {api_key_header}
  }};
  var startTime = Date.now();
  var scrollMarks = {{}};

  function send(eventType, eventData) {{
    try {{
      var body = JSON.stringify({{
        business_id: BID,
        event_type: eventType,
        event_data: eventData || {{}},
        source_url: window.location.href,
        timestamp: new Date().toISOString()
      }});
      if (navigator.sendBeacon) {{
        var blob = new Blob([body], {{ type: "application/json" }});
        navigator.sendBeacon(API, blob);
      }} else {{
        fetch(API, {{ method: "POST", headers: HEADERS, body: body, keepalive: true }});
      }}
    }} catch (e) {{
      /* silent fail — never break the host page */
    }}
  }}

  /* Page View */
  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", function() {{ send("page_view"); }});
  }} else {{
    send("page_view");
  }}

  /* CTA / Booking Clicks — delegate from document */
  document.addEventListener("click", function(e) {{
    var el = e.target.closest("button, a, [role=button]");
    if (!el) return;
    var cls = (el.className || "").toLowerCase();
    var txt = (el.textContent || "").toLowerCase().trim();
    var isBooking = cls.indexOf("book") > -1 || txt.indexOf("book") > -1 ||
                    txt.indexOf("schedule") > -1 || txt.indexOf("appointment") > -1;
    var isCTA = cls.indexOf("cta") > -1 || cls.indexOf("btn") > -1 ||
                el.tagName === "BUTTON" || cls.indexOf("button") > -1;
    if (isBooking) {{
      send("booking_click", {{ text: txt.substring(0, 60), element: el.tagName }});
    }} else if (isCTA) {{
      send("cta_click", {{ text: txt.substring(0, 60), element: el.tagName }});
    }}
  }}, true);

  /* Scroll Depth */
  var scrollTimer = null;
  window.addEventListener("scroll", function() {{
    if (scrollTimer) clearTimeout(scrollTimer);
    scrollTimer = setTimeout(function() {{
      var docH = document.documentElement.scrollHeight - window.innerHeight;
      if (docH <= 0) return;
      var pct = Math.round((window.scrollY / docH) * 100);
      var marks = [25, 50, 75, 100];
      for (var i = 0; i < marks.length; i++) {{
        if (pct >= marks[i] && !scrollMarks[marks[i]]) {{
          scrollMarks[marks[i]] = true;
          send("scroll_depth", {{ depth_percent: marks[i] }});
        }}
      }}
    }}, 200);
  }}, {{ passive: true }});

  /* Bounce + Time on Page */
  window.addEventListener("beforeunload", function() {{
    var elapsed = Math.round((Date.now() - startTime) / 1000);
    if (elapsed < 10) {{
      send("bounce", {{ time_on_page_seconds: elapsed }});
    }}
    send("time_on_page", {{ seconds: elapsed }});
  }});

  /* Form Submissions */
  document.addEventListener("submit", function(e) {{
    var form = e.target;
    var id = form.id || form.action || "unknown";
    send("form_submit", {{ form_id: id }});
  }}, true);
}})();
</script>'''

    @staticmethod
    def inject(html_content, business_id, api_key=None, backend_url=None):
        """
        Injects the tracking script before </body> in existing HTML.

        Args:
            html_content: The full HTML string.
            business_id:  Business owner's ID.
            api_key:      Optional API key.
            backend_url:  Override backend URL.

        Returns:
            HTML string with tracking script injected.
        """
        if not html_content or not business_id:
            return html_content

        snippet = TrackingSnippet.generate(
            business_id=business_id,
            api_key=api_key,
            backend_url=backend_url,
        )

        # Inject before </body> if it exists
        if "</body>" in html_content:
            return html_content.replace("</body>", f"{snippet}\n</body>")
        elif "</html>" in html_content:
            return html_content.replace("</html>", f"{snippet}\n</html>")
        else:
            # Append at the end
            return html_content + "\n" + snippet

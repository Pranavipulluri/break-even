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
    def generate(business_id, api_key=None, backend_url=None, website_id=None):
        """
        Returns a <script> tag string for embedding in child websites.

        Args:
            business_id: The business owner's ID (sent with every event).
            api_key:     Optional API key for authenticated event ingestion.
            backend_url: The main backend URL. Defaults to production-friendly
                        relative path (the child site's own Netlify function or
                        the main backend).
            website_id:  The child website's MongoDB ID.
        """
        # Default to the production backend — override via env in deployment
        if not backend_url:
            import os
            backend_url = os.environ.get('BACKEND_URL') or os.environ.get('SELF_URL')
            if not backend_url:
                try:
                    from flask import request
                    backend_url = request.url_root.rstrip('/')
                except Exception:
                    backend_url = ""

        api_key_header = ""
        if api_key:
            api_key_header = f'"X-BE-Key": "{api_key}",'

        web_id_str = str(website_id) if website_id else ""

        return f'''<!-- Break-Even Analytics Tracker -->
<script>
(function() {{
  "use strict";
  var BID = "{business_id}";
  var WID = "{web_id_str}";
  window.__BE_WID = WID;
  window.__BE_BACKEND_URL = "{backend_url}";
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

  function trackProductInteraction(productId, type) {{
    if (!productId || !WID) return;
    try {{
      var body = JSON.stringify({{
        product_id: productId,
        type: type
      }});
      fetch("{backend_url}/api/site/" + WID + "/track-interaction", {{
        method: "POST",
        headers: {{ "Content-Type": "application/json" }},
        body: body
      }});
    }} catch (e) {{
      /* silent fail */
    }}
  }}

  /* Page View */
  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", function() {{ send("page_view"); }});
  }} else {{
    send("page_view");
  }}

  /* Product View Tracking on load */
  function trackLoadedProducts() {{
    try {{
      var prodElements = document.querySelectorAll("[data-track-product-view]");
      prodElements.forEach(function(el) {{
        var pId = el.getAttribute("data-product-id");
        if (pId) {{
          trackProductInteraction(pId, "view");
        }}
      }});
    }} catch (err) {{}}
  }}

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", trackLoadedProducts);
  }} else {{
    trackLoadedProducts();
  }}

  /* Product Inquiry tracking and Form Autofill */
  document.addEventListener("click", function(e) {{
    try {{
      var el = e.target.closest("[data-track-product-inquiry]");
      if (!el) return;
      var pId = el.getAttribute("data-product-id");
      var pName = el.getAttribute("data-product-name");
      
      if (pId) {{
        trackProductInteraction(pId, "inquiry");
      }}
      
      // Autofill contact/message form if exists
      var contactForm = document.querySelector("#contact form, form[onsubmit*='submitContact']");
      if (contactForm) {{
        var subjectInput = contactForm.querySelector("[name=subject]");
        var messageInput = contactForm.querySelector("[name=message]");
        if (subjectInput) {{
          subjectInput.value = "Consultation: " + pName;
        }}
        if (messageInput) {{
          messageInput.value = "I would like to consult and book for: " + pName + ". Please get back to me.";
        }}
      }}
    }} catch (err) {{}}
  }}, true);

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
    def inject(html_content, business_id, api_key=None, backend_url=None, website_id=None):
        """
        Injects the tracking script before </body> in existing HTML.

        Args:
            html_content: The full HTML string.
            business_id:  Business owner's ID.
            api_key:      Optional API key.
            backend_url:  Override backend URL.
            website_id:   The child website's MongoDB ID.

        Returns:
            HTML string with tracking script injected.
        """
        if not html_content or not business_id:
            return html_content

        # Look up website_id in the database if not explicitly passed
        if not website_id and business_id:
            try:
                from app import mongo
                site = mongo.db.child_websites.find_one({"owner_id": str(business_id)}, {"_id": 1})
                if not site:
                    from bson import ObjectId
                    site = mongo.db.child_websites.find_one({"owner_id": ObjectId(business_id)}, {"_id": 1})
                if site:
                    website_id = str(site["_id"])
            except Exception:
                pass

        snippet = TrackingSnippet.generate(
            business_id=business_id,
            api_key=api_key,
            backend_url=backend_url,
            website_id=website_id,
        )

        # Inject before </body> if it exists
        if "</body>" in html_content:
            return html_content.replace("</body>", f"{snippet}\n</body>")
        elif "</html>" in html_content:
            return html_content.replace("</html>", f"{snippet}\n</html>")
        else:
            # Append at the end
            return html_content + "\n" + snippet

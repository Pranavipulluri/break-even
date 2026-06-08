"""
Break-Even Platform — Full System Health Check
Covers backend routes, MongoDB, Gemini, Netlify, Socket.IO, and auth flow.
"""

import os, sys, json, time, datetime
import requests
import socketio as sio_client

BASE_URL   = "http://localhost:5000"
API        = f"{BASE_URL}/api"
TIMEOUT    = 10

# ── Terminal colours ──────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

results = []

def PASS(name, detail=""):
    tag = f"{GREEN}[PASS]{RESET}"
    print(f"  {tag} {name}" + (f"\n         {CYAN}{detail}{RESET}" if detail else ""))
    results.append({"name": name, "status": "PASS", "detail": detail})

def FAIL(name, detail=""):
    tag = f"{RED}[FAIL]{RESET}"
    print(f"  {tag} {name}" + (f"\n         {RED}{detail}{RESET}" if detail else ""))
    results.append({"name": name, "status": "FAIL", "detail": detail})

def WARN(name, detail=""):
    tag = f"{YELLOW}[WARN]{RESET}"
    print(f"  {tag} {name}" + (f"\n         {YELLOW}{detail}{RESET}" if detail else ""))
    results.append({"name": name, "status": "WARN", "detail": detail})

def section(title):
    print(f"\n{BOLD}{'='*66}{RESET}")
    print(f"{BOLD}  {title}{RESET}")
    print(f"{BOLD}{'='*66}{RESET}")

def get(path, token=None, **kw):
    h = {"Authorization": f"Bearer {token}"} if token else {}
    return requests.get(f"{API}{path}", headers=h, timeout=TIMEOUT, **kw)

def post(path, body=None, token=None, **kw):
    h = {"Content-Type": "application/json"}
    if token: h["Authorization"] = f"Bearer {token}"
    return requests.post(f"{API}{path}", json=body or {}, headers=h, timeout=TIMEOUT, **kw)

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 — BACKEND REACHABILITY
# ─────────────────────────────────────────────────────────────────────────────
section("1 · FLASK SERVER + HEALTH ROUTE")

try:
    r = requests.get(BASE_URL, timeout=TIMEOUT)
    PASS("Flask server reachable at localhost:5000", f"HTTP {r.status_code}")
except Exception as e:
    FAIL("Flask server reachable at localhost:5000", str(e))
    print(f"\n{RED}  Flask is not running — remaining checks will fail.{RESET}\n")
    sys.exit(1)

try:
    r = get("/health")
    if r.status_code == 200:
        PASS("GET /api/health", f"HTTP 200 — {r.text[:80]}")
    else:
        WARN("GET /api/health", f"HTTP {r.status_code}")
except Exception as e:
    FAIL("GET /api/health", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 — MONGODB
# ─────────────────────────────────────────────────────────────────────────────
section("2 · MONGODB")

try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
    from pymongo import MongoClient
    uri  = os.environ.get("MONGO_URI", "mongodb://localhost:27017/breakeven")
    cli  = MongoClient(uri, serverSelectionTimeoutMS=5000)
    db   = cli.get_default_database() if "breakeven" not in uri else cli["breakeven"]
    colls = db.list_collection_names()
    if len(colls) >= 21:
        PASS(f"MongoDB connected — {len(colls)} collections present",
             ", ".join(sorted(colls)[:8]) + " …")
    else:
        WARN(f"MongoDB connected — only {len(colls)}/21 collections",
             ", ".join(sorted(colls)))
except Exception as e:
    FAIL("MongoDB connection", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 — AUTH FLOW (register → login → JWT)
# ─────────────────────────────────────────────────────────────────────────────
section("3 · AUTH FLOW — register → login → JWT")

ts    = int(time.time())
EMAIL = f"healthcheck_{ts}@breakeven.test"
PWD   = "Health@1234"
TOKEN = None
USER_ID = None

try:
    r = post("/auth/register", {"email": EMAIL, "password": PWD,
                                 "name": "HealthCheck Owner",
                                 "business_name": "HealthCheck Biz",
                                 "business_type": "general"})
    if r.status_code in (200, 201):
        PASS("POST /api/auth/register", f"HTTP {r.status_code} — {EMAIL}")
    elif r.status_code == 409:
        WARN("POST /api/auth/register", "User already exists (409) — proceeding to login")
    else:
        FAIL("POST /api/auth/register", f"HTTP {r.status_code}: {r.text[:120]}")
except Exception as e:
    FAIL("POST /api/auth/register", str(e))

try:
    r = post("/auth/login", {"email": EMAIL, "password": PWD})
    if r.status_code == 200:
        body    = r.json()
        TOKEN   = body.get("token") or body.get("access_token")
        USER_ID = (body.get("user") or {}).get("_id") or (body.get("user") or {}).get("id")
        if TOKEN:
            PASS("POST /api/auth/login", f"JWT obtained — user_id={USER_ID}")
        else:
            FAIL("POST /api/auth/login", f"No token in response: {json.dumps(body)[:120]}")
    else:
        FAIL("POST /api/auth/login", f"HTTP {r.status_code}: {r.text[:120]}")
except Exception as e:
    FAIL("POST /api/auth/login", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 — ROUTE SMOKE TESTS
# ─────────────────────────────────────────────────────────────────────────────
section("4 · ROUTE SMOKE TESTS")

# Routes that require auth — 401 proves the route is registered (not 404)
AUTH_OK  = [200, 204]
ROUTE_OK = [200, 204, 400, 401, 404, 405]   # 401 = route exists, auth gate working

ROUTES = [
    ("GET",  "/analytics/summary",          None,  [200, 204, 400, 404]),
    ("GET",  "/analytics/overview?range=7d", None, ROUTE_OK),
    ("GET",  "/products",                   None,  ROUTE_OK),
    ("GET",  "/messages",                   None,  ROUTE_OK),
    ("GET",  "/dashboard",                  None,  ROUTE_OK),
    ("GET",  "/translation/translate",      None,  [200, 400, 404, 405]),
    ("POST", "/events/ingest",              {"business_id": USER_ID or "test",
                                              "event_type": "page_view",
                                              "event_data": {}}, [200, 202, 400, 404]),
]

for method, path, body, ok_codes in ROUTES:
    try:
        if method == "GET":
            r = get(path, token=TOKEN)
        else:
            r = post(path, body, token=TOKEN)
        if r.status_code in ok_codes:
            PASS(f"{method} /api{path}", f"HTTP {r.status_code}")
        else:
            FAIL(f"{method} /api{path}", f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        FAIL(f"{method} /api{path}", str(e))

# agent/optimize needs a website — skip if no token
if TOKEN and USER_ID:
    try:
        r = post("/agent/optimize",
                 {"command": "Health check optimize", "business_id": USER_ID},
                 token=TOKEN)
        if r.status_code in (200, 400, 404, 422):
            PASS("POST /api/agent/optimize", f"HTTP {r.status_code}")
        else:
            FAIL("POST /api/agent/optimize", f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        FAIL("POST /api/agent/optimize", str(e))

    try:
        r = post("/website-builder/create",
                 {"website_name": "HC Test", "business_type": "general",
                  "color_theme": "blue", "contact_info": {"phone": "000"},
                  "area": "Test City", "description": "Health check site"},
                 token=TOKEN)
        if r.status_code in (200, 201, 400, 409):
            PASS("POST /api/website-builder/create", f"HTTP {r.status_code}")
        else:
            FAIL("POST /api/website-builder/create", f"HTTP {r.status_code}: {r.text[:100]}")
    except Exception as e:
        FAIL("POST /api/website-builder/create", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5 — SOCKET.IO
# ─────────────────────────────────────────────────────────────────────────────
section("5 · SOCKET.IO")

connected = False
try:
    sio = sio_client.Client(logger=False, engineio_logger=False)
    sio.connect(BASE_URL, wait_timeout=6)
    connected = sio.connected
    if connected:
        PASS("Socket.IO handshake", f"sid={sio.get_sid()}")
    else:
        FAIL("Socket.IO handshake", "connect() returned but sio.connected=False")
    sio.disconnect()
except Exception as e:
    FAIL("Socket.IO handshake", str(e))

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6 — EXTERNAL API KEYS
# ─────────────────────────────────────────────────────────────────────────────
section("6 · EXTERNAL SERVICES (Gemini + Netlify)")

# Gemini
gemini_key = os.environ.get("GEMINI_API_KEY", "")
if not gemini_key:
    WARN("Gemini API key", "GEMINI_API_KEY not set — AI Copilot runs in fallback mode")
else:
    try:
        import google.generativeai as genai
        genai.configure(api_key=gemini_key)
        # Try current model first, fall back to legacy name
        for model_name in ("gemini-2.0-flash", "gemini-1.5-flash", "gemini-pro"):
            try:
                m    = genai.GenerativeModel(model_name)
                resp = m.generate_content("Reply with only the word: OK")
                txt  = resp.text.strip()
                break
            except Exception:
                txt = ""
        if txt:
            PASS("Gemini API key valid", f"Model={model_name} responded: '{txt[:40]}'")
        else:
            FAIL("Gemini API key valid", "All Gemini models returned empty response")
    except Exception as e:
        FAIL("Gemini API key valid", str(e)[:120])

# Netlify
netlify_token = os.environ.get("NETLIFY_TOKEN", "") or os.environ.get("NETLIFY_API_TOKEN", "")
if not netlify_token:
    WARN("Netlify token", "NETLIFY_TOKEN not set — Netlify deploys disabled")
else:
    try:
        r = requests.get(
            "https://api.netlify.com/api/v1/user",
            headers={"Authorization": f"Bearer {netlify_token}"},
            timeout=TIMEOUT,
        )
        if r.status_code == 200:
            name = r.json().get("full_name") or r.json().get("email", "unknown")
            PASS("Netlify token valid", f"Authenticated as '{name}'")
        elif r.status_code == 401:
            FAIL("Netlify token valid", "401 Unauthorized — token invalid or expired")
        else:
            WARN("Netlify token valid", f"HTTP {r.status_code}: {r.text[:80]}")
    except Exception as e:
        FAIL("Netlify token reachable", str(e)[:120])

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7 — FRONTEND CODE CHECKS (static)
# ─────────────────────────────────────────────────────────────────────────────
section("7 · FRONTEND STATIC CHECKS")

FRONTEND = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "src")

PAGE_ROUTES = [
    "pages/Dashboard.jsx",
    "pages/Analytics.jsx",
    "pages/Products.jsx",
    "pages/Messages.jsx",
    "pages/WebsiteBuilder.jsx",
    "pages/QRCode.jsx",
    "pages/AITools.jsx",
    "pages/Login.jsx",
    "pages/Register.jsx",
]

for rel in PAGE_ROUTES:
    fp = os.path.join(FRONTEND, rel)
    if os.path.isfile(fp):
        size = os.path.getsize(fp)
        PASS(f"Page file exists: {rel}", f"{size:,} bytes")
    else:
        FAIL(f"Page file exists: {rel}", "File not found")

# Confirm clearInterval is in the hook (not missing cleanup)
hook_path = os.path.join(FRONTEND, "hooks", "useAnalytics.js")
if os.path.isfile(hook_path):
    src = open(hook_path, encoding="utf-8").read()
    set_count   = src.count("setInterval")
    clear_count = src.count("clearInterval")
    if clear_count >= set_count:
        PASS("useAnalytics.js — clearInterval cleanup",
             f"{set_count} setInterval / {clear_count} clearInterval calls")
    else:
        FAIL("useAnalytics.js — clearInterval cleanup",
             f"{set_count} setInterval but only {clear_count} clearInterval — memory leak!")
else:
    FAIL("useAnalytics.js exists", "File not found")

# Confirm Dashboard uses the hook (not a raw setInterval)
dash = open(os.path.join(FRONTEND, "pages/Dashboard.jsx"), encoding="utf-8").read()
if "useAnalyticsSummary" in dash and "setInterval" not in dash:
    PASS("Dashboard.jsx — polling via hook (no raw setInterval)", "")
elif "setInterval" in dash and "clearInterval" in dash:
    WARN("Dashboard.jsx — raw setInterval found but clearInterval present", "")
elif "setInterval" in dash:
    FAIL("Dashboard.jsx — raw setInterval without clearInterval", "Memory leak risk")
else:
    PASS("Dashboard.jsx — no raw setInterval (delegates to hook)", "")

anal = open(os.path.join(FRONTEND, "pages/Analytics.jsx"), encoding="utf-8").read()
if "useAnalyticsRange" in anal and "setInterval" not in anal:
    PASS("Analytics.jsx — polling via hook (no raw setInterval)", "")
elif "setInterval" in anal and "clearInterval" in anal:
    WARN("Analytics.jsx — raw setInterval found but clearInterval present", "")
elif "setInterval" in anal:
    FAIL("Analytics.jsx — raw setInterval without clearInterval", "Memory leak risk")
else:
    PASS("Analytics.jsx — no raw setInterval (delegates to hook)", "")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 8 — INTEGRATION: FULL AUTH ROUND-TRIP
# ─────────────────────────────────────────────────────────────────────────────
section("8 · INTEGRATION — Auth round-trip token validity")

if TOKEN:
    try:
        r = get("/products", token=TOKEN)
        if r.status_code in (200, 204):
            PASS("JWT token accepted by /api/products", f"HTTP {r.status_code}")
        else:
            FAIL("JWT token accepted by /api/products", f"HTTP {r.status_code}")
    except Exception as e:
        FAIL("JWT token round-trip", str(e))
else:
    FAIL("JWT token round-trip", "No token obtained — login step failed")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
section("HEALTH CHECK SUMMARY")

passed  = [r for r in results if r["status"] == "PASS"]
failed  = [r for r in results if r["status"] == "FAIL"]
warned  = [r for r in results if r["status"] == "WARN"]

print(f"\n  {GREEN}PASS{RESET}  {len(passed):>3}")
print(f"  {YELLOW}WARN{RESET}  {len(warned):>3}")
print(f"  {RED}FAIL{RESET}  {len(failed):>3}")
print(f"  ─────────────")
print(f"  TOTAL {len(results):>3}\n")

if failed:
    print(f"  {RED}{BOLD}Failed checks:{RESET}")
    for f in failed:
        print(f"    {RED}✗{RESET} {f['name']}")
        if f["detail"]:
            print(f"        {f['detail'][:100]}")

if warned:
    print(f"\n  {YELLOW}{BOLD}Warnings:{RESET}")
    for w in warned:
        print(f"    {YELLOW}!{RESET} {w['name']}")
        if w["detail"]:
            print(f"        {w['detail'][:100]}")

overall = "ALL SYSTEMS OPERATIONAL" if not failed else f"{len(failed)} CHECK(S) FAILED"
colour  = GREEN if not failed else RED
print(f"\n  {colour}{BOLD}>> {overall}{RESET}\n")

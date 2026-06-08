import sys
import io
import os

# ── Windows UTF-8 fix ────────────────────────────────────────────────────────
# The default Windows console uses cp1252 which cannot encode emoji (✅ ❌ 🚀
# etc.) used in logger/print statements throughout the backend.  Reconfigure
# stdout and stderr to UTF-8 so the server never crashes on an encode error.
# Setting PYTHONIOENCODING here also covers any sub-processes spawned later.
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
if hasattr(sys.stdout, "reconfigure"):
    # Python 3.7+ fast path
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
else:
    # Fallback for older Pythons / non-TTY pipes
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
# ─────────────────────────────────────────────────────────────────────────────

from dotenv import load_dotenv
load_dotenv()  # Load .env BEFORE app creation reads Config

from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    # Check if eventlet is installed and used as the server driver
    try:
        import eventlet
        has_eventlet = True
    except ImportError:
        has_eventlet = False

    if has_eventlet:
        # Eventlet wsgi server does not accept allow_unsafe_werkzeug
        socketio.run(app, host='0.0.0.0', port=port, debug=True)
    else:
        try:
            socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
        except TypeError:
            socketio.run(app, host='0.0.0.0', port=port, debug=True)



from dotenv import load_dotenv
load_dotenv()  # Load .env BEFORE app creation reads Config

from app import create_app, socketio
import os

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


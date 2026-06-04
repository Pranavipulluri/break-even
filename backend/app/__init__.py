from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.config import Config
from apscheduler.schedulers.background import BackgroundScheduler

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()
mail = Mail()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder='../static', static_url_path='/static')
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    mongo.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS with flexible port handling
    allowed_origins = [
        "http://localhost:3000", 
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",  # Just in case React increments further
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003"
    ]
    
    CORS(app, 
         origins=allowed_origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    mail.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*")
    
    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.products import products_bp
    from app.routes.messages import messages_bp
    from app.routes.analytics import analytics_bp
    from app.routes.qr_code import qr_bp
    from app.routes.ai_tools import ai_bp
    from app.routes.website_builder import website_bp
    from app.routes.customers import customers_bp
    from app.routes.child_website import child_website_bp
    from app.routes.public_api import public_api_bp
    from app.routes.bookings import bookings_bp
    from app.routes.bookings_routes import bookings_routes_bp
    from app.routes.orders import orders_bp
    from app.routes.law_firm_routes import law_firm_bp, init_law_firm_routes
    from app.routes.beauty_salon_routes import beauty_salon_bp, init_beauty_salon_routes
    from app.routes.translation_routes import translation_bp
    from app.routes.ai_chatbot_routes import ai_chatbot_bp
    from app.routes.consultation_routes import consultation_bp
    from app.routes.agent_routes import agent_bp
    from app.routes.event_routes import event_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(products_bp, url_prefix='/api')
    app.register_blueprint(messages_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(qr_bp, url_prefix='/api')
    app.register_blueprint(ai_bp, url_prefix='/api')
    app.register_blueprint(website_bp, url_prefix='/api')
    app.register_blueprint(customers_bp, url_prefix='/api')
    app.register_blueprint(child_website_bp, url_prefix='/api')
    app.register_blueprint(public_api_bp, url_prefix='/api')
    app.register_blueprint(bookings_bp, url_prefix='/api')
    app.register_blueprint(bookings_routes_bp, url_prefix='/api')
    app.register_blueprint(orders_bp, url_prefix='/api')
    app.register_blueprint(law_firm_bp, url_prefix='/api')
    app.register_blueprint(beauty_salon_bp)  # Beauty salon routes with custom prefix
    app.register_blueprint(translation_bp, url_prefix='/api')  # Translation routes with prefix
    app.register_blueprint(ai_chatbot_bp)  # AI chatbot routes
    app.register_blueprint(consultation_bp, url_prefix='/api')  # Consultation routes
    app.register_blueprint(agent_bp, url_prefix='/api')  # AI Agent Copilot routes
    app.register_blueprint(event_bp, url_prefix='/api')  # Analytics Event Collector
    
    # Initialize law firm integration service with socketio and mongo client
    init_law_firm_routes(socketio, mongo.cx)
    
    # Initialize beauty salon integration service with socketio and mongo client
    init_beauty_salon_routes(socketio, mongo.cx)

    # WebSocket event handlers
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        emit('connected', {'message': 'Connected to Break-even server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('join_room')
    def handle_join_room(user_id):
        join_room(user_id)
        print(f'User {user_id} joined their room')
        emit('joined_room', {'room': user_id})

    @socketio.on('join_agent_room')
    def handle_join_agent_room(data):
        """Frontend copilot drawer joins the business room to receive agent thought streams."""
        business_id = data.get('business_id') if isinstance(data, dict) else data
        join_room(str(business_id))
        print(f'Agent room joined for business: {business_id}')
        emit('agent_room_joined', {'business_id': str(business_id)})

    @socketio.on('leave_room')
    def handle_leave_room(user_id):
        leave_room(user_id)
        print(f'User {user_id} left their room')

    # Add health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'service': 'break-even-backend'}), 200

    # Initialize database on first run
    with app.app_context():
        from app.utils.database import init_database
        init_database()

    # ── Outcome Updater — closes the AI learn loop ──
    # Runs every 15 seconds to check for patches whose predicted outcomes
    # have sat long enough to evaluate against real event data.
    # Updates business_memory records from "applied_pending_results" to
    # "success" / "FAILED" with observed conversion deltas and re-vectorizes.
    try:
        from app.services.outcome_updater import run_outcome_updates
        scheduler = BackgroundScheduler(daemon=True)
        scheduler.add_job(
            func=run_outcome_updates,
            args=[app],
            trigger="interval",
            seconds=15,
            id="outcome_updater",
            replace_existing=True,
            max_instances=1,
        )
        scheduler.start()
        import logging
        logging.getLogger(__name__).info(
            "🔄 OutcomeUpdater scheduler started (interval=15s)"
        )
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(
            f"OutcomeUpdater scheduler failed to start: {e}"
        )

    return app

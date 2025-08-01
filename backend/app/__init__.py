from flask import Flask, jsonify
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_mail import Mail
from flask_socketio import SocketIO, emit, join_room, leave_room
from app.config import Config

# Initialize extensions
mongo = PyMongo()
jwt = JWTManager()
mail = Mail()
socketio = SocketIO()

def create_app(config_class=Config):
    app = Flask(__name__)  # ✅ fixed here
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

    return app

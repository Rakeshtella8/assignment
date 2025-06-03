from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

from app.core.config import config
from app.database.base import init_db

# Initialize extensions
jwt = JWTManager()
bcrypt = Bcrypt()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

def create_app(config_name='default'):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize CORS
    CORS(app, resources={
        r"/api/*": {"origins": app.config['CORS_ORIGINS']}
    })
    
    # Initialize extensions
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    init_db(app)
    
    # Initialize Redis connection
    app.redis = redis.from_url(app.config['REDIS_URL'])
    
    # Register blueprints
    from app.api.routes.auth import auth_bp
    from app.api.routes.documents import documents_bp
    from app.api.routes.users import users_bp
    
    app.register_blueprint(auth_bp, url_prefix=f"{app.config['API_PREFIX']}/auth")
    app.register_blueprint(documents_bp, url_prefix=f"{app.config['API_PREFIX']}/documents")
    app.register_blueprint(users_bp, url_prefix=f"{app.config['API_PREFIX']}/users")
    
    # Register error handlers
    register_error_handlers(app)
    
    return app

def register_error_handlers(app):
    """Register error handlers for the application."""
    
    @app.errorhandler(400)
    def bad_request(error):
        return {
            'message': 'Bad request',
            'details': str(error)
        }, 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return {
            'message': 'Unauthorized',
            'details': str(error)
        }, 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return {
            'message': 'Forbidden',
            'details': str(error)
        }, 403
    
    @app.errorhandler(404)
    def not_found(error):
        return {
            'message': 'Resource not found',
            'details': str(error)
        }, 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return {
            'message': 'Validation error',
            'details': str(error)
        }, 422
    
    @app.errorhandler(500)
    def internal_server_error(error):
        app.logger.error(f"Server Error: {str(error)}")
        return {
            'message': 'Internal server error',
            'details': str(error)
        }, 500 
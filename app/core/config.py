import os
from datetime import timedelta
import stat

class Config:
    # Base configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    APP_ENV = os.getenv('APP_ENV', 'development')
    DEBUG = APP_ENV == 'development'

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'MYSQL_DATABASE_URI',
        'mysql+pymysql://root:password@localhost:3306/fintech_cms'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,  # Added timeout
        'max_overflow': 5    # Added max overflow
    }

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 30)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 7)))
    JWT_ERROR_MESSAGE_KEY = 'message'

    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    
    # Security
    BCRYPT_LOG_ROUNDS = 13
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    
    # API Configuration
    API_TITLE = 'Fintech CMS API'
    API_VERSION = 'v1'
    API_PREFIX = f'/api/{API_VERSION}'
    
    # Pagination
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100
    
    # Document Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx', 'xls', 'xlsx'}

    # Cache Configuration
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = REDIS_URL
    CACHE_DEFAULT_TIMEOUT = 300

    # Rate Limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = REDIS_URL

    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    @staticmethod
    def init_app(app):
        """Initialize application configuration"""
        # Create upload directory with secure permissions
        os.makedirs(Config.UPLOAD_FOLDER, mode=0o750, exist_ok=True)
        # Ensure upload directory has secure permissions even if it already existed
        os.chmod(Config.UPLOAD_FOLDER, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)

        # Create logs directory
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, mode=0o750, exist_ok=True)
        os.chmod(log_dir, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP)


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost:3306/fintech_cms_test'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # Production specific initialization
        import logging
        from logging.handlers import RotatingFileHandler
        
        # File handler
        file_handler = RotatingFileHandler(
            'logs/fintech_cms.log',
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(cls.LOG_FORMAT))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 
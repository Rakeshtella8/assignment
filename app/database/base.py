from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """Initialize the database with the Flask app."""
    db.init_app(app)
    migrate.init_app(app, db)

    # Import models here to ensure they are registered with SQLAlchemy
    from app.models.user import User
    from app.models.document import Document
    from app.models.recent_view import RecentView 
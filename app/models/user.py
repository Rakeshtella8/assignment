from werkzeug.security import generate_password_hash, check_password_hash
from app.models.base import BaseModel, db
from app.models.recent_view import RecentView

class User(BaseModel):
    """User model for authentication and authorization."""
    
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    role = db.Column(db.String(20), nullable=False, default='user')
    is_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)

    # Relationships
    documents = db.relationship('Document', backref='owner', lazy='dynamic')
    recent_views = db.relationship('RecentView', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        """Initialize a new user."""
        super(User, self).__init__(**kwargs)
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def set_password(self, password):
        """Set the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        """Check if the user is an admin."""
        return self.role == 'admin'

    def to_dict(self):
        """Convert user instance to dictionary."""
        data = super().to_dict()
        # Remove sensitive information
        data.pop('password_hash', None)
        return data

    @classmethod
    def get_by_email(cls, email):
        """Get a user by email."""
        return cls.query.filter_by(email=email).first()

    @classmethod
    def get_by_username(cls, username):
        """Get a user by username."""
        return cls.query.filter_by(username=username).first()

    def get_recent_views(self, limit=10):
        """Get user's recently viewed documents."""
        return (RecentView.query
                .filter_by(user_id=self.id)
                .order_by(RecentView.viewed_at.desc())
                .limit(limit)
                .all()) 
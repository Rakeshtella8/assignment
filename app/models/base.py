from datetime import datetime
from app.database.base import db

class BaseModel(db.Model):
    """Base model class that includes common fields and methods."""
    
    __abstract__ = True

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def save(self):
        """Save the model instance to the database."""
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        """Delete the model instance from the database."""
        db.session.delete(self)
        db.session.commit()

    def update(self, **kwargs):
        """Update the model instance with the given kwargs."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        return self.save()

    @classmethod
    def get_by_id(cls, id):
        """Get a model instance by ID."""
        return cls.query.get(id)

    @classmethod
    def get_all(cls):
        """Get all active model instances."""
        return cls.query.filter_by(is_active=True).all()

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        } 
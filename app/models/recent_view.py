from datetime import datetime
from app.models.base import BaseModel, db
from flask import current_app

class RecentView(BaseModel):
    """Model for tracking recently viewed documents."""
    
    __tablename__ = 'recent_views'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    viewed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        # Ensure one record per user-document combination
        db.UniqueConstraint('user_id', 'document_id', name='uq_user_document'),
        # Index for quick retrieval of recent views
        db.Index('idx_recent_views_user_time', 'user_id', 'viewed_at')
    )

    @classmethod
    def add_view(cls, user_id, document_id):
        """Add or update a document view for a user."""
        view = cls.query.filter_by(
            user_id=user_id,
            document_id=document_id
        ).first()

        if view:
            view.viewed_at = datetime.utcnow()
            view.save()
        else:
            view = cls(
                user_id=user_id,
                document_id=document_id
            )
            view.save()

            # Maintain a maximum of 50 recent views per user
            cls._cleanup_old_views(user_id)

        return view

    @classmethod
    def _cleanup_old_views(cls, user_id, max_views=50):
        """Remove old views beyond the maximum limit."""
        try:
            views = cls.query.filter_by(user_id=user_id)\
                .order_by(cls.viewed_at.desc())\
                .offset(max_views)\
                .all()
            
            if views:
                for view in views:
                    db.session.delete(view)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error cleaning up old views: {str(e)}")

    @classmethod
    def get_user_recent_views(cls, user_id, limit=10):
        """Get a user's recently viewed documents."""
        return cls.query.filter_by(user_id=user_id)\
            .order_by(cls.viewed_at.desc())\
            .limit(limit)\
            .all()

    def to_dict(self):
        """Convert recent view instance to dictionary."""
        data = super().to_dict()
        data['document'] = self.document.to_dict() if self.document else None
        return data 
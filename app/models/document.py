import os
import uuid
from app.models.base import BaseModel, db
from app.core.config import Config

class Document(BaseModel):
    """Document model for financial document management."""
    
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(512), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    mime_type = db.Column(db.String(100), nullable=False)
    
    # Document metadata
    document_type = db.Column(db.String(50), nullable=False)  # e.g., 'bank_statement', 'invoice', 'tax_form'
    document_date = db.Column(db.Date)
    metadata = db.Column(db.JSON)  # Flexible metadata storage
    
    # Security and access control
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_confidential = db.Column(db.Boolean, default=False)
    access_level = db.Column(db.String(20), default='private')  # private, shared, public
    
    # Version control
    version = db.Column(db.Integer, default=1)
    parent_id = db.Column(db.Integer, db.ForeignKey('documents.id'))
    
    # Relationships
    recent_views = db.relationship('RecentView', backref='document', lazy='dynamic')
    versions = db.relationship(
        'Document',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    def __init__(self, **kwargs):
        """Initialize a new document."""
        super(Document, self).__init__(**kwargs)
        if 'file' in kwargs:
            self._process_file(kwargs['file'])

    def _process_file(self, file):
        """Process and store the uploaded file."""
        unique_id = str(uuid.uuid4())
        filename = f"{self.owner_id}_{self.document_type}_{unique_id}_{file.filename}"
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        self.file_path = filename
        self.file_size = os.path.getsize(file_path)
        self.mime_type = file.content_type
        self.file_type = os.path.splitext(filename)[1][1:].lower()

    def create_version(self, file):
        """Create a new version of the document."""
        new_version = Document(
            title=self.title,
            description=self.description,
            document_type=self.document_type,
            owner_id=self.owner_id,
            is_confidential=self.is_confidential,
            access_level=self.access_level,
            version=self.version + 1,
            parent_id=self.id,
            file=file
        )
        new_version.save()
        return new_version

    def get_full_path(self):
        """Get the full path to the document file."""
        return os.path.join(Config.UPLOAD_FOLDER, self.file_path)

    def to_dict(self):
        """Convert document instance to dictionary."""
        data = super().to_dict()
        # Add additional computed fields
        data['owner'] = self.owner.to_dict() if self.owner else None
        data['download_url'] = f"/api/v1/documents/{self.id}/download"
        return data

    @classmethod
    def get_user_documents(cls, user_id, page=1, per_page=20):
        """Get paginated documents for a user."""
        return cls.query.filter_by(
            owner_id=user_id,
            is_active=True
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

    @classmethod
    def search(cls, query, user_id=None, document_type=None, page=1, per_page=20):
        """Search documents with optional filters."""
        filters = [cls.is_active == True]
        
        if user_id:
            filters.append(cls.owner_id == user_id)
        if document_type:
            filters.append(cls.document_type == document_type)
        if query:
            search = f"%{query}%"
            filters.append(db.or_(
                cls.title.ilike(search),
                cls.description.ilike(search)
            ))
        
        return cls.query.filter(
            *filters
        ).order_by(
            cls.created_at.desc()
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        ) 
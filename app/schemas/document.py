from marshmallow import fields, validates, ValidationError
from app.schemas.base import BaseSchema
from app.core.config import Config

class DocumentSchema(BaseSchema):
    """Schema for document model."""
    
    title = fields.String(required=True)
    description = fields.String()
    file_path = fields.String(dump_only=True)
    file_type = fields.String(dump_only=True)
    file_size = fields.Integer(dump_only=True)
    mime_type = fields.String(dump_only=True)
    document_type = fields.String(required=True)
    document_date = fields.Date()
    metadata = fields.Dict()
    owner_id = fields.Integer(dump_only=True)
    is_confidential = fields.Boolean()
    access_level = fields.String()
    version = fields.Integer(dump_only=True)
    parent_id = fields.Integer(dump_only=True)
    download_url = fields.String(dump_only=True)

    @validates('document_type')
    def validate_document_type(self, value):
        """Validate document type."""
        valid_types = {'bank_statement', 'invoice', 'tax_form', 'receipt', 'contract', 'other'}
        if value not in valid_types:
            raise ValidationError(f'Invalid document type. Must be one of: {", ".join(valid_types)}')

    @validates('access_level')
    def validate_access_level(self, value):
        """Validate access level."""
        if value and value not in {'private', 'shared', 'public'}:
            raise ValidationError('Invalid access level. Must be one of: private, shared, public')

class DocumentUpdateSchema(BaseSchema):
    """Schema for document update operations."""
    
    title = fields.String()
    description = fields.String()
    document_type = fields.String()
    document_date = fields.Date()
    metadata = fields.Dict()
    is_confidential = fields.Boolean()
    access_level = fields.String()

    @validates('document_type')
    def validate_document_type(self, value):
        """Validate document type."""
        if value:
            valid_types = {'bank_statement', 'invoice', 'tax_form', 'receipt', 'contract', 'other'}
            if value not in valid_types:
                raise ValidationError(f'Invalid document type. Must be one of: {", ".join(valid_types)}')

    @validates('access_level')
    def validate_access_level(self, value):
        """Validate access level."""
        if value and value not in {'private', 'shared', 'public'}:
            raise ValidationError('Invalid access level. Must be one of: private, shared, public')

class DocumentSearchSchema(BaseSchema):
    """Schema for document search parameters."""
    
    query = fields.String()
    document_type = fields.String()
    page = fields.Integer(missing=1)
    per_page = fields.Integer(missing=Config.DEFAULT_PAGE_SIZE)

    @validates('per_page')
    def validate_per_page(self, value):
        """Validate items per page."""
        if value > Config.MAX_PAGE_SIZE:
            raise ValidationError(f'Maximum items per page is {Config.MAX_PAGE_SIZE}') 
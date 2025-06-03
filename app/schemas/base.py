from marshmallow import Schema, fields, ValidationError

class BaseSchema(Schema):
    """Base schema with common fields."""
    
    id = fields.Integer(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    is_active = fields.Boolean(dump_only=True)

class PaginationSchema(Schema):
    """Schema for pagination metadata."""
    
    page = fields.Integer(required=True)
    per_page = fields.Integer(required=True)
    total = fields.Integer(required=True)
    pages = fields.Integer(required=True)
    has_next = fields.Boolean(required=True)
    has_prev = fields.Boolean(required=True)

class ErrorSchema(Schema):
    """Schema for error responses."""
    
    message = fields.String(required=True)
    code = fields.String()
    details = fields.Dict() 
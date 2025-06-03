from marshmallow import fields, validates, ValidationError, Schema
from app.schemas.base import BaseSchema

class UserSchema(BaseSchema):
    """Schema for user model."""
    
    email = fields.Email(required=True)
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)
    first_name = fields.String()
    last_name = fields.String()
    role = fields.String(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    last_login = fields.DateTime(dump_only=True)

    @validates('username')
    def validate_username(self, value):
        """Validate username format."""
        if len(value) < 3:
            raise ValidationError('Username must be at least 3 characters long')
        if not value.isalnum():
            raise ValidationError('Username must contain only letters and numbers')

    @validates('password')
    def validate_password(self, value):
        """Validate password strength."""
        if len(value) < 8:
            raise ValidationError('Password must be at least 8 characters long')
        if not any(char.isupper() for char in value):
            raise ValidationError('Password must contain at least one uppercase letter')
        if not any(char.islower() for char in value):
            raise ValidationError('Password must contain at least one lowercase letter')
        if not any(char.isdigit() for char in value):
            raise ValidationError('Password must contain at least one number')

class UserUpdateSchema(BaseSchema):
    """Schema for user update operations."""
    
    first_name = fields.String()
    last_name = fields.String()
    current_password = fields.String(load_only=True)
    new_password = fields.String(load_only=True)

    @validates('new_password')
    def validate_new_password(self, value):
        """Validate new password strength."""
        if value:
            if len(value) < 8:
                raise ValidationError('Password must be at least 8 characters long')
            if not any(char.isupper() for char in value):
                raise ValidationError('Password must contain at least one uppercase letter')
            if not any(char.islower() for char in value):
                raise ValidationError('Password must contain at least one lowercase letter')
            if not any(char.isdigit() for char in value):
                raise ValidationError('Password must contain at least one number')

class LoginSchema(Schema):
    """Schema for login requests."""
    
    username = fields.String(required=True)
    password = fields.String(required=True)

class TokenSchema(Schema):
    """Schema for authentication tokens."""
    
    access_token = fields.String(required=True)
    refresh_token = fields.String(required=True)
    token_type = fields.String(required=True)
    expires_in = fields.Integer(required=True) 
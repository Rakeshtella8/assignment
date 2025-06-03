from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    create_access_token
)
from marshmallow import ValidationError

from app.models.user import User
from app.schemas.user import UserSchema, LoginSchema, TokenSchema
from app.core.security import create_tokens, log_activity
from app import limiter

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
@limiter.limit("5 per minute")
def register():
    """Register a new user."""
    try:
        data = UserSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 422

    if User.get_by_email(data['email']):
        return jsonify({'message': 'Email already registered'}), 409
    
    if User.get_by_username(data['username']):
        return jsonify({'message': 'Username already taken'}), 409

    user = User(**data)
    user.save()

    # Generate tokens
    tokens = create_tokens(user.id)
    
    return jsonify({
        'message': 'User registered successfully',
        'user': UserSchema().dump(user),
        'tokens': TokenSchema().dump(tokens)
    }), 201

@auth_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Authenticate a user and return tokens."""
    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 422

    user = User.get_by_username(data['username'])
    if not user or not user.check_password(data['password']):
        return jsonify({'message': 'Invalid credentials'}), 401

    # Update last login
    user.last_login = datetime.utcnow()
    user.save()

    # Generate tokens
    tokens = create_tokens(user.id)

    return jsonify({
        'message': 'Login successful',
        'user': UserSchema().dump(user),
        'tokens': TokenSchema().dump(tokens)
    })

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token."""
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Generate new access token
    access_token = create_access_token(identity=current_user_id)

    return jsonify({
        'access_token': access_token,
        'token_type': 'bearer',
        'expires_in': current_app.config['JWT_ACCESS_TOKEN_EXPIRES'].total_seconds()
    })

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
@log_activity('profile_view')
def get_me():
    """Get current user's profile."""
    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(UserSchema().dump(user)) 
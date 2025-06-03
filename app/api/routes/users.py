from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.models.user import User
from app.schemas.user import UserSchema, UserUpdateSchema
from app.core.security import admin_required, log_activity

users_bp = Blueprint('users', __name__)

@users_bp.route('', methods=['GET'])
@jwt_required()
@admin_required()
def list_users():
    """List all users (admin only)."""
    users = User.get_all()
    return jsonify(UserSchema(many=True).dump(users))

@users_bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_user(user_id):
    """Get a specific user (admin only)."""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify(UserSchema().dump(user))

@users_bp.route('/profile', methods=['PUT'])
@jwt_required()
@log_activity('profile_update')
def update_profile():
    """Update current user's profile."""
    try:
        data = UserUpdateSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({'message': 'Validation error', 'errors': e.messages}), 422

    current_user_id = get_jwt_identity()
    user = User.get_by_id(current_user_id)
    
    if not user:
        return jsonify({'message': 'User not found'}), 404

    # Check current password if changing password
    if data.get('new_password'):
        if not data.get('current_password'):
            return jsonify({'message': 'Current password is required'}), 400
        if not user.check_password(data['current_password']):
            return jsonify({'message': 'Current password is incorrect'}), 401
        user.set_password(data['new_password'])
        data.pop('new_password')
        data.pop('current_password')

    # Update other fields
    user.update(**data)

    return jsonify({
        'message': 'Profile updated successfully',
        'user': UserSchema().dump(user)
    })

@users_bp.route('/<int:user_id>/verify', methods=['POST'])
@jwt_required()
@admin_required()
@log_activity('user_verify')
def verify_user(user_id):
    """Verify a user (admin only)."""
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.is_verified = True
    user.save()

    return jsonify({
        'message': 'User verified successfully',
        'user': UserSchema().dump(user)
    })

@users_bp.route('/<int:user_id>/role', methods=['PUT'])
@jwt_required()
@admin_required()
@log_activity('role_update')
def update_role(user_id):
    """Update user's role (admin only)."""
    data = request.get_json()
    if 'role' not in data:
        return jsonify({'message': 'Role is required'}), 400

    if data['role'] not in {'user', 'admin'}:
        return jsonify({'message': 'Invalid role'}), 400

    user = User.get_by_id(user_id)
    if not user:
        return jsonify({'message': 'User not found'}), 404

    user.role = data['role']
    user.save()

    return jsonify({
        'message': 'User role updated successfully',
        'user': UserSchema().dump(user)
    }) 
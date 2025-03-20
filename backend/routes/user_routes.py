"""
User management API routes.
"""
from flask import Blueprint, request, jsonify, g
from .auth import login_required
from models.user import User

user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/profile', methods=['GET'])
@login_required
def get_user_profile():
    """
    Get the current user's profile information.
    
    Returns:
        HTTP 200 with user profile data
        HTTP 404 if user not found
    """
    user_id = g.user_id
    
    # Get user from database
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Return user profile data
    return jsonify({
        "user_id": user.user_id,
        "username": user.username,
        "max_yubikeys": user.max_yubikeys,
        "created_at": user.created_at if hasattr(user, 'created_at') else None
    }), 200

@user_blueprint.route('/profile', methods=['PUT'])
@login_required
def update_user_profile():
    """
    Update the current user's profile information.
    
    Returns:
        HTTP 200 with updated user profile data
        HTTP 400 if request is invalid
        HTTP 404 if user not found
    """
    user_id = g.user_id
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Get user from database
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Update user fields
    # Only allow updating certain fields
    username = data.get('username')
    if username:
        user.username = username
    
    # Save changes to database
    success = user.update()
    if not success:
        return jsonify({"error": "Failed to update user"}), 500
    
    # Return updated user data
    return jsonify({
        "user_id": user.user_id,
        "username": user.username,
        "max_yubikeys": user.max_yubikeys,
        "created_at": user.created_at if hasattr(user, 'created_at') else None
    }), 200

@user_blueprint.route('/register', methods=['POST'])
def register_user():
    """
    Register a new user.
    
    Returns:
        HTTP 201 with user ID if created successfully
        HTTP 400 if request is invalid
        HTTP 409 if username already exists
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    username = data.get('username')
    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    # Check if user already exists
    existing_user = User.get_by_username(username)
    if existing_user:
        return jsonify({"error": "Username already exists"}), 409
    
    # Create new user
    user = User.create(username=username)
    if not user:
        return jsonify({"error": "Failed to create user"}), 500
    
    return jsonify({
        "message": "User created successfully",
        "user_id": user.user_id
    }), 201 
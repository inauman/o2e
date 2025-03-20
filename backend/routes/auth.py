"""
Authentication routes for the API.
"""
from flask import Blueprint, request, jsonify, session, g
from functools import wraps
import jwt
from datetime import datetime, timedelta

auth_blueprint = Blueprint('auth', __name__)

# Mock function for JWT secret
def get_jwt_secret():
    """Get the JWT secret for token verification."""
    from flask import current_app
    return current_app.config.get('JWT_SECRET_KEY', 'default-secret-key')

def login_required(f):
    """
    Decorator to require authentication for routes.
    
    This checks for a valid JWT token in the Authorization header.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authentication required"}), 401
        
        token = auth_header.split('Bearer ')[1]
        
        try:
            # Verify and decode the JWT token
            payload = jwt.decode(token, get_jwt_secret(), algorithms=['HS256'])
            
            # Check if token is expired
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                return jsonify({"error": "Token expired"}), 401
            
            # Set user ID in Flask g object for this request
            g.user_id = payload.get('sub')
            
            return f(*args, **kwargs)
        except jwt.PyJWTError as e:
            return jsonify({"error": f"Invalid token: {str(e)}"}), 401
            
    return decorated_function

@auth_blueprint.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token.
    
    For testing/development only - production would use WebAuthn.
    """
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    # For development/testing, we'll create a simple JWT token
    # In production, this would validate credentials properly
    from flask import current_app
    
    # Use simple user ID for demo
    user_id = f"user-{username}"
    
    # Create token with expiration
    token_expiry = datetime.utcnow() + timedelta(hours=1)
    token_payload = {
        "sub": user_id,
        "exp": token_expiry,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        token_payload,
        get_jwt_secret(),
        algorithm='HS256'
    )
    
    # Set user in session
    session['user_id'] = user_id
    
    return jsonify({
        "token": token,
        "expiresIn": 3600,
        "user_id": user_id
    }), 200

@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    """Log out user by clearing the session."""
    session.clear()
    return jsonify({"success": True}), 200

@auth_blueprint.route('/verify', methods=['GET'])
@login_required
def verify_token():
    """
    Verify that the provided token is valid.
    
    This route is protected by the login_required decorator.
    """
    # If we get here, the token is valid
    return jsonify({
        "valid": True,
        "user_id": g.user_id
    }), 200 
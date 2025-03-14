"""
Authentication service for the application.
"""
import functools
from flask import request, jsonify, g
import jwt
import os
from datetime import datetime, timedelta

from models.user import User

# Secret key for JWT
JWT_SECRET = os.environ.get("JWT_SECRET", "development_secret_key")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=1)


def generate_token(user_id: str) -> str:
    """
    Generate a JWT token for a user.
    
    Args:
        user_id: The user ID to generate a token for
        
    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + JWT_EXPIRATION_DELTA,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> tuple:
    """
    Verify a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Tuple of (is_valid, user_id or error message)
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return True, payload["user_id"]
    except jwt.ExpiredSignatureError:
        return False, "Token has expired"
    except jwt.InvalidTokenError:
        return False, "Invalid token"


def login_required(f):
    """
    Decorator to require login for a route.
    
    This decorator checks for a valid JWT token in the Authorization header
    and sets g.user to the authenticated user if found.
    """
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if token is in header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid authorization header"}), 401
        
        # Extract token
        token = auth_header[7:]  # Remove "Bearer " prefix
        
        # Verify token
        is_valid, result = verify_token(token)
        if not is_valid:
            return jsonify({"error": result}), 401
        
        # Get user from database
        user = User.get_by_id(result)
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        # Set user in Flask g object
        g.user = user
        
        return f(*args, **kwargs)
    
    return decorated_function 
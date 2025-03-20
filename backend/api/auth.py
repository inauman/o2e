"""
Authentication API routes for YubiKey Manager
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, g
from services.webauthn_service import WebAuthnService
from models.user import User
from models.yubikey import YubiKey
import logging
import base64

# Create a blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize WebAuthn service
webauthn_service = WebAuthnService()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@auth_bp.route('/register', methods=['GET'])
def register_view():
    """Render the registration page"""
    return render_template('register.html')

@auth_bp.route('/register/begin', methods=['POST'])
def register_begin():
    """
    Begin the registration process for a new user.
    
    Request body:
    {
        "email": "user@example.com"
    }
    
    Returns:
        200: Registration options for WebAuthn
        400: Invalid request
        409: User already exists
        500: Internal server error
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Check if user already exists
        existing_user = User.get_by_email(email)
        if existing_user:
            return jsonify({"error": "User already exists"}), 409
        
        # Create a new user
        user = User.create(email=email)
        if not user:
            return jsonify({"error": "Failed to create user"}), 500
        
        # Generate registration options
        try:
            options, state = webauthn_service.generate_registration_options(
                user_id=user.user_id,
                email=user.email
            )
            
            # Store state in session
            session['webauthn_state'] = state
            
            return jsonify(options), 200
            
        except Exception as e:
            # If registration fails, delete the user
            user.delete()
            raise e
            
    except Exception as e:
        logger.error(f"Error in register_begin: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/register/complete', methods=['POST'])
def register_complete():
    """
    Complete the registration process by verifying the WebAuthn credential.
    
    Request body:
    {
        "credential": {
            "id": "base64url",
            "rawId": "base64url",
            "response": {
                "clientDataJSON": "base64url",
                "attestationObject": "base64url"
            },
            "type": "public-key"
        },
        "nickname": "optional string"
    }
    
    Returns:
        201: Registration successful
        400: Invalid request
        500: Internal server error
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        # Get state from session
        state = session.get('webauthn_state')
        if not state:
            return jsonify({"error": "Registration session expired"}), 400
        
        data = request.json
        credential = data.get('credential')
        nickname = data.get('nickname')
        
        if not credential:
            return jsonify({"error": "Credential is required"}), 400
        
        # Verify registration response
        result = webauthn_service.verify_registration_response(
            credential=credential,
            state=state,
            nickname=nickname
        )
        
        if not result['success']:
            return jsonify({"error": result.get('error', 'Registration failed')}), 400
        
        # Clear state from session
        session.pop('webauthn_state', None)
        
        return jsonify({
            "user_id": result['user_id'],
            "credential_id": result['credential_id'],
            "is_primary": result['is_primary']
        }), 201
        
    except Exception as e:
        logger.error(f"Error in register_complete: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/authenticate', methods=['GET'])
def authenticate_view():
    """Render the authentication page"""
    return render_template('authenticate.html')

@auth_bp.route('/authenticate/begin', methods=['POST'])
def authenticate_begin():
    """
    Begin the authentication process.
    
    Request body:
    {
        "email": "user@example.com"
    }
    
    Returns:
        200: Authentication options for WebAuthn
        400: Invalid request
        404: User not found
        500: Internal server error
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.json
        email = data.get('email')
        
        if not email:
            return jsonify({"error": "Email is required"}), 400
        
        # Get user
        user = User.get_by_email(email)
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Generate authentication options
        try:
            options, state = webauthn_service.generate_authentication_options(user.user_id)
            
            # Store state in session
            session['webauthn_state'] = state
            
            return jsonify(options), 200
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
            
    except Exception as e:
        logger.error(f"Error in authenticate_begin: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/authenticate/complete', methods=['POST'])
def authenticate_complete():
    """
    Complete the authentication process by verifying the WebAuthn assertion.
    
    Request body:
    {
        "credential": {
            "id": "base64url",
            "rawId": "base64url",
            "response": {
                "clientDataJSON": "base64url",
                "authenticatorData": "base64url",
                "signature": "base64url",
                "userHandle": "base64url"
            },
            "type": "public-key"
        }
    }
    
    Returns:
        200: Authentication successful
        400: Invalid request
        401: Authentication failed
        500: Internal server error
    """
    try:
        # Validate request
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        # Get state from session
        state = session.get('webauthn_state')
        if not state:
            return jsonify({"error": "Authentication session expired"}), 400
        
        data = request.json
        credential = data.get('credential')
        
        if not credential:
            return jsonify({"error": "Credential is required"}), 400
        
        # Verify authentication response
        result = webauthn_service.verify_authentication_response(
            credential=credential,
            state=state
        )
        
        if not result['success']:
            return jsonify({"error": result.get('error', 'Authentication failed')}), 401
        
        # Clear state from session
        session.pop('webauthn_state', None)
        
        # Store user info in session
        session['user_id'] = result['user_id']
        session['email'] = result['email']
        
        return jsonify({
            "user_id": result['user_id'],
            "email": result['email'],
            "credential_id": result['credential_id'],
            "is_primary": result['is_primary']
        }), 200
        
    except Exception as e:
        logger.error(f"Error in authenticate_complete: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Log out the user by clearing session"""
    session.clear()
    return jsonify({"success": True, "redirect": url_for('index')})

@auth_bp.route('/delete-credential', methods=['POST'])
def delete_credential():
    """Delete a YubiKey credential"""
    try:
        # Get username from either form data or JSON request
        if request.is_json:
            username = request.json.get('username')
            logger.info(f"JSON request received with username: {username}")
        else:
            username = request.form.get('username')
            logger.info(f"Form data request received with username: {username}")
        
        if not username:
            logger.error("Username is required but not provided")
            return jsonify({"error": "Username is required"}), 400
        
        # Get user by username
        user = User.get_by_username(username)
        if not user:
            logger.error(f"User not found with username: {username}")
            return jsonify({"error": "User not found"}), 404
            
        # Get the YubiKey credential for this user
        yubikeys = YubiKey.get_yubikeys_by_user_id(user.user_id)
        
        if not yubikeys:
            logger.error(f"No YubiKey found for username: {username}")
            return jsonify({"error": "No YubiKey found for this user"}), 404
            
        if len(yubikeys) == 1:
            logger.error(f"Cannot delete the only YubiKey for username: {username}")
            return jsonify({"error": "Cannot delete your only YubiKey. You must have at least one YubiKey registered."}), 400
            
        # Delete each YubiKey credential for this user
        success = True
        for yubikey in yubikeys:
            if not webauthn_service.revoke_yubikey(user.user_id, yubikey.credential_id):
                success = False
                logger.error(f"Failed to delete YubiKey credential {yubikey.credential_id}")
        
        if not success:
            return jsonify({"error": "Failed to delete one or more credentials"}), 500
        
        logger.info(f"Successfully deleted credentials for username: {username}")
        return jsonify({"success": True})
    except Exception as e:
        logger.error(f"Error in delete_credential: {str(e)}")
        return jsonify({"error": str(e)}), 500 
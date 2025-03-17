"""
Authentication API routes for YubiKey Bitcoin Seed Storage
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from services.webauthn_service import WebAuthnService
import logging
from models.user import User

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

@auth_bp.route('/register/begin', methods=['POST', 'OPTIONS'])
def register_begin():
    """Begin the registration process by generating challenge"""
    try:
        # Handle preflight requests for CORS
        if request.method == 'OPTIONS':
            return '', 200
            
        # Get username from either form data or JSON request
        if request.is_json:
            username = request.json.get('username')
            logger.info(f"JSON request received with username: {username}")
        else:
            username = request.form.get('username')
            logger.info(f"Form data request received with username: {username}")
            
        # Handle case where username might be in request data
        if not username and request.data:
            try:
                import json
                data = json.loads(request.data)
                username = data.get('username')
                logger.info(f"Extracted username from request data: {username}")
            except Exception as e:
                logger.error(f"Failed to parse request data: {e}")
        
        if not username:
            logger.error("Username is required but not provided")
            return jsonify({"error": "Username is required"}), 400
            
        logger.info(f"Generating registration options for username: {username}")
        
        # Get or create user
        user = User.get_by_username(username)
        if not user:
            logger.info(f"Creating new user with username: {username}")
            user = User.create(username=username)
        
        # Generate registration options with user_id and username
        options, state = webauthn_service.generate_registration_options(user.user_id, username)
        
        session['registration_state'] = state
        logger.info("Registration state stored in session")
        
        return jsonify(options)
    except Exception as e:
        logger.error(f"Error in register_begin: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/register/complete', methods=['POST', 'OPTIONS'])
def register_complete():
    """Complete the registration process by verifying attestation"""
    try:
        # Handle preflight requests for CORS
        if request.method == 'OPTIONS':
            return '', 200
            
        logger.info("Processing registration completion")
        credential = request.json
        state = session.get('registration_state')
        
        if not state:
            logger.error("Registration state not found in session")
            return jsonify({"error": "Registration session expired"}), 400
            
        logger.info("Verifying registration response")
        result = webauthn_service.verify_registration_response(credential, state)
        
        # On success, redirect to authenticate page
        if result.get('success'):
            logger.info("Registration successful")
            return jsonify({"success": True, "redirect": url_for('auth.authenticate_view')})
        
        logger.error(f"Registration failed: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in register_complete: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/authenticate', methods=['GET'])
def authenticate_view():
    """Render the authentication page"""
    return render_template('authenticate.html')

@auth_bp.route('/authenticate/begin', methods=['POST', 'OPTIONS'])
def authenticate_begin():
    """Begin the authentication process by generating challenge"""
    try:
        # Handle preflight requests for CORS
        if request.method == 'OPTIONS':
            return '', 200
            
        # Get username from either form data or JSON request
        if request.is_json:
            username = request.json.get('username')
            logger.info(f"JSON request received with username: {username}")
        else:
            username = request.form.get('username')
            logger.info(f"Form data request received with username: {username}")
            
        # Handle case where username might be in request data
        if not username and request.data:
            try:
                import json
                data = json.loads(request.data)
                username = data.get('username')
                logger.info(f"Extracted username from request data: {username}")
            except Exception as e:
                logger.error(f"Failed to parse request data: {e}")
        
        if not username:
            logger.error("Username is required but not provided")
            return jsonify({"error": "Username is required"}), 400
        
        # Get user by username
        user = User.get_by_username(username)
        if not user:
            logger.error(f"User not found with username: {username}")
            return jsonify({"error": "User not found"}), 404
            
        logger.info(f"Generating authentication options for username: {username}")
        # Pass user_id instead of username
        options, state = webauthn_service.generate_authentication_options(user.user_id)
        
        session['authentication_state'] = state
        logger.info("Authentication state stored in session")
        
        return jsonify(options)
    except Exception as e:
        logger.error(f"Error in authenticate_begin: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/authenticate/complete', methods=['POST', 'OPTIONS'])
def authenticate_complete():
    """Complete the authentication process by verifying assertion"""
    try:
        # Handle preflight requests for CORS
        if request.method == 'OPTIONS':
            return '', 200
            
        logger.info("Processing authentication completion")
        credential = request.json
        state = session.get('authentication_state')
        
        if not state:
            logger.error("Authentication state not found in session")
            return jsonify({"error": "Authentication session expired"}), 400
            
        logger.info("Verifying authentication response")
        result = webauthn_service.verify_authentication_response(credential, state)
        
        # On success, set session and redirect to index
        if result.get('success'):
            logger.info("Authentication successful")
            session['authenticated'] = True
            session['username'] = result.get('username')
            return jsonify({"success": True, "redirect": url_for('index')})
        
        logger.error(f"Authentication failed: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in authenticate_complete: {str(e)}")
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Log out the user by clearing session"""
    session.clear()
    return jsonify({"success": True, "redirect": url_for('index')}) 
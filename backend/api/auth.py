"""
Authentication API routes for YubiKey Bitcoin Seed Storage
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from ..services.webauthn_service import WebAuthnService

# Create a blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Initialize WebAuthn service
webauthn_service = WebAuthnService()

@auth_bp.route('/register', methods=['GET'])
def register_view():
    """Render the registration page"""
    return render_template('register.html')

@auth_bp.route('/register/begin', methods=['POST'])
def register_begin():
    """Begin the registration process by generating challenge"""
    try:
        username = request.form.get('username')
        if not username:
            return jsonify({"error": "Username is required"}), 400
            
        options, state = webauthn_service.generate_registration_options(username)
        session['registration_state'] = state
        return jsonify(options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/register/complete', methods=['POST'])
def register_complete():
    """Complete the registration process by verifying attestation"""
    try:
        credential = request.json
        state = session.get('registration_state')
        
        if not state:
            return jsonify({"error": "Registration session expired"}), 400
            
        result = webauthn_service.verify_registration_response(credential, state)
        
        # On success, redirect to authenticate page
        if result.get('success'):
            return jsonify({"success": True, "redirect": url_for('auth.authenticate_view')})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/authenticate', methods=['GET'])
def authenticate_view():
    """Render the authentication page"""
    return render_template('authenticate.html')

@auth_bp.route('/authenticate/begin', methods=['POST'])
def authenticate_begin():
    """Begin the authentication process by generating challenge"""
    try:
        username = request.form.get('username')
        if not username:
            return jsonify({"error": "Username is required"}), 400
            
        options, state = webauthn_service.generate_authentication_options(username)
        session['authentication_state'] = state
        return jsonify(options)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/authenticate/complete', methods=['POST'])
def authenticate_complete():
    """Complete the authentication process by verifying assertion"""
    try:
        credential = request.json
        state = session.get('authentication_state')
        
        if not state:
            return jsonify({"error": "Authentication session expired"}), 400
            
        result = webauthn_service.verify_authentication_response(credential, state)
        
        # On success, set session and redirect to index
        if result.get('success'):
            session['authenticated'] = True
            session['username'] = result.get('username')
            return jsonify({"success": True, "redirect": url_for('index')})
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Log out the user by clearing session"""
    session.clear()
    return jsonify({"success": True, "redirect": url_for('index')}) 
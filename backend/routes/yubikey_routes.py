"""
API routes for YubiKey management.
"""
from flask import Blueprint, request, jsonify, g
import json
import uuid
import os
import base64

from models.yubikey import YubiKey
from models.yubikey_salt import YubiKeySalt
from models.database import DatabaseManager
from services.webauthn_service import WebAuthnService
from services.auth_service import login_required
from utils.validation import validate_request
from utils.logging import get_logger

logger = get_logger(__name__)

# Blueprint for YubiKey routes
yubikey_blueprint = Blueprint('yubikey', __name__, url_prefix='/api/yubikey')

# Initialize services
webauthn_service = WebAuthnService()


@yubikey_blueprint.route('/yubikeys/register/options', methods=['POST'])
@login_required
def get_registration_options():
    """
    Get WebAuthn registration options for a new YubiKey.
    
    Request body:
    {
        "username": "string"  # Optional, defaults to user's username
    }
    
    Returns:
        200: Registration options
        400: Invalid request
        401: Unauthorized
        403: Maximum YubiKeys reached
        500: Internal server error
    """
    # Validate request
    schema = {
        "type": "object",
        "properties": {
            "username": {"type": "string"}
        }
    }
    
    valid, errors = validate_request(request, schema)
    if not valid:
        return jsonify({"error": "Invalid request", "details": errors}), 400
    
    # Get authenticated user from context
    user = g.user
    
    # Get username from request or use user's username
    data = request.json or {}
    username = data.get("username", user.username)
    
    try:
        # Check if user can register another YubiKey
        if not user.can_register_yubikey():
            return jsonify({
                "error": "Maximum YubiKeys reached",
                "max_yubikeys": user.max_yubikeys,
                "current_count": user.count_yubikeys()
            }), 403
        
        # Generate registration options
        options, state = webauthn_service.generate_registration_options(user.user_id, username)
        
        # Store state in session
        # In a real implementation, this would be stored in a database or cache
        # For now, we'll store it in the user's session
        g.webauthn_state = state
        
        return jsonify(options), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@yubikey_blueprint.route('/yubikeys/register/verify', methods=['POST'])
@login_required
def verify_registration():
    """
    Verify WebAuthn registration response and store the YubiKey credential.
    
    Request body:
    {
        "credential": {
            "id": "string",
            "rawId": "string",
            "response": {
                "clientDataJSON": "string",
                "attestationObject": "string"
            },
            "type": "string"
        },
        "nickname": "string"  # Optional nickname for the YubiKey
    }
    
    Returns:
        201: YubiKey registered
        400: Invalid request
        401: Unauthorized
        500: Internal server error
    """
    # Validate request
    schema = {
        "type": "object",
        "required": ["credential"],
        "properties": {
            "credential": {
                "type": "object",
                "required": ["id", "rawId", "response", "type"],
                "properties": {
                    "id": {"type": "string"},
                    "rawId": {"type": "string"},
                    "response": {
                        "type": "object",
                        "required": ["clientDataJSON", "attestationObject"],
                        "properties": {
                            "clientDataJSON": {"type": "string"},
                            "attestationObject": {"type": "string"}
                        }
                    },
                    "type": {"type": "string"}
                }
            },
            "nickname": {"type": "string"}
        }
    }
    
    valid, errors = validate_request(request, schema)
    if not valid:
        return jsonify({"error": "Invalid request", "details": errors}), 400
    
    # Get authenticated user from context
    user = g.user
    
    # Get state from session
    state = getattr(g, 'webauthn_state', None)
    if not state:
        return jsonify({"error": "Registration session expired"}), 400
    
    # Get request data
    data = request.json
    credential = data["credential"]
    nickname = data.get("nickname")
    
    try:
        # Verify registration response
        result = webauthn_service.verify_registration_response(credential, state, nickname)
        
        if not result["success"]:
            return jsonify({"error": result.get("error", "Registration failed")}), 400
        
        # Clear state from session
        delattr(g, 'webauthn_state')
        
        return jsonify({
            "credential_id": result["credential_id"],
            "is_primary": result["is_primary"]
        }), 201
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@yubikey_blueprint.route('/yubikeys/authenticate/options', methods=['POST'])
def get_authentication_options():
    """
    Get WebAuthn authentication options.
    
    Request body:
    {
        "user_id": "string"  # The ID of the user to authenticate
    }
    
    Returns:
        200: Authentication options
        400: Invalid request
        404: User not found or no YubiKeys registered
        500: Internal server error
    """
    # Validate request
    schema = {
        "type": "object",
        "required": ["user_id"],
        "properties": {
            "user_id": {"type": "string"}
        }
    }
    
    valid, errors = validate_request(request, schema)
    if not valid:
        return jsonify({"error": "Invalid request", "details": errors}), 400
    
    # Get request data
    data = request.json
    user_id = data["user_id"]
    
    try:
        # Generate authentication options
        options, state = webauthn_service.generate_authentication_options(user_id)
        
        # Store state in session
        # In a real implementation, this would be stored in a database or cache
        # For now, we'll store it in the request context
        g.webauthn_state = state
        
        return jsonify(options), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@yubikey_blueprint.route('/yubikeys/authenticate/verify', methods=['POST'])
def verify_authentication():
    """
    Verify WebAuthn authentication response.
    
    Request body:
    {
        "credential": {
            "id": "string",
            "rawId": "string",
            "response": {
                "clientDataJSON": "string",
                "authenticatorData": "string",
                "signature": "string",
                "userHandle": "string"
            },
            "type": "string"
        }
    }
    
    Returns:
        200: Authentication successful
        400: Invalid request
        401: Authentication failed
        500: Internal server error
    """
    # Validate request
    schema = {
        "type": "object",
        "required": ["credential"],
        "properties": {
            "credential": {
                "type": "object",
                "required": ["id", "rawId", "response", "type"],
                "properties": {
                    "id": {"type": "string"},
                    "rawId": {"type": "string"},
                    "response": {
                        "type": "object",
                        "required": ["clientDataJSON", "authenticatorData", "signature"],
                        "properties": {
                            "clientDataJSON": {"type": "string"},
                            "authenticatorData": {"type": "string"},
                            "signature": {"type": "string"},
                            "userHandle": {"type": "string"}
                        }
                    },
                    "type": {"type": "string"}
                }
            }
        }
    }
    
    valid, errors = validate_request(request, schema)
    if not valid:
        return jsonify({"error": "Invalid request", "details": errors}), 400
    
    # Get state from session
    state = getattr(g, 'webauthn_state', None)
    if not state:
        return jsonify({"error": "Authentication session expired"}), 400
    
    # Get request data
    data = request.json
    credential = data["credential"]
    
    try:
        # Verify authentication response
        result = webauthn_service.verify_authentication_response(credential, state)
        
        if not result["success"]:
            return jsonify({"error": result.get("error", "Authentication failed")}), 401
        
        # Clear state from session
        delattr(g, 'webauthn_state')
        
        # Generate an authentication token
        from services.auth_service import generate_token
        token = generate_token(result["user_id"])
        
        return jsonify({
            "token": token,
            "user_id": result["user_id"],
            "credential_id": result["credential_id"],
            "is_primary": result["is_primary"]
        }), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@yubikey_blueprint.route('/yubikeys', methods=['GET'])
@login_required
def list_yubikeys():
    """
    List all YubiKeys registered for the authenticated user.
    
    Returns:
        200: List of YubiKeys
        401: Unauthorized
        500: Internal server error
    """
    # Get authenticated user from context
    user = g.user
    
    try:
        # List YubiKeys
        yubikeys = webauthn_service.list_yubikeys(user.user_id)
        
        return jsonify(yubikeys), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@yubikey_blueprint.route('/yubikeys/<credential_id>/primary', methods=['PUT'])
@login_required
def set_primary_yubikey(credential_id):
    """
    Set a YubiKey as the primary YubiKey for the authenticated user.
    
    Args:
        credential_id: The ID of the credential to set as primary
    
    Returns:
        200: YubiKey set as primary
        401: Unauthorized
        403: Forbidden (not owner)
        404: YubiKey not found
        500: Internal server error
    """
    # Get authenticated user from context
    user = g.user
    
    try:
        # Get the YubiKey
        yubikey = YubiKey.get_by_credential_id(credential_id)
        
        if not yubikey:
            return jsonify({"error": "YubiKey not found"}), 404
        
        if yubikey.user_id != user.user_id:
            return jsonify({"error": "You are not authorized to modify this YubiKey"}), 403
        
        # Set as primary
        success = webauthn_service.set_primary_yubikey(user.user_id, credential_id)
        
        if not success:
            return jsonify({"error": "Failed to set YubiKey as primary"}), 500
        
        return jsonify({"success": True}), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@yubikey_blueprint.route('/yubikeys/<credential_id>', methods=['DELETE'])
@login_required
def revoke_yubikey(credential_id):
    """
    Revoke a YubiKey credential.
    
    Args:
        credential_id: The ID of the credential to revoke
    
    Returns:
        200: YubiKey revoked
        401: Unauthorized
        403: Forbidden (not owner or only YubiKey)
        404: YubiKey not found
        500: Internal server error
    """
    # Get authenticated user from context
    user = g.user
    
    try:
        # Get the YubiKey
        yubikey = YubiKey.get_by_credential_id(credential_id)
        
        if not yubikey:
            return jsonify({"error": "YubiKey not found"}), 404
        
        if yubikey.user_id != user.user_id:
            return jsonify({"error": "You are not authorized to revoke this YubiKey"}), 403
        
        # Check if this is the only YubiKey
        yubikeys = YubiKey.get_yubikeys_by_user_id(user.user_id)
        if len(yubikeys) == 1:
            return jsonify({"error": "Cannot revoke the only YubiKey"}), 403
        
        # Revoke the YubiKey
        success = webauthn_service.revoke_yubikey(user.user_id, credential_id)
        
        if not success:
            return jsonify({"error": "Failed to revoke YubiKey"}), 500
        
        return jsonify({"success": True}), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@yubikey_blueprint.route('/register', methods=['POST'])
@login_required
def register_yubikey():
    """
    Register a YubiKey by creating a new salt.
    
    Request body:
    {
        "credential_id": "string",
        "purpose": "string"  # Optional, defaults to "seed_encryption"
    }
    
    Returns:
        201: YubiKey salt registered
        400: Invalid request
        401: Unauthorized
        500: Internal server error
    """
    # Validate request
    schema = {
        "type": "object",
        "required": ["credential_id"],
        "properties": {
            "credential_id": {"type": "string"},
            "purpose": {"type": "string"}
        }
    }
    
    valid, errors = validate_request(request, schema)
    if not valid:
        return jsonify({
            "success": False,
            "error": "Invalid request",
            "details": errors
        }), 400
    
    # Get request data
    data = request.json
    credential_id = data["credential_id"]
    purpose = data.get("purpose", "seed_encryption")
    
    try:
        # Generate a new salt
        salt = os.urandom(32)
        
        # Create YubiKey salt
        yubikey_salt = YubiKeySalt.create(
            credential_id=credential_id,
            salt=salt,
            purpose=purpose
        )
        
        if yubikey_salt is None:
            return jsonify({
                "success": False,
                "error": "Failed to create YubiKey salt. Credential may not exist."
            }), 500
        
        return jsonify({
            "success": True,
            "salt_id": yubikey_salt.salt_id,
            "salt": salt.hex()
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": f"Internal server error: {str(e)}"
        }), 500


@yubikey_blueprint.route('/salts', methods=['GET'])
@login_required
def get_yubikey_salts():
    """
    Get all salts associated with a YubiKey credential ID.
    
    Query parameters:
    - credential_id: The credential ID of the YubiKey
    - purpose: Optional filter by purpose
    
    Returns:
    {
        "success": true,
        "salts": [
            {
                "salt_id": "string",
                "credential_id": "string",
                "salt": "hex_string",
                "creation_date": "ISO date string",
                "last_used": "ISO date string or null",
                "purpose": "string"
            },
            ...
        ]
    }
    """
    try:
        credential_id = request.args.get('credential_id')
        purpose = request.args.get('purpose')
        
        if not credential_id:
            return jsonify({"success": False, "error": "Credential ID is required"}), 400
        
        # Get salts by credential ID and optional purpose
        if purpose:
            salts = YubiKeySalt.get_by_credential_id(credential_id, purpose)
        else:
            salts = YubiKeySalt.get_by_credential_id(credential_id)
        
        # Convert salts to dictionaries
        salt_dicts = [salt.to_dict() for salt in salts]
        
        return jsonify({
            "success": True,
            "salts": salt_dicts
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting YubiKey salts: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@yubikey_blueprint.route('/salt/<salt_id>', methods=['GET'])
@login_required
def get_yubikey_salt(salt_id):
    """
    Get a specific salt by its ID.
    
    Path parameters:
    - salt_id: The ID of the salt to retrieve
    
    Returns:
    {
        "success": true,
        "salt": {
            "salt_id": "string",
            "credential_id": "string",
            "salt": "hex_string",
            "creation_date": "ISO date string",
            "last_used": "ISO date string or null",
            "purpose": "string"
        }
    }
    """
    try:
        # Get salt by ID
        salt = YubiKeySalt.get_by_id(salt_id)
        
        if not salt:
            return jsonify({"success": False, "error": "Salt not found"}), 404
        
        # Update last used time
        salt.update_last_used()
        
        return jsonify({
            "success": True,
            "salt": salt.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting YubiKey salt: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@yubikey_blueprint.route('/salt/<salt_id>', methods=['DELETE'])
@login_required
def delete_yubikey_salt(salt_id):
    """
    Delete a specific salt by its ID.
    
    Path parameters:
    - salt_id: The ID of the salt to delete
    
    Returns:
    {
        "success": true
    }
    """
    try:
        # Get salt by ID
        salt = YubiKeySalt.get_by_id(salt_id)
        
        if not salt:
            return jsonify({"success": False, "error": "Salt not found"}), 404
        
        # Delete the salt
        if not salt.delete():
            return jsonify({"success": False, "error": "Failed to delete salt"}), 500
        
        return jsonify({
            "success": True
        }), 200
        
    except Exception as e:
        logger.error(f"Error deleting YubiKey salt: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@yubikey_blueprint.route('/generate-salt', methods=['POST'])
@login_required
def generate_salt():
    """
    Generate a new random salt without associating it with a YubiKey.
    
    Returns:
    {
        "success": true,
        "salt": "hex_string"
    }
    """
    try:
        # Generate a random salt
        salt = os.urandom(32)  # 256 bits
        
        return jsonify({
            "success": True,
            "salt": salt.hex()
        }), 200
        
    except Exception as e:
        logger.error(f"Error generating salt: {str(e)}")
        return jsonify({"success": False, "error": "Internal server error"}), 500 
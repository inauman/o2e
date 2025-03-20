"""
YubiKey management API routes.
"""

from flask import Blueprint, request, jsonify, g
from models.yubikey import YubiKey
from models.user import User
import logging

# Create a blueprint for YubiKey routes
yubikey_bp = Blueprint('yubikey', __name__, url_prefix='/api/yubikey')

# Set up logging
logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require login for routes"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in g:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    
    return decorated_function


@yubikey_bp.route('/list', methods=['GET'])
@login_required
def list_yubikeys():
    """
    List all YubiKeys registered to the authenticated user.
    
    Returns:
        200: List of YubiKeys
        401: Authentication required
        500: Internal server error
    """
    try:
        yubikeys = YubiKey.get_yubikeys_by_user_id(g.user_id)
        
        return jsonify([{
            "credential_id": yk.credential_id,
            "nickname": yk.nickname,
            "is_primary": yk.is_primary,
            "created_at": yk.created_at.isoformat(),
            "last_used": yk.last_used.isoformat() if yk.last_used else None
        } for yk in yubikeys]), 200
        
    except Exception as e:
        logger.error(f"Error listing YubiKeys: {str(e)}")
        return jsonify({"error": str(e)}), 500


@yubikey_bp.route('/<credential_id>/set-primary', methods=['POST'])
@login_required
def set_primary_yubikey(credential_id: str):
    """
    Set a YubiKey as the primary key for the authenticated user.
    
    Args:
        credential_id: The ID of the credential to set as primary
    
    Returns:
        200: YubiKey set as primary
        401: Authentication required
        403: Not authorized to modify this YubiKey
        404: YubiKey not found
        500: Internal server error
    """
    try:
        yubikey = YubiKey.get_by_credential_id(credential_id)
        if not yubikey:
            return jsonify({"error": "YubiKey not found"}), 404
        
        if yubikey.user_id != g.user_id:
            return jsonify({"error": "Not authorized to modify this YubiKey"}), 403
        
        # Set as primary and update
        yubikey.is_primary = True
        if not yubikey.update():
            return jsonify({"error": "Failed to update YubiKey"}), 500
        
        return jsonify({
            "credential_id": yubikey.credential_id,
            "is_primary": True
        }), 200
        
    except Exception as e:
        logger.error(f"Error setting primary YubiKey: {str(e)}")
        return jsonify({"error": str(e)}), 500


@yubikey_bp.route('/<credential_id>/update', methods=['PATCH'])
@login_required
def update_yubikey(credential_id: str):
    """
    Update a YubiKey's nickname.
    
    Args:
        credential_id: The ID of the credential to update
    
    Request body:
    {
        "nickname": "string"
    }
    
    Returns:
        200: YubiKey updated
        400: Invalid request
        401: Authentication required
        403: Not authorized to modify this YubiKey
        404: YubiKey not found
        500: Internal server error
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.json
        nickname = data.get('nickname')
        
        if not nickname:
            return jsonify({"error": "Nickname is required"}), 400
        
        yubikey = YubiKey.get_by_credential_id(credential_id)
        if not yubikey:
            return jsonify({"error": "YubiKey not found"}), 404
        
        if yubikey.user_id != g.user_id:
            return jsonify({"error": "Not authorized to modify this YubiKey"}), 403
        
        # Update nickname
        yubikey.nickname = nickname
        if not yubikey.update():
            return jsonify({"error": "Failed to update YubiKey"}), 500
        
        return jsonify({
            "credential_id": yubikey.credential_id,
            "nickname": yubikey.nickname
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating YubiKey: {str(e)}")
        return jsonify({"error": str(e)}), 500


@yubikey_bp.route('/<credential_id>', methods=['DELETE'])
@login_required
def delete_yubikey(credential_id: str):
    """
    Delete a YubiKey registration.
    
    Args:
        credential_id: The ID of the credential to delete
    
    Returns:
        200: YubiKey deleted
        401: Authentication required
        403: Not authorized to delete this YubiKey
        404: YubiKey not found
        409: Cannot delete the only YubiKey
        500: Internal server error
    """
    try:
        yubikey = YubiKey.get_by_credential_id(credential_id)
        if not yubikey:
            return jsonify({"error": "YubiKey not found"}), 404
        
        if yubikey.user_id != g.user_id:
            return jsonify({"error": "Not authorized to delete this YubiKey"}), 403
        
        # Attempt to delete
        if not yubikey.delete():
            return jsonify({"error": "Cannot delete the only YubiKey"}), 409
        
        return jsonify({"message": "YubiKey deleted successfully"}), 200
        
    except Exception as e:
        logger.error(f"Error deleting YubiKey: {str(e)}")
        return jsonify({"error": str(e)}), 500 
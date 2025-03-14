"""
API routes for seed operations.
"""
from flask import Blueprint, request, jsonify, g
import base64
import json

from models.seed import Seed
from services.auth_service import login_required
from services.crypto_service import encrypt_seed, decrypt_seed
from utils.validation import validate_request

# Blueprint for seed routes
seed_blueprint = Blueprint('seed_api', __name__)


@seed_blueprint.route('/seeds', methods=['POST'])
@login_required
def create_seed():
    """
    Create a new seed for the authenticated user.
    
    Request body:
    {
        "seed_phrase": "string",  # The seed phrase to encrypt and store
        "metadata": {             # Optional metadata about the seed
            "label": "string",
            "type": "string",
            "tags": ["string"]
        }
    }
    
    Returns:
        201: Created seed
        400: Invalid request
        401: Unauthorized
        500: Internal server error
    """
    # Validate request
    schema = {
        "type": "object",
        "required": ["seed_phrase"],
        "properties": {
            "seed_phrase": {"type": "string", "minLength": 1},
            "metadata": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "type": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }
    
    valid, errors = validate_request(request, schema)
    if not valid:
        return jsonify({"error": "Invalid request", "details": errors}), 400
    
    # Get request data
    data = request.json
    seed_phrase = data["seed_phrase"]
    metadata = data.get("metadata", {})
    
    # Get authenticated user from context
    user_id = g.user.user_id
    
    try:
        # Encrypt the seed phrase
        encrypted_seed = encrypt_seed(seed_phrase)
        
        # Create the seed in the database
        seed = Seed.create(
            user_id=user_id,
            encrypted_seed=encrypted_seed,
            metadata=metadata
        )
        
        if seed is None:
            return jsonify({"error": "Failed to create seed"}), 500
        
        # Return the created seed
        return jsonify(seed.to_dict()), 201
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@seed_blueprint.route('/seeds', methods=['GET'])
@login_required
def get_seeds():
    """
    Get all seeds for the authenticated user.
    
    Returns:
        200: List of seeds
        401: Unauthorized
        500: Internal server error
    """
    # Get authenticated user from context
    user_id = g.user.user_id
    
    try:
        # Get all seeds for the user
        seeds = Seed.get_by_user_id(user_id)
        
        # Convert seeds to dictionaries
        seeds_dict = [seed.to_dict() for seed in seeds]
        
        return jsonify(seeds_dict), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@seed_blueprint.route('/seeds/<seed_id>', methods=['GET'])
@login_required
def get_seed(seed_id):
    """
    Get a specific seed by ID for the authenticated user.
    
    Args:
        seed_id: The ID of the seed to get
    
    Returns:
        200: Seed data
        401: Unauthorized
        403: Forbidden (not owner)
        404: Seed not found
        500: Internal server error
    """
    # Get authenticated user from context
    user_id = g.user.user_id
    
    try:
        # Get the seed
        seed = Seed.get_by_id(seed_id)
        
        if seed is None:
            return jsonify({"error": "Seed not found"}), 404
        
        # Check if user is authorized to access this seed
        if seed.user_id != user_id:
            return jsonify({"error": "You are not authorized to access this seed"}), 403
        
        # Update last accessed time
        seed.update_last_accessed()
        
        return jsonify(seed.to_dict()), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@seed_blueprint.route('/seeds/<seed_id>/decrypt', methods=['POST'])
@login_required
def decrypt_seed_data(seed_id):
    """
    Decrypt a specific seed by ID for the authenticated user.
    
    Args:
        seed_id: The ID of the seed to decrypt
    
    Returns:
        200: Decrypted seed phrase
        401: Unauthorized
        403: Forbidden (not owner)
        404: Seed not found
        500: Internal server error
    """
    # Get authenticated user from context
    user_id = g.user.user_id
    
    try:
        # Get the seed
        seed = Seed.get_by_id(seed_id)
        
        if seed is None:
            return jsonify({"error": "Seed not found"}), 404
        
        # Check if user is authorized to access this seed
        if seed.user_id != user_id:
            return jsonify({"error": "You are not authorized to access this seed"}), 403
        
        # Decrypt the seed
        decrypted_seed = decrypt_seed(seed.encrypted_seed)
        
        # Update last accessed time
        seed.update_last_accessed()
        
        return jsonify({"seed_phrase": decrypted_seed}), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@seed_blueprint.route('/seeds/<seed_id>', methods=['PUT'])
@login_required
def update_seed(seed_id):
    """
    Update a specific seed by ID for the authenticated user.
    
    Args:
        seed_id: The ID of the seed to update
    
    Request body:
    {
        "seed_phrase": "string",  # Optional new seed phrase
        "metadata": {             # Optional new metadata
            "label": "string",
            "type": "string",
            "tags": ["string"]
        }
    }
    
    Returns:
        200: Updated seed
        400: Invalid request
        401: Unauthorized
        403: Forbidden (not owner)
        404: Seed not found
        500: Internal server error
    """
    # Validate request
    schema = {
        "type": "object",
        "properties": {
            "seed_phrase": {"type": "string", "minLength": 1},
            "metadata": {
                "type": "object",
                "properties": {
                    "label": {"type": "string"},
                    "type": {"type": "string"},
                    "tags": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }
    
    valid, errors = validate_request(request, schema)
    if not valid:
        return jsonify({"error": "Invalid request", "details": errors}), 400
    
    # Get request data
    data = request.json
    
    # Get authenticated user from context
    user_id = g.user.user_id
    
    try:
        # Get the seed
        seed = Seed.get_by_id(seed_id)
        
        if seed is None:
            return jsonify({"error": "Seed not found"}), 404
        
        # Check if user is authorized to access this seed
        if seed.user_id != user_id:
            return jsonify({"error": "You are not authorized to access this seed"}), 403
        
        # Update seed phrase if provided
        if "seed_phrase" in data:
            encrypted_seed = encrypt_seed(data["seed_phrase"])
            seed.encrypted_seed = encrypted_seed
        
        # Update metadata if provided
        if "metadata" in data:
            seed.update_metadata(data["metadata"])
        
        # Update the seed in the database
        if not seed.update():
            return jsonify({"error": "Failed to update seed"}), 500
        
        return jsonify(seed.to_dict()), 200
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@seed_blueprint.route('/seeds/<seed_id>', methods=['DELETE'])
@login_required
def delete_seed(seed_id):
    """
    Delete a specific seed by ID for the authenticated user.
    
    Args:
        seed_id: The ID of the seed to delete
    
    Returns:
        204: No content (success)
        401: Unauthorized
        403: Forbidden (not owner)
        404: Seed not found
        500: Internal server error
    """
    # Get authenticated user from context
    user_id = g.user.user_id
    
    try:
        # Get the seed
        seed = Seed.get_by_id(seed_id)
        
        if seed is None:
            return jsonify({"error": "Seed not found"}), 404
        
        # Check if user is authorized to access this seed
        if seed.user_id != user_id:
            return jsonify({"error": "You are not authorized to delete this seed"}), 403
        
        # Delete the seed
        if not seed.delete():
            return jsonify({"error": "Failed to delete seed"}), 500
        
        return "", 204
    
    except Exception as e:
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500 
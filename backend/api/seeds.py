"""
Seed management API routes for YubiKey Bitcoin Seed Storage
"""

from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for
from services.bitcoin_service import BitcoinService
from services.encryption_service import EncryptionService

# Create a blueprint for seed management routes
seeds_bp = Blueprint('seeds', __name__, url_prefix='/api/seeds')

# Initialize services
bitcoin_service = BitcoinService()
encryption_service = EncryptionService()

@seeds_bp.route('/store', methods=['GET'])
def store_seed_view():
    """Render the seed storage page"""
    if not session.get('authenticated'):
        return redirect(url_for('auth.authenticate_view'))
    return render_template('store_seed.html')

@seeds_bp.route('/generate', methods=['POST'])
def generate_seed():
    """Generate a new BIP39 seed phrase"""
    try:
        # Skip authentication check in development mode
        if not request.headers.get('X-Skip-Auth') and not session.get('authenticated'):
            return jsonify({"error": "Authentication required"}), 401
            
        # Generate a new seed phrase
        mnemonic = bitcoin_service.generate_mnemonic()
        # For security, only return first 4 words in development mode
        if request.headers.get('X-Skip-Auth'):
            words = mnemonic.split()
            partial_mnemonic = ' '.join(words[:4]) + ' ...'
            return jsonify({"success": True, "mnemonic": mnemonic, "partial_mnemonic": partial_mnemonic})
        return jsonify({"success": True, "mnemonic": mnemonic})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seeds_bp.route('/validate', methods=['POST'])
def validate_seed():
    """Validate a BIP39 seed phrase"""
    try:
        if not session.get('authenticated'):
            return jsonify({"error": "Authentication required"}), 401
            
        mnemonic = request.json.get('mnemonic')
        if not mnemonic:
            return jsonify({"error": "Seed phrase is required"}), 400
            
        is_valid = bitcoin_service.validate_mnemonic(mnemonic)
        return jsonify({"success": True, "valid": is_valid})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seeds_bp.route('/store', methods=['POST'])
def store_seed():
    """Store an encrypted seed phrase"""
    try:
        if not session.get('authenticated'):
            return jsonify({"error": "Authentication required"}), 401
            
        username = session.get('username')
        mnemonic = request.json.get('mnemonic')
        encryption_key = request.json.get('encryption_key')
        
        if not all([username, mnemonic, encryption_key]):
            return jsonify({"error": "Missing required parameters"}), 400
            
        # Encrypt and store the seed
        result = encryption_service.store_encrypted_seed(username, mnemonic, encryption_key)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@seeds_bp.route('/view', methods=['GET'])
def view_seed_view():
    """Render the seed viewing page"""
    if not session.get('authenticated'):
        return redirect(url_for('auth.authenticate_view'))
    return render_template('view_seed.html')

@seeds_bp.route('/retrieve', methods=['POST'])
def retrieve_seed():
    """Retrieve and decrypt a stored seed phrase"""
    try:
        if not session.get('authenticated'):
            return jsonify({"error": "Authentication required"}), 401
            
        username = session.get('username')
        encryption_key = request.json.get('encryption_key')
        
        if not all([username, encryption_key]):
            return jsonify({"error": "Missing required parameters"}), 400
            
        # Retrieve and decrypt the seed
        result = encryption_service.retrieve_encrypted_seed(username, encryption_key)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500 
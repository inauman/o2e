#!/usr/bin/env python3
"""
Main application for YubiKey Bitcoin Seed Storage POC.
"""

import os
import json
import yaml
import base64
import binascii
import time
import threading
import argparse
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from flask_cors import CORS
from utils.bitcoin_utils import BitcoinSeedManager
from utils.security import WebAuthnManager
from api.auth import auth_bp
from api.seeds import seeds_bp
from routes.seed_routes import seed_blueprint
from routes.yubikey_routes import yubikey_blueprint
from services.bitcoin_service import BitcoinService
from services.webauthn_service import WebAuthnService
from services.secure_memory_service import SecureMemoryManager
from models.database import DatabaseManager

def load_config(config_name: str = 'default') -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Args:
        config_name: The name of the configuration to load ('default', 'testing', etc.)
        
    Returns:
        Dictionary containing configuration values
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    # Override settings for testing
    if config_name == 'testing':
        config['data']['database']['path'] = ':memory:'  # Use in-memory database for testing
        config['flask']['testing'] = True
        
    # For backward compatibility, add database section
    config['database'] = config['data']['database']
        
    return config

def create_app(config_name: str = 'default') -> Flask:
    """
    Create and configure the Flask application
    
    Args:
        config_name: The name of the configuration to use ('default', 'testing', etc.)
        
    Returns:
        The configured Flask application
    """
    # Initialize Flask application
    app = Flask(__name__)
    
    # Enable CORS for all routes and origins
    CORS(app, supports_credentials=True)
    
    # Load configuration
    config = load_config(config_name)
    
    # Set secret key for sessions
    app.secret_key = config.get('flask', {}).get('secret_key', os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production'))
    
    # Update all configuration sections
    for section in config:
        app.config[section] = config[section]
    
    # Initialize database
    db_path = ':memory:' if config_name == 'testing' else config['data']['database']['path']
    db = DatabaseManager(db_path)
    db.initialize_schema()
    
    # Initialize services
    bitcoin_service = BitcoinService(
        strength=config['bitcoin']['seed_strength']
    )
    webauthn_service = WebAuthnService()
    secure_memory = SecureMemoryManager(timeout=config['security']['memory_timeout'])
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(seeds_bp)
    app.register_blueprint(seed_blueprint, url_prefix='/api/v1')
    app.register_blueprint(yubikey_blueprint)
    
    # Define routes
    @app.route('/')
    def index():
        """Render the index page"""
        return render_template('index.html')
    
    @app.route('/test_yubikey')
    def test_yubikey():
        """Render the YubiKey test page"""
        return render_template('test_yubikey.html')
    
    @app.route('/resident_keys')
    def resident_keys():
        """Render the resident keys page"""
        return render_template('resident_keys.html')
    
    @app.route('/delete_credential')
    def delete_credential():
        """Render the delete credential page"""
        return render_template('delete_credential.html')
    
    @app.errorhandler(404)
    def page_not_found(e):
        """Handle 404 errors"""
        return render_template('error.html', error="Page not found"), 404
    
    @app.errorhandler(500)
    def server_error(e):
        """Handle 500 errors"""
        return render_template('error.html', error="Server error"), 500
    
    # Serve React app in production
    @app.route('/<path:path>')
    def serve_react(path):
        """Serve static files from the React app"""
        if path != "" and os.path.exists(os.path.join('static', path)):
            return send_from_directory('static', path)
        return send_from_directory('static', 'index.html')
    
    # Make services available to blueprints
    app.bitcoin_service = bitcoin_service
    app.webauthn_service = webauthn_service
    app.secure_memory = secure_memory
    
    return app

# Create the default application instance
app = create_app()

# Initialize managers
bitcoin_manager = BitcoinSeedManager(
    strength=app.config['bitcoin']['seed_strength']
)
webauthn_manager = WebAuthnManager()

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='YubiKey Bitcoin Seed Storage Backend')
    parser.add_argument('--port', type=int, default=app.config['flask'].get('port', 5000),
                        help='Port to run the server on (default: 5000)')
    parser.add_argument('--host', type=str, default=app.config['flask'].get('host', '127.0.0.1'),
                        help='Host to run the server on (default: 127.0.0.1)')
    args = parser.parse_args()
    
    # Update the port in the WebAuthn config as well if it changed
    if args.port != 5000:
        print(f"Running on non-default port {args.port}. Updating WebAuthn origin.")
        app.config['webauthn']['origin'] = f"https://localhost:{args.port}"
    
    app.run(
        host=args.host,
        port=args.port,
        debug=app.config['flask'].get('debug', False)
    ) 
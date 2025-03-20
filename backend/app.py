#!/usr/bin/env python3
"""
Main application for YubiKey Bitcoin Seed Storage POC.
"""

import os
import argparse
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, g
from flask_cors import CORS
from utils.security import WebAuthnManager
from routes.yubikey_routes import yubikey_blueprint
from routes.auth import auth_blueprint
from routes.user_routes import user_blueprint
from services.webauthn_service import WebAuthnService
from services.secure_memory_service import SecureMemoryManager
from models.database import DatabaseManager
from config import DevelopmentConfig, TestConfig, ProductionConfig
import logging


def create_app(config_object=None):
    """
    Create and configure the Flask application
    
    Args:
        config_object: Configuration object to use (defaults to DevelopmentConfig)
        
    Returns:
        The configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_object is None:
        config_object = DevelopmentConfig
    app.config.from_object(config_object)
    
    # Enable CORS
    CORS(app, supports_credentials=True)
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize database
    init_database(app)
    
    # Initialize WebAuthn
    init_webauthn(app)
    
    # Initialize services
    init_services(app)
    
    # Register blueprints
    app.register_blueprint(yubikey_blueprint, url_prefix='/api/yubikey')
    app.register_blueprint(auth_blueprint, url_prefix='/api/auth')
    app.register_blueprint(user_blueprint, url_prefix='/api/user')
    
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
    
    @app.route('/delete-credential')
    def delete_credential_view():
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
    
    @app.before_request
    def load_user():
        """Load user from session into request context."""
        g.user_id = session.get('user_id')
    
    @app.after_request
    def add_security_headers(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response
    
    return app


def init_database(app):
    """Initialize the database.
    
    Args:
        app: The Flask application
    """
    db_path = app.config['DATABASE_PATH']
    db_manager = DatabaseManager(db_path)
    db_manager.initialize_schema()
    print("✓ Database schema initialized successfully")


def init_webauthn(app):
    """Initialize the WebAuthn manager.
    
    Args:
        app: The Flask application
    """
    print(f"Initializing WebAuthnManager with rp_id: {app.config['WEBAUTHN_RP_ID']}, "
          f"rp_name: {app.config['WEBAUTHN_RP_NAME']}")
    print(f"WebAuthn origin: {app.config['WEBAUTHN_ORIGIN']}")
    
    WebAuthnManager(
        rp_id=app.config['WEBAUTHN_RP_ID'],
        rp_name=app.config['WEBAUTHN_RP_NAME'],
        rp_origin=app.config['WEBAUTHN_ORIGIN']
    )


def init_services(app):
    """Initialize application services.
    
    Args:
        app: The Flask application
    """
    # Initialize WebAuthn service
    webauthn_service = WebAuthnService()
    
    # Initialize secure memory service
    secure_memory = SecureMemoryManager(timeout=300)  # 5-minute timeout default
    
    # Make services available to blueprints
    app.webauthn_service = webauthn_service
    app.secure_memory = secure_memory


# Create the default application instance
app = create_app()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=5001, help="Port to run the server on")
    args = parser.parse_args()

    print(f"Starting server with WebAuthn settings:")
    print(f"RP ID: {app.config['WEBAUTHN_RP_ID']}")
    print(f"Origin: {app.config['WEBAUTHN_ORIGIN']}")

    # Always use localhost and HTTPS for WebAuthn compatibility
    app.run(
        host="localhost",
        port=args.port,
        debug=True,
        ssl_context='adhoc'  # Use adhoc SSL certificates for development
    ) 
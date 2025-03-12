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
from typing import Dict, Any, Optional
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory
from bitcoin_utils import BitcoinSeedManager
from yubikey_utils import WebAuthnManager
from api.auth import auth_bp
from api.seeds import seeds_bp

# Load configuration
def load_config() -> Dict[str, Any]:
    """
    Load configuration from YAML file
    
    Returns:
        Dictionary containing configuration values
    """
    config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

config = load_config()

# Initialize Flask application
app = Flask(__name__)
app.secret_key = config["app"]["secret_key"]

# Initialize managers
bitcoin_manager = BitcoinSeedManager(
    strength=config["bitcoin"]["seed_strength"]
)
webauthn_manager = WebAuthnManager()

# Ensure data directory exists
os.makedirs(config["storage"]["data_dir"], exist_ok=True)
encrypted_seeds_file = config["storage"]["encrypted_seeds_file"]

# Initialize the encrypted seeds file if it doesn't exist
if not os.path.exists(encrypted_seeds_file):
    with open(encrypted_seeds_file, "w") as f:
        json.dump({}, f)

# Secure memory handling
class SecureMemoryManager:
    """
    Manages secure storage of sensitive data in memory with auto-clearing.
    """
    
    def __init__(self, timeout: int = 60):
        """
        Initialize the secure memory manager.
        
        Args:
            timeout: Number of seconds before auto-clearing (default: 60)
        """
        self.timeout = timeout
        self._storage = {}
        self._timers = {}
        self._lock = threading.Lock()
    
    def store(self, key: str, value: str) -> None:
        """
        Store a value securely with auto-clearing after timeout.
        
        Args:
            key: The key to store the value under
            value: The value to store
        """
        with self._lock:
            # Cancel any existing timer
            if key in self._timers and self._timers[key] is not None:
                self._timers[key].cancel()
            
            # Store the value
            self._storage[key] = value
            
            # Set a timer to clear the value
            self._timers[key] = threading.Timer(self.timeout, self.clear, args=[key])
            self._timers[key].daemon = True
            self._timers[key].start()
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a stored value.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        with self._lock:
            return self._storage.get(key)
    
    def clear(self, key: str = None) -> None:
        """
        Clear stored values.
        
        Args:
            key: The specific key to clear, or None to clear all
        """
        with self._lock:
            if key is not None:
                if key in self._storage:
                    del self._storage[key]
                if key in self._timers:
                    if self._timers[key] is not None:
                        self._timers[key].cancel()
                    del self._timers[key]
            else:
                # Clear all values
                for timer_key in list(self._timers.keys()):
                    if self._timers[timer_key] is not None:
                        self._timers[timer_key].cancel()
                self._storage.clear()
                self._timers.clear()
    
    def extend_timeout(self, key: str) -> bool:
        """
        Extend the timeout for a stored value.
        
        Args:
            key: The key to extend timeout for
            
        Returns:
            True if the timeout was extended, False if the key was not found
        """
        with self._lock:
            if key not in self._storage:
                return False
            
            # Get the current value
            value = self._storage[key]
            
            # Store it again (which resets the timer)
            self.store(key, value)
            
            return True

# Initialize secure memory manager
secure_memory = SecureMemoryManager(timeout=config["security"]["memory_timeout"])

# Create Flask application
def create_app() -> Flask:
    """
    Create and configure the Flask application
    
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    config = load_config()
    
    # Configure Flask
    app.secret_key = config['flask']['secret_key']
    app.config['SESSION_TYPE'] = 'filesystem'
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(seeds_bp)
    
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
    
    return app

# Run the application
if __name__ == '__main__':
    app = create_app()
    config = load_config()
    
    # Run with SSL in development
    app.run(
        host=config['flask']['host'],
        port=config['flask']['port'],
        ssl_context=(
            config['flask']['ssl_cert'],
            config['flask']['ssl_key']
        ),
        debug=config['flask']['debug']
    ) 
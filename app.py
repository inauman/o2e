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
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from bitcoin_utils import BitcoinSeedManager
from yubikey_utils import WebAuthnManager

# Load configuration
def load_config() -> Dict[str, Any]:
    """
    Load configuration from the YAML file.
    
    Returns:
        Dictionary containing the configuration
    """
    with open("config.yaml", "r") as file:
        return yaml.safe_load(file)

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

@app.route("/")
def index():
    """
    Main page of the application.
    """
    return render_template("index.html")

@app.route("/generate-seed", methods=["POST"])
def generate_seed():
    """
    Generate a new Bitcoin seed phrase.
    """
    # Get entropy bits from request or use default
    entropy_bits = request.json.get("entropy_bits", config["bitcoin"]["seed_strength"])
    
    # Create a temporary manager with the requested strength
    temp_manager = BitcoinSeedManager(strength=int(entropy_bits))
    
    # Generate a new mnemonic and seed
    mnemonic, seed = temp_manager.generate_seed()
    
    # Store in secure memory instead of session
    seed_id = binascii.hexlify(os.urandom(16)).decode()
    secure_memory.store(f"seed:{seed_id}", mnemonic)
    
    # Store in session just the reference
    session["seed_id"] = seed_id
    
    # Return partial mnemonic for display
    # In a real app, you might not want to display the full mnemonic in the browser
    words = mnemonic.split()
    word_count = len(words)
    first_words = " ".join(words[:3])
    last_words = " ".join(words[-2:])
    
    return jsonify({
        "success": True,
        "partial_mnemonic": f"{first_words}...{last_words}",
        "word_count": word_count,
        "entropy_bits": entropy_bits
    })

@app.route("/validate-seed", methods=["POST"])
def validate_seed():
    """
    Validate a user-provided seed phrase.
    """
    seed_phrase = request.json.get("seed_phrase", "")
    
    if not seed_phrase:
        return jsonify({
            "valid": False,
            "message": "Seed phrase is required"
        }), 400
    
    # Validate the seed phrase
    is_valid = bitcoin_manager.validate_mnemonic(seed_phrase)
    
    if is_valid:
        # Store in secure memory
        seed_id = binascii.hexlify(os.urandom(16)).decode()
        secure_memory.store(f"seed:{seed_id}", seed_phrase)
        
        # Store reference in session
        session["seed_id"] = seed_id
        
        # Get entropy bits
        word_count = len(seed_phrase.split())
        entropy_bits = None
        if word_count == 12:
            entropy_bits = 128
        elif word_count == 15:
            entropy_bits = 160
        elif word_count == 18:
            entropy_bits = 192
        elif word_count == 21:
            entropy_bits = 224
        elif word_count == 24:
            entropy_bits = 256
        
        return jsonify({
            "valid": True,
            "message": "Seed phrase is valid",
            "word_count": word_count,
            "entropy_bits": entropy_bits
        })
    else:
        return jsonify({
            "valid": False,
            "message": "Invalid seed phrase. Please check for typos or use a valid BIP39 mnemonic."
        })

@app.route("/register", methods=["GET"])
def register_page():
    """
    Display the registration page.
    """
    # Check if a seed has been generated
    if "seed_id" not in session:
        return redirect(url_for("index"))
    
    return render_template("register.html")

@app.route("/begin-registration", methods=["POST"])
def begin_registration():
    """
    Begin the WebAuthn registration process.
    """
    username = request.json.get("username", "user")
    
    # Generate registration options
    registration_data = webauthn_manager.generate_registration_options_for_user(username)
    
    # Store user_id in session
    session["user_id"] = registration_data["user_id"]
    
    return jsonify(registration_data["options"])

@app.route("/complete-registration", methods=["POST"])
def complete_registration():
    """
    Complete the WebAuthn registration process.
    """
    if "user_id" not in session:
        return jsonify({"success": False, "error": "No registration in progress"}), 400
    
    user_id = session["user_id"]
    
    try:
        # Verify the registration response
        verification = webauthn_manager.verify_registration_response(user_id, request.json)
        
        # If we have a seed in secure memory, encrypt and store it
        if "seed_id" in session:
            seed_id = session["seed_id"]
            mnemonic = secure_memory.get(f"seed:{seed_id}")
            
            if mnemonic:
                store_encrypted_seed(user_id, mnemonic)
                secure_memory.clear(f"seed:{seed_id}")
                session.pop("seed_id")
        
        return jsonify({"success": True, "user_id": user_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

def store_encrypted_seed(user_id: str, mnemonic: str) -> None:
    """
    Store an encrypted seed for a user.
    
    In a real application, this would use proper encryption derived from the WebAuthn credential.
    For this POC, we'll use a simplified approach.
    
    Args:
        user_id: The user ID
        mnemonic: The mnemonic phrase to encrypt and store
    """
    # In a real application, the encryption key would be derived from the WebAuthn credential
    # or another secure source. For this POC, we'll use a placeholder approach.
    
    # Load existing encrypted seeds
    with open(encrypted_seeds_file, "r") as f:
        encrypted_seeds = json.load(f)
    
    # Calculate entropy bits
    word_count = len(mnemonic.split())
    entropy_bits = None
    if word_count == 12:
        entropy_bits = 128
    elif word_count == 15:
        entropy_bits = 160
    elif word_count == 18:
        entropy_bits = 192
    elif word_count == 21:
        entropy_bits = 224
    elif word_count == 24:
        entropy_bits = 256
    
    # Store the "encrypted" seed (in a real application, this would be properly encrypted)
    # For the POC, we'll just encode it as base64
    encrypted_seeds[user_id] = {
        "encrypted_seed": base64.b64encode(mnemonic.encode()).decode(),
        "created_at": import_time(),
        "word_count": word_count,
        "entropy_bits": entropy_bits,
        "last_retrieved": None
    }
    
    # Save the encrypted seeds
    with open(encrypted_seeds_file, "w") as f:
        json.dump(encrypted_seeds, f)

def import_time() -> str:
    """
    Get the current time as a string.
    
    Returns:
        Current time as ISO format string
    """
    from datetime import datetime
    return datetime.now().isoformat()

@app.route("/authenticate", methods=["GET"])
def authenticate_page():
    """
    Display the authentication page.
    """
    return render_template("authenticate.html")

@app.route("/begin-authentication", methods=["POST"])
def begin_authentication():
    """
    Begin the WebAuthn authentication process.
    """
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"success": False, "error": "User ID is required"}), 400
    
    try:
        # Generate authentication options
        options = webauthn_manager.generate_authentication_options(user_id)
        
        # Store user_id in session
        session["auth_user_id"] = user_id
        
        return jsonify(options)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route("/complete-authentication", methods=["POST"])
def complete_authentication():
    """
    Complete the WebAuthn authentication process.
    """
    if "auth_user_id" not in session:
        return jsonify({"success": False, "error": "No authentication in progress"}), 400
    
    user_id = session["auth_user_id"]
    
    try:
        # Verify the authentication response
        verification = webauthn_manager.verify_authentication_response(user_id, request.json)
        
        # If successful, retrieve the encrypted seed
        has_seed = check_user_has_seed(user_id)
        
        # Store temporarily in session for the seed display page
        session["authenticated_user_id"] = user_id
        
        return jsonify({
            "success": True,
            "message": "Authentication successful",
            "has_seed": has_seed
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

def check_user_has_seed(user_id: str) -> bool:
    """
    Check if a user has a stored seed.
    
    Args:
        user_id: The user ID
        
    Returns:
        True if the user has a stored seed, False otherwise
    """
    # Load existing encrypted seeds
    with open(encrypted_seeds_file, "r") as f:
        encrypted_seeds = json.load(f)
    
    return user_id in encrypted_seeds

def retrieve_encrypted_seed(user_id: str) -> Optional[str]:
    """
    Retrieve and decrypt a stored seed for a user.
    
    In a real application, this would use proper decryption with a key derived
    from the WebAuthn credential. For this POC, we'll use a simplified approach.
    
    Args:
        user_id: The user ID
        
    Returns:
        The decrypted mnemonic phrase, or None if not found
    """
    # Load existing encrypted seeds
    with open(encrypted_seeds_file, "r") as f:
        encrypted_seeds = json.load(f)
    
    if user_id not in encrypted_seeds:
        return None
    
    # Retrieve and "decrypt" the seed (in a real application, this would be properly decrypted)
    encrypted_seed = encrypted_seeds[user_id]["encrypted_seed"]
    mnemonic = base64.b64decode(encrypted_seed).decode()
    
    # Update last retrieved time
    encrypted_seeds[user_id]["last_retrieved"] = import_time()
    
    # Save the updated encrypted seeds
    with open(encrypted_seeds_file, "w") as f:
        json.dump(encrypted_seeds, f)
    
    return mnemonic

@app.route("/view-seed")
def view_seed():
    """
    Display the retrieved seed.
    """
    if "authenticated_user_id" not in session:
        return redirect(url_for("authenticate_page"))
    
    user_id = session["authenticated_user_id"]
    mnemonic = retrieve_encrypted_seed(user_id)
    
    if not mnemonic:
        return render_template("error.html", message="No seed found for your YubiKey.")
    
    # Store in secure memory for a short time
    seed_view_id = binascii.hexlify(os.urandom(16)).decode()
    secure_memory.store(f"view:{seed_view_id}", mnemonic)
    session["seed_view_id"] = seed_view_id
    
    # Load metadata
    with open(encrypted_seeds_file, "r") as f:
        encrypted_seeds = json.load(f)
    
    entropy_bits = encrypted_seeds[user_id].get("entropy_bits")
    last_retrieved = encrypted_seeds[user_id].get("last_retrieved")
    
    # Pass the seed to the template
    return render_template(
        "view_seed.html", 
        seed_phrase=mnemonic.split(),
        entropy_bits=entropy_bits,
        last_retrieved=last_retrieved
    )

@app.route("/store-seed", methods=["POST"])
def store_seed():
    """
    Store a seed phrase.
    """
    if "authenticated_user_id" not in session:
        return jsonify({"success": False, "error": "Authentication required"}), 401
    
    user_id = session["authenticated_user_id"]
    seed_phrase = request.json.get("seed_phrase", "")
    
    if not seed_phrase:
        return jsonify({"success": False, "error": "Seed phrase is required"}), 400
    
    # Validate the seed phrase
    is_valid = bitcoin_manager.validate_mnemonic(seed_phrase)
    
    if not is_valid:
        return jsonify({
            "success": False,
            "error": "Invalid seed phrase. Please check for typos or use a valid BIP39 mnemonic."
        }), 400
    
    # Store the seed
    store_encrypted_seed(user_id, seed_phrase)
    
    return jsonify({"success": True})

@app.route("/logout")
def logout():
    """
    End the session and clear any sensitive data.
    """
    # Clear any secure memory entries
    if "seed_id" in session:
        secure_memory.clear(f"seed:{session['seed_id']}")
    
    if "seed_view_id" in session:
        secure_memory.clear(f"view:{session['seed_view_id']}")
    
    # Clear session
    session.clear()
    
    return redirect(url_for("index"))

@app.route("/test-yubikey")
def test_yubikey():
    """
    Test if YubiKey is working.
    """
    return render_template("test_yubikey.html")

if __name__ == "__main__":
    # Run the Flask application with SSL for WebAuthn
    app.run(
        host=config["app"]["host"],
        port=config["app"]["port"],
        debug=config["app"]["debug"],
        ssl_context="adhoc"  # Generate a self-signed certificate for HTTPS
    ) 
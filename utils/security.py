"""
WebAuthn security utilities
"""

import base64
import json
import os
import secrets
import yaml
from typing import Dict, Any, Tuple, List, Optional

# Define our own load_config function instead of importing it
def load_config() -> Dict[str, Any]:
    """
    Load configuration from the YAML file.
    
    Returns:
        Dictionary containing the configuration
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), "..", "backend", "config.yaml")
        with open(config_path, "r") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print("Config file not found, using default values")
        return {
            "webauthn": {
                "rp_id": "localhost",
                "rp_name": "YubiKey Bitcoin Seed Storage",
            }
        }

class WebAuthnManager:
    def __init__(self, rp_id: str = None, rp_name: str = None):
        """
        Initialize WebAuthn manager
        
        Args:
            rp_id: Relying Party ID (defaults to config value)
            rp_name: Relying Party name (defaults to config value)
        """
        config = load_config()
        
        if rp_id is None:
            rp_id = config["webauthn"]["rp_id"]
            
        if rp_name is None:
            rp_name = config["webauthn"]["rp_name"]
            
        self.rp_id = rp_id
        self.rp_name = rp_name
        
        # For backward compatibility with tests
        # 'storage' section is now marked as legacy in config.yaml
        if "storage" in config and "credentials_file" in config["storage"]:
            self.credentials_file = config["storage"]["credentials_file"]
        else:
            # When using database approach, use a dummy path for compatibility with tests
            self.credentials_file = "data/credentials.json"

    def _ensure_storage_exists(self) -> None:
        """
        Legacy method kept for backward compatibility.
        No longer creates physical files as we now use the database.
        """
        # This is now a no-op since we're using the database
        # But kept for backward compatibility with tests
        return 

    def _store_challenge(self, user_id: str, challenge: str) -> None:
        """
        Store a challenge for later verification.
        
        Args:
            user_id: User ID (can be string or bytes)
            challenge: The base64-encoded challenge
        """
        try:
            # Ensure user_id is a string for storage
            if isinstance(user_id, bytes):
                user_id = user_id.decode('utf-8')
                
            print(f"Storing challenge for user ID: {user_id}", flush=True)
            
            # Ensure challenge is a string for storage
            if isinstance(challenge, bytes):
                challenge = base64.b64encode(challenge).decode('utf-8')
                print(f"Converted challenge from bytes to base64 string", flush=True)
            
            # Store challenge in the database
            from models.database import DatabaseManager
            db = DatabaseManager()
            
            # Store challenge in a temporary table
            db.execute_query(
                """
                CREATE TABLE IF NOT EXISTS webauthn_challenges (
                    user_id TEXT PRIMARY KEY,
                    challenge TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            
            # Insert or replace the challenge
            db.execute_query(
                """
                INSERT OR REPLACE INTO webauthn_challenges (user_id, challenge)
                VALUES (?, ?)
                """,
                (user_id, challenge)
            )
            
            print("Stored challenge in database", flush=True)
            
        except Exception as e:
            import traceback
            print(f"Error in _store_challenge: {str(e)}", flush=True)
            traceback.print_exc()
            raise 
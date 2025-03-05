#!/usr/bin/env python3
"""
YubiKey utilities for Bitcoin Seed Storage POC.
This module handles WebAuthn integration with YubiKey.
"""

import os
import json
import base64
import yaml
import uuid
from typing import Dict, Any, Optional, Tuple
from webauthn import (
    generate_registration_options,
    verify_registration_response,
    generate_authentication_options,
    verify_authentication_response,
)
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorSelectionCriteria,
    UserVerificationRequirement,
    ResidentKeyRequirement,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

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

class WebAuthnManager:
    """
    Manages WebAuthn operations for YubiKey integration.
    """
    
    def __init__(self, rp_id: str = None, rp_name: str = None):
        """
        Initialize the WebAuthn manager.
        
        Args:
            rp_id: The Relying Party ID (defaults to config value)
            rp_name: The Relying Party name (defaults to config value)
        """
        if rp_id is None:
            rp_id = config["webauthn"]["rp_id"]
        if rp_name is None:
            rp_name = config["webauthn"]["rp_name"]
            
        self.rp_id = rp_id
        self.rp_name = rp_name
        
        # Credentials storage
        self.credentials_file = config["storage"]["credentials_file"]
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """
        Ensure the storage directory and files exist.
        """
        os.makedirs(os.path.dirname(self.credentials_file), exist_ok=True)
        if not os.path.exists(self.credentials_file):
            with open(self.credentials_file, "w") as f:
                json.dump({}, f)
    
    def generate_registration_options_for_user(self, username: str) -> Dict[str, Any]:
        """
        Generate WebAuthn registration options for a user.
        
        Args:
            username: The username to register
            
        Returns:
            WebAuthn registration options
        """
        # Create a user ID
        user_id = str(uuid.uuid4())
        
        # Configure authenticator selection criteria based on config
        authenticator_selection = AuthenticatorSelectionCriteria(
            user_verification=UserVerificationRequirement(config["yubikey"]["user_verification"]),
            authenticator_attachment="cross-platform",  # YubiKey is cross-platform
            resident_key=ResidentKeyRequirement.DISCOURAGED,  # We don't need resident keys for this POC
        )
        
        # Generate registration options
        options = generate_registration_options(
            rp_id=self.rp_id,
            rp_name=self.rp_name,
            user_id=user_id,
            user_name=username,
            user_display_name=username,
            attestation=AttestationConveyancePreference.NONE,
            authenticator_selection=authenticator_selection,
            supported_pub_key_algs=[
                COSEAlgorithmIdentifier.ES256,  # ECDSA with P-256
            ],
            timeout=60000,  # 60 seconds
        )
        
        # Convert challenge to base64 for sending to browser
        options["challenge"] = base64.b64encode(options["challenge"]).decode("utf-8")
        
        # Store challenge in JSON file temporarily (in a real app, this would be in a database or session)
        self._store_challenge(user_id, options["challenge"])
        
        return {
            "options": options,
            "user_id": user_id
        }
    
    def _store_challenge(self, user_id: str, challenge: str) -> None:
        """
        Store a challenge for later verification.
        
        Args:
            user_id: User ID
            challenge: The base64-encoded challenge
        """
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        if "challenges" not in credentials:
            credentials["challenges"] = {}
        
        credentials["challenges"][user_id] = challenge
        
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)
    
    def _get_challenge(self, user_id: str) -> Optional[bytes]:
        """
        Get a stored challenge.
        
        Args:
            user_id: User ID
            
        Returns:
            The challenge as bytes, or None if not found
        """
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        if "challenges" not in credentials or user_id not in credentials["challenges"]:
            return None
        
        challenge = credentials["challenges"][user_id]
        return base64.b64decode(challenge)
    
    def verify_registration_response(self, user_id: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a WebAuthn registration response.
        
        Args:
            user_id: The user ID
            response: The WebAuthn response from the browser
            
        Returns:
            Verification result
        """
        # Get the stored challenge
        challenge = self._get_challenge(user_id)
        if not challenge:
            raise ValueError("Challenge not found for user")
        
        # Process response data for verification
        client_data = base64.b64decode(response["response"]["clientDataJSON"])
        att_obj = base64.b64decode(response["response"]["attestationObject"])
        
        # Verify the registration response
        verification = verify_registration_response(
            credential_id=base64.b64decode(response["rawId"]),
            credential_public_key=None,  # Will be extracted from attestation
            attestation_object=att_obj,
            client_data=client_data,
            expected_challenge=challenge,
            expected_rp_id=self.rp_id,
            expected_origin="https://localhost:5000",  # Should match your application origin
        )
        
        # Store the credential
        self._store_credential(user_id, verification)
        
        # Clean up the challenge
        self._remove_challenge(user_id)
        
        return {
            "verified": True,
            "credential_id": base64.b64encode(verification.credential_id).decode("utf-8")
        }
    
    def _store_credential(self, user_id: str, verification: Any) -> None:
        """
        Store a verified credential.
        
        Args:
            user_id: User ID
            verification: Verification result from verify_registration_response
        """
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        if "users" not in credentials:
            credentials["users"] = {}
        
        # Store the credential information
        credentials["users"][user_id] = {
            "credential_id": base64.b64encode(verification.credential_id).decode("utf-8"),
            "public_key": base64.b64encode(verification.credential_public_key).decode("utf-8"),
            "sign_count": verification.sign_count,
        }
        
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)
    
    def _remove_challenge(self, user_id: str) -> None:
        """
        Remove a stored challenge.
        
        Args:
            user_id: User ID
        """
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        if "challenges" in credentials and user_id in credentials["challenges"]:
            del credentials["challenges"][user_id]
        
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)
    
    def get_user_credential(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a user's credential.
        
        Args:
            user_id: User ID
            
        Returns:
            Credential information or None if not found
        """
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        if "users" not in credentials or user_id not in credentials["users"]:
            return None
        
        return credentials["users"][user_id]
    
    def generate_authentication_options(self, user_id: str) -> Dict[str, Any]:
        """
        Generate WebAuthn authentication options.
        
        Args:
            user_id: The user ID
            
        Returns:
            WebAuthn authentication options
        """
        # Get the user's credential
        credential = self.get_user_credential(user_id)
        if not credential:
            raise ValueError(f"No credential found for user {user_id}")
        
        # Generate authentication options
        options = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=[{
                "type": "public-key",
                "id": base64.b64decode(credential["credential_id"]),
            }],
            user_verification=UserVerificationRequirement(config["yubikey"]["user_verification"]),
            timeout=60000,  # 60 seconds
        )
        
        # Convert challenge to base64 for sending to browser
        options["challenge"] = base64.b64encode(options["challenge"]).decode("utf-8")
        
        # Store the challenge
        self._store_challenge(user_id, options["challenge"])
        
        return options
    
    def verify_authentication_response(self, user_id: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a WebAuthn authentication response.
        
        Args:
            user_id: The user ID
            response: The WebAuthn response from the browser
            
        Returns:
            Verification result
        """
        # Get the stored credential
        credential = self.get_user_credential(user_id)
        if not credential:
            raise ValueError(f"No credential found for user {user_id}")
        
        # Get the stored challenge
        challenge = self._get_challenge(user_id)
        if not challenge:
            raise ValueError("Challenge not found for user")
        
        # Decode response data
        credential_id = base64.b64decode(response["rawId"])
        client_data = base64.b64decode(response["response"]["clientDataJSON"])
        auth_data = base64.b64decode(response["response"]["authenticatorData"])
        signature = base64.b64decode(response["response"]["signature"])
        
        # Verify the authentication response
        verification = verify_authentication_response(
            credential_id=credential_id,
            credential_public_key=base64.b64decode(credential["public_key"]),
            authenticator_data=auth_data,
            client_data=client_data,
            signature=signature,
            expected_challenge=challenge,
            expected_rp_id=self.rp_id,
            expected_origin="https://localhost:5000",  # Should match your application origin
            require_user_verification=config["yubikey"]["user_verification"] == "required",
        )
        
        # Update the sign count
        self._update_sign_count(user_id, verification.new_sign_count)
        
        # Clean up the challenge
        self._remove_challenge(user_id)
        
        return {
            "verified": True,
            "user_id": user_id,
        }
    
    def _update_sign_count(self, user_id: str, new_sign_count: int) -> None:
        """
        Update the sign count for a credential.
        
        Args:
            user_id: User ID
            new_sign_count: The new sign count
        """
        with open(self.credentials_file, "r") as f:
            credentials = json.load(f)
        
        if "users" in credentials and user_id in credentials["users"]:
            credentials["users"][user_id]["sign_count"] = new_sign_count
        
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f)


if __name__ == "__main__":
    # Simple test to verify the module
    webauthn_manager = WebAuthnManager()
    print(f"WebAuthn manager initialized with RP ID: {webauthn_manager.rp_id}")
    print(f"Credentials file path: {webauthn_manager.credentials_file}")
    
    # This part would need a browser to fully test
    print("Note: Full WebAuthn testing requires browser interaction.") 
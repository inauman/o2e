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
    AuthenticatorAttestationResponse,
    RegistrationCredential,
    AuthenticatorAssertionResponse,
    AuthenticationCredential,
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from datetime import datetime

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
                json.dump({"credentials": {}, "challenges": {}}, f)
        else:
            # Check if the file contains valid JSON
            try:
                with open(self.credentials_file, "r") as f:
                    data = json.load(f)
                # Ensure the structure is correct
                if not isinstance(data, dict):
                    with open(self.credentials_file, "w") as f:
                        json.dump({"credentials": {}, "challenges": {}}, f)
                # Make sure required keys exist
                if "credentials" not in data:
                    data["credentials"] = {}
                if "challenges" not in data:
                    data["challenges"] = {}
                # Write back with structure fixed
                with open(self.credentials_file, "w") as f:
                    json.dump(data, f)
            except (json.JSONDecodeError, ValueError):
                # File exists but is not valid JSON, overwrite with proper structure
                with open(self.credentials_file, "w") as f:
                    json.dump({"credentials": {}, "challenges": {}}, f)
    
    def generate_registration_options_for_user(self, username: str) -> Dict[str, Any]:
        """
        Generate WebAuthn registration options for a user.
        
        Args:
            username: The username to register
            
        Returns:
            WebAuthn registration options
        """
        try:
            print("Generating registration options for user", flush=True)
            # Create a user ID
            user_id = str(uuid.uuid4())
            print(f"Generated user ID: {user_id}", flush=True)
            
            # Convert user_id to bytes for WebAuthn
            user_id_bytes = user_id.encode('utf-8')
            print(f"Converted user ID to bytes, length: {len(user_id_bytes)}", flush=True)
            
            # Configure authenticator selection criteria based on config
            authenticator_selection = AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement(config["yubikey"]["user_verification"]),
                authenticator_attachment="cross-platform",  # YubiKey is cross-platform
                resident_key=ResidentKeyRequirement.DISCOURAGED,  # We don't need resident keys for this POC
            )
            print("Created authenticator selection criteria", flush=True)
            
            # Generate registration options
            options = generate_registration_options(
                rp_id=self.rp_id,
                rp_name=self.rp_name,
                user_id=user_id_bytes,
                user_name=username,
                user_display_name=username,
                attestation=AttestationConveyancePreference.NONE,
                authenticator_selection=authenticator_selection,
                supported_pub_key_algs=[
                    COSEAlgorithmIdentifier.ECDSA_SHA_256,  # -7 (ECDSA with P-256)
                    COSEAlgorithmIdentifier.RSASSA_PKCS1_v1_5_SHA_256,  # -257 (RSASSA-PKCS1-v1_5 with SHA-256)
                    COSEAlgorithmIdentifier.EDDSA,  # -8 (EdDSA)
                    COSEAlgorithmIdentifier.RSASSA_PSS_SHA_256,  # -37 (RSASSA-PSS with SHA-256)
                ],
                timeout=60000,  # 60 seconds
            )
            print("WebAuthn options generated", flush=True)
            print(f"Options type: {type(options)}", flush=True)
            
            # Create a response dictionary from the options object's attributes
            response_options = {}
            
            # Convert challenge to base64 for sending to browser
            raw_challenge = options.challenge
            print(f"Raw challenge type: {type(raw_challenge)}, length: {len(raw_challenge)}", flush=True)
            response_options["challenge"] = base64.b64encode(raw_challenge).decode("utf-8")
            print(f"Encoded challenge: {response_options['challenge']}", flush=True)
            
            # Add other required properties - use proper attribute access
            response_options["rp"] = {"id": options.rp.id, "name": options.rp.name}
            response_options["user"] = {
                "id": base64.b64encode(options.user.id).decode("utf-8"),
                "name": options.user.name,
                "displayName": options.user.display_name
            }
            
            # Add remaining properties
            response_options["pubKeyCredParams"] = []
            for alg in options.pub_key_cred_params:
                response_options["pubKeyCredParams"].append({
                    "type": "public-key",
                    "alg": int(alg.alg)  # Get the actual integer value of the enum
                })
            
            response_options["timeout"] = options.timeout
            response_options["attestation"] = options.attestation.value if hasattr(options.attestation, 'value') else str(options.attestation)
            
            if options.authenticator_selection:
                response_options["authenticatorSelection"] = {
                    "authenticatorAttachment": options.authenticator_selection.authenticator_attachment,
                    "residentKey": options.authenticator_selection.resident_key,
                    "requireResidentKey": options.authenticator_selection.require_resident_key,
                    "userVerification": options.authenticator_selection.user_verification
                }
            
            # Store the challenge for verification
            self._store_challenge(options.user.id, response_options["challenge"])
            print(f"Challenge stored for user ID: {options.user.id}", flush=True)
            
            # Create a session to remember the user ID
            from flask import session
            user_id_str = options.user.id.decode("utf-8") if isinstance(options.user.id, bytes) else options.user.id
            session["registering_user_id"] = user_id_str
            print(f"Stored user ID in session: {session['registering_user_id']}", flush=True)
            
            return response_options
        except Exception as e:
            import traceback
            print(f"Error in generate_registration_options_for_user: {str(e)}", flush=True)
            traceback.print_exc()
            raise
    
    def _store_challenge(self, user_id: str, challenge: str) -> None:
        """
        Store a challenge for later verification.
        
        Args:
            user_id: User ID (can be string or bytes)
            challenge: The base64-encoded challenge
        """
        try:
            # Ensure user_id is a string for JSON storage
            if isinstance(user_id, bytes):
                user_id = user_id.decode('utf-8')
                
            print(f"Storing challenge for user ID: {user_id}", flush=True)
            print(f"Credentials file: {self.credentials_file}", flush=True)
            
            # Ensure challenge is a string for JSON storage
            if isinstance(challenge, bytes):
                challenge = base64.b64encode(challenge).decode('utf-8')
                print(f"Converted challenge from bytes to base64 string", flush=True)
                
            with open(self.credentials_file, "r") as f:
                credentials = json.load(f)
            print("Loaded credentials file", flush=True)
            
            # Make sure the challenges key exists
            if "challenges" not in credentials:
                credentials["challenges"] = {}
            
            credentials["challenges"][user_id] = challenge
            print("Updated credentials with challenge", flush=True)
            
            with open(self.credentials_file, "w") as f:
                json.dump(credentials, f)
            print("Saved credentials file", flush=True)
        except Exception as e:
            import traceback
            print(f"Error in _store_challenge: {str(e)}", flush=True)
            traceback.print_exc()
            raise
    
    def _get_challenge(self, user_id: str) -> Optional[bytes]:
        """
        Get a stored challenge.
        
        Args:
            user_id: User ID (can be string or bytes)
            
        Returns:
            The challenge as bytes, or None if not found
        """
        # Ensure user_id is a string for JSON lookup
        if isinstance(user_id, bytes):
            user_id = user_id.decode('utf-8')
            print(f"Converted user_id from bytes to string: {user_id}", flush=True)
            
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
        
        try:
            # Add proper padding to base64 strings before decoding
            def pad_base64(b64_str):
                # Ensure we're working with a string
                if isinstance(b64_str, bytes):
                    b64_str = b64_str.decode('utf-8')
                
                # URLSafe base64 uses - and _ instead of + and /
                b64_str = b64_str.replace('-', '+').replace('_', '/')
                    
                # Remove any existing padding
                b64_str = b64_str.rstrip('=')
                
                # Add proper padding
                remainder = len(b64_str) % 4
                if remainder > 0:
                    b64_str += '=' * (4 - remainder)
                return b64_str
            
            # Process response data for verification with detailed logging
            print(f"Processing clientDataJSON, original length: {len(response['response']['clientDataJSON'])}", flush=True)
            client_data_b64 = pad_base64(response["response"]["clientDataJSON"])
            print(f"After padding clientDataJSON, length: {len(client_data_b64)}", flush=True)
            
            print(f"Processing attestationObject, original length: {len(response['response']['attestationObject'])}", flush=True)
            att_obj_b64 = pad_base64(response["response"]["attestationObject"])
            print(f"After padding attestationObject, length: {len(att_obj_b64)}", flush=True)
            
            print(f"Processing rawId, original length: {len(response['rawId'])}", flush=True)
            raw_id_b64 = pad_base64(response["rawId"])
            print(f"After padding rawId, length: {len(raw_id_b64)}", flush=True)
            
            # Create the registration credential with all required attributes in the correct JSON format
            # Note: we need to maintain the camelCase property names that match the WebAuthn API
            registration_credential = {
                "id": response["id"],
                "rawId": raw_id_b64,  # Must be "rawId" not "raw_id"
                "response": {
                    "clientDataJSON": client_data_b64,
                    "attestationObject": att_obj_b64
                },
                "type": "public-key"
            }
            
            # Verify the registration response
            verification = verify_registration_response(
                credential=registration_credential,
                expected_challenge=challenge,
                expected_rp_id=self.rp_id,
                expected_origin="https://localhost:5001",  # Use the correct port 5001 to match our application
            )
            
            # Store the credential
            self._store_credential(user_id, verification)
            
            # Clean up the challenge
            self._remove_challenge(user_id)
            
            # Return a simplified response that matches the expected format
            return {
                "verified": True,
                "credential_id": response["id"]
            }
            
        except Exception as e:
            import traceback
            print(f"Error in base64 decoding or verification: {str(e)}", flush=True)
            traceback.print_exc()
            raise ValueError(f"{str(e)}")
    
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
            "registered_at": datetime.now().isoformat()
        }
        
        print(f"Storing credential for user ID: {user_id}", flush=True)
        print(f"Credential ID: {credentials['users'][user_id]['credential_id']}", flush=True)
        print(f"Sign count: {verification.sign_count}", flush=True)
        
        with open(self.credentials_file, "w") as f:
            json.dump(credentials, f, indent=2)
    
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
        try:
            # Get the stored credential
            credential = self.get_user_credential(user_id)
            if not credential:
                raise ValueError(f"No credential found for user {user_id}")
            
            # Get the stored challenge
            challenge = self._get_challenge(user_id)
            if not challenge:
                raise ValueError("Challenge not found for user")
            
            # Add proper padding to base64 strings before decoding
            def pad_base64(b64_str):
                # Ensure we're working with a string
                if isinstance(b64_str, bytes):
                    b64_str = b64_str.decode('utf-8')
                
                # URLSafe base64 uses - and _ instead of + and /
                b64_str = b64_str.replace('-', '+').replace('_', '/')
                    
                # Remove any existing padding
                b64_str = b64_str.rstrip('=')
                
                # Add proper padding
                remainder = len(b64_str) % 4
                if remainder > 0:
                    b64_str += '=' * (4 - remainder)
                return b64_str
                
            # Process response data for verification with detailed logging
            print(f"Processing clientDataJSON, original length: {len(response['response']['clientDataJSON'])}", flush=True)
            client_data_b64 = pad_base64(response["response"]["clientDataJSON"])
            print(f"After padding clientDataJSON, length: {len(client_data_b64)}", flush=True)
            
            print(f"Processing authenticatorData, original length: {len(response['response']['authenticatorData'])}", flush=True)
            auth_data_b64 = pad_base64(response["response"]["authenticatorData"])
            print(f"After padding authenticatorData, length: {len(auth_data_b64)}", flush=True)
            
            print(f"Processing signature, original length: {len(response['response']['signature'])}", flush=True)
            signature_b64 = pad_base64(response["response"]["signature"])
            print(f"After padding signature, length: {len(signature_b64)}", flush=True)
            
            print(f"Processing rawId, original length: {len(response['rawId'])}", flush=True)
            raw_id_b64 = pad_base64(response["rawId"])
            print(f"After padding rawId, length: {len(raw_id_b64)}", flush=True)
            
            # Handle user_handle which might be None
            user_handle_b64 = None
            if "userHandle" in response["response"] and response["response"]["userHandle"]:
                user_handle_b64 = pad_base64(response["response"]["userHandle"])
                print(f"Processing userHandle, padded length: {len(user_handle_b64)}", flush=True)
            
            # Create authentication credential with all required attributes in the correct JSON format
            # Note: we need to maintain the camelCase property names that match the WebAuthn API
            authentication_credential = {
                "id": response["id"],
                "rawId": raw_id_b64,  # Must be "rawId" not "raw_id"
                "response": {
                    "clientDataJSON": client_data_b64,
                    "authenticatorData": auth_data_b64,
                    "signature": signature_b64
                },
                "type": "public-key"
            }
            
            # Add userHandle if it exists
            if user_handle_b64:
                authentication_credential["response"]["userHandle"] = user_handle_b64
            
            # Get credential public key from storage
            credential_public_key = base64.b64decode(credential["public_key"])
            
            # Verify the authentication response
            verification = verify_authentication_response(
                credential=authentication_credential,
                expected_challenge=challenge,
                expected_rp_id=self.rp_id,
                expected_origin="https://localhost:5001",  # Use the correct port 5001 to match our application
                credential_public_key=credential_public_key,
                credential_current_sign_count=credential["sign_count"],
                require_user_verification=config["yubikey"]["user_verification"] == "required"
            )
            
            # Update the sign count
            self._update_sign_count(user_id, verification.new_sign_count)
            
            # Clean up the challenge
            self._remove_challenge(user_id)
            
            # Return a simplified response
            return {
                "verified": True
            }
            
        except Exception as e:
            import traceback
            print(f"Error in authentication verification: {str(e)}", flush=True)
            traceback.print_exc()
            raise ValueError(f"{str(e)}")
    
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
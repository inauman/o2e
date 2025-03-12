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
                resident_key=ResidentKeyRequirement.REQUIRED,  # Changed from DISCOURAGED to REQUIRED for resident keys
                require_resident_key=True,  # Added to ensure resident keys are required
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
        # For resident keys, we could omit the allow_credentials parameter,
        # but we'll include it for compatibility with both resident and non-resident keys
        options = generate_authentication_options(
            rp_id=self.rp_id,
            allow_credentials=[{
                "type": "public-key",
                "id": base64.b64decode(credential["credential_id"]),
            }],
            user_verification=UserVerificationRequirement(config["yubikey"]["user_verification"]),
            timeout=60000,  # 60 seconds
        )
        
        # Convert the options object to a dictionary so we can access values with square brackets
        options_dict = options.asdict() if hasattr(options, 'asdict') else vars(options)
        
        # Log the keys in the options_dict for debugging
        print(f"Options keys: {list(options_dict.keys())}", flush=True)
        
        # Convert challenge to base64 for sending to browser
        options_dict["challenge"] = base64.b64encode(options_dict["challenge"]).decode("utf-8")
        
        # Check for the correct key name for credentials (could be allowCredentials or allow_credentials)
        cred_key = None
        if "allowCredentials" in options_dict:
            cred_key = "allowCredentials"
        elif "allow_credentials" in options_dict:
            cred_key = "allow_credentials"
        
        if cred_key:
            print(f"Found credentials key: {cred_key}", flush=True)
            # Convert all credential ids in credentials list to base64 strings
            for i, cred in enumerate(options_dict[cred_key]):
                if isinstance(cred["id"], bytes):
                    options_dict[cred_key][i]["id"] = base64.b64encode(cred["id"]).decode("utf-8")
        else:
            print("Warning: No credentials key found in options_dict", flush=True)
            print(f"Available keys: {list(options_dict.keys())}", flush=True)
        
        # Store the challenge
        self._store_challenge(user_id, options_dict["challenge"])
        
        return options_dict
    
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
    
    def delete_credential(self, user_id: str) -> bool:
        """
        Delete a user's credential.
        
        Args:
            user_id: The user ID whose credential should be deleted
            
        Returns:
            True if the credential was deleted, False if it wasn't found
        """
        try:
            # Ensure the credentials file exists
            self._ensure_storage_exists()
            
            with open(self.credentials_file, "r") as f:
                credentials = json.load(f)
            
            # Check if the user exists
            if "users" not in credentials or user_id not in credentials["users"]:
                return False
            
            # Delete the user's credential
            del credentials["users"][user_id]
            
            # Delete any challenges associated with the user
            if "challenges" in credentials and user_id in credentials["challenges"]:
                del credentials["challenges"][user_id]
                
            # Delete any seeds associated with the user (if applicable)
            if "encrypted_seeds" in credentials and user_id in credentials["encrypted_seeds"]:
                del credentials["encrypted_seeds"][user_id]
            
            # Save the updated credentials
            with open(self.credentials_file, "w") as f:
                json.dump(credentials, f)
            
            return True
        except Exception as e:
            import traceback
            print(f"Error deleting credential: {str(e)}", flush=True)
            traceback.print_exc()
            return False
    
    def generate_authentication_options_for_all_resident_keys(self) -> Dict[str, Any]:
        """
        Generate WebAuthn authentication options without specifying credentials.
        This will allow the YubiKey to present all resident keys for the relying party.
        
        Returns:
            WebAuthn authentication options
        """
        try:
            # Generate authentication options without specifying credentials
            options = generate_authentication_options(
                rp_id=self.rp_id,
                # No allow_credentials parameter - this makes the authenticator present all resident keys
                user_verification=UserVerificationRequirement(config["yubikey"]["user_verification"]),
                timeout=60000,  # 60 seconds
            )
            
            # Convert the options object to a dictionary
            options_dict = options.asdict() if hasattr(options, 'asdict') else vars(options)
            
            # Log the keys in the options_dict for debugging
            print(f"Options keys for resident keys: {list(options_dict.keys())}", flush=True)
            
            # Convert challenge to base64 for sending to browser
            options_dict["challenge"] = base64.b64encode(options_dict["challenge"]).decode("utf-8")
            
            # Store the challenge for verification
            self._store_challenge("resident_keys_auth", options_dict["challenge"])
            
            return options_dict
        except Exception as e:
            import traceback
            print(f"Error in generate_authentication_options_for_all_resident_keys: {str(e)}", flush=True)
            traceback.print_exc()
            raise
    
    def verify_resident_key_authentication_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify a WebAuthn authentication response for resident keys.
        This method extracts the user ID from the credential and verifies the authentication.
        
        Args:
            response: The authentication response from the client
            
        Returns:
            A dictionary with verification results, including the user ID
        """
        try:
            print(f"Verifying resident key authentication response: {json.dumps(response, indent=2)}", flush=True)
            
            # Get the challenge from storage
            challenge = self._get_challenge("resident_keys_auth")
            if not challenge:
                raise ValueError("No challenge found for resident key authentication")
            
            # Decode the challenge from base64
            challenge_bytes = base64.b64decode(challenge)
            
            # Process the client data JSON
            client_data_b64 = pad_base64(response["response"]["clientDataJSON"])
            client_data_bytes = base64.b64decode(client_data_b64)
            
            # Process the authenticator data
            auth_data_b64 = pad_base64(response["response"]["authenticatorData"])
            
            # Process the signature
            signature_b64 = pad_base64(response["response"]["signature"])
            
            # Process the user handle (if present)
            user_handle_b64 = None
            if response["response"].get("userHandle"):
                user_handle_b64 = pad_base64(response["response"]["userHandle"])
                user_handle_bytes = base64.b64decode(user_handle_b64)
                # The user handle is the user ID in bytes
                user_id = user_handle_bytes.decode("utf-8")
                print(f"Extracted user ID from user handle: {user_id}", flush=True)
            else:
                # If no user handle, we need to find the credential in our storage
                credential_id_b64 = response["rawId"]
                user_id = self._find_user_by_credential_id(credential_id_b64)
                if not user_id:
                    raise ValueError("Could not determine user ID from credential")
                print(f"Found user ID from credential ID: {user_id}", flush=True)
            
            # Get the credential from storage
            credential = self.get_user_credential(user_id)
            if not credential:
                raise ValueError(f"No credential found for user {user_id}")
            
            # Create the authentication credential
            authentication_credential = {
                "id": response["id"],
                "rawId": pad_base64(response["rawId"]),
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
                expected_challenge=challenge_bytes,
                expected_rp_id=self.rp_id,
                expected_origin="https://localhost:5001",  # Use the correct port 5001 to match our application
                credential_public_key=credential_public_key,
                credential_current_sign_count=credential["sign_count"],
                require_user_verification=config["yubikey"]["user_verification"] == "required"
            )
            
            # Update the sign count
            self._update_sign_count(user_id, verification.new_sign_count)
            
            # Clean up the challenge
            self._remove_challenge("resident_keys_auth")
            
            # Return a simplified response with the user ID
            return {
                "verified": True,
                "user_id": user_id,
                "credential_id": response.get("id")  # Include the credential ID in the response
            }
            
        except Exception as e:
            import traceback
            print(f"Error in resident key authentication verification: {str(e)}", flush=True)
            traceback.print_exc()
            raise ValueError(f"{str(e)}")
    
    def _find_user_by_credential_id(self, credential_id_b64: str) -> Optional[str]:
        """
        Find a user by credential ID.
        
        Args:
            credential_id_b64: Base64-encoded credential ID
            
        Returns:
            User ID or None if not found
        """
        try:
            with open(self.credentials_file, "r") as f:
                credentials = json.load(f)
            
            if "users" not in credentials:
                return None
            
            for user_id, user_data in credentials["users"].items():
                if user_data.get("credential_id") == credential_id_b64:
                    return user_id
            
            return None
        except Exception as e:
            print(f"Error finding user by credential ID: {str(e)}", flush=True)
            return None


if __name__ == "__main__":
    # Simple test to verify the module
    webauthn_manager = WebAuthnManager()
    print(f"WebAuthn manager initialized with RP ID: {webauthn_manager.rp_id}")
    print(f"Credentials file path: {webauthn_manager.credentials_file}")
    
    # This part would need a browser to fully test
    print("Note: Full WebAuthn testing requires browser interaction.") 
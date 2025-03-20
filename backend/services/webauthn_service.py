"""
Service for handling WebAuthn operations.
"""
import os
import base64
import secrets
import json
import uuid
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime, timezone

from models.user import User
from models.yubikey import YubiKey
from models.database import DatabaseManager


class WebAuthnService:
    """Service for handling WebAuthn operations"""
    
    def __init__(self):
        """Initialize the WebAuthn service with configuration"""
        self.origin = os.getenv('WEBAUTHN_ORIGIN', 'https://localhost')
        self.rp_id = os.getenv('WEBAUTHN_RP_ID', 'localhost')
        self.rp_name = os.getenv('WEBAUTHN_RP_NAME', 'YubiKey Manager')
        # Commented out as WebAuthnManager is not defined
        # self.webauthn_manager = WebAuthnManager(rp_id=self.rp_id, rp_name=self.rp_name, origin=self.origin)
        
        # Log initialization
        print(f"Initializing WebAuthnManager with rp_id: {self.rp_id}, rp_name: {self.rp_name}")
        print(f"WebAuthn origin: {self.origin}")
    
    def generate_registration_options(self, user_id: str, email: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate registration options for WebAuthn with support for multiple YubiKeys.
        
        Args:
            user_id: The ID of the user registering a YubiKey
            email: The email address of the user
            
        Returns:
            A tuple of (options, state) where options are the WebAuthn options to send to the client
            and state is the server state to save for verification
        """
        # Check if user can register another YubiKey
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        if not user.can_register_yubikey():
            raise ValueError(f"User has reached the maximum number of YubiKeys ({user.max_yubikeys})")
        
        # Get existing credentials to exclude
        existing_yubikeys = YubiKey.get_yubikeys_by_user_id(user_id)
        exclude_credentials = []
        
        for yubikey in existing_yubikeys:
            exclude_credentials.append({
                'id': base64.urlsafe_b64decode(yubikey.credential_id),
                'type': 'public-key',
                'transports': ['usb', 'nfc', 'ble']
            })
        
        # Generate a random challenge
        challenge = os.urandom(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge).rstrip(b'=').decode('ascii')
        
        # Create registration options
        options = {
            'publicKey': {
                'challenge': challenge_b64,
                'rp': {
                    'name': self.rp_name,
                    'id': self.rp_id
                },
                'user': {
                    'id': base64.urlsafe_b64encode(user_id.encode()).rstrip(b'=').decode('ascii'),
                    'name': email,
                    'displayName': email
                },
                'pubKeyCredParams': [
                    {'type': 'public-key', 'alg': -7},  # ES256
                    {'type': 'public-key', 'alg': -257}  # RS256
                ],
                'timeout': 60000,
                'excludeCredentials': exclude_credentials,
                'authenticatorSelection': {
                    'authenticatorAttachment': 'cross-platform',
                    'userVerification': 'preferred',
                    'residentKey': 'required',
                    'requireResidentKey': True
                },
                'attestation': 'none'
            }
        }
        
        # Save state for verification
        state = {
            'challenge': challenge_b64,
            'user_id': user_id,
            'email': email
        }
        
        if user_id:
            # Check if user has any existing YubiKeys
            existing_yubikeys = YubiKey.get_yubikeys_by_user_id(user_id)
            if not existing_yubikeys:
                options["authenticatorSelection"]["userVerification"] = "required"
        
        return options, state
    
    def verify_registration_response(self, credential: Dict[str, Any], state: Dict[str, Any], nickname: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify registration response from WebAuthn and store the credential.
        
        Args:
            credential: The credential response from the client
            state: The server state saved during registration options generation
            nickname: An optional nickname for the YubiKey
            
        Returns:
            A dictionary with the result of the verification
        """
        try:
            # Extract credential data
            credential_id = base64.urlsafe_b64encode(
                base64.urlsafe_b64decode(credential['rawId'])
            ).rstrip(b'=').decode('ascii')
            
            user_id = state['user_id']
            email = state['email']
            
            # Decode the attestation object and client data
            try:
                attestation_object = base64.urlsafe_b64decode(credential['response']['attestationObject'])
                client_data = base64.urlsafe_b64decode(credential['response']['clientDataJSON'])
            except Exception as e:
                raise ValueError(f"Failed to decode credential data: {str(e)}")
            
            # Create the YubiKey in the database
            # Set as primary if this is the user's first YubiKey
            user = User.get_by_id(user_id)
            is_primary = user.count_yubikeys() == 0
            
            yubikey = YubiKey.create(
                credential_id=credential_id,
                user_id=user_id,
                public_key=attestation_object,  # In production, extract the actual public key
                nickname=nickname or f"{email}'s YubiKey",
                aaguid=None,  # Extract from attestation if needed
                sign_count=0,
                is_primary=is_primary
            )
            
            if not yubikey:
                raise ValueError('Failed to store YubiKey credential')
            
            return {
                'success': True,
                'user_id': user_id,
                'credential_id': credential_id,
                'is_primary': yubikey.is_primary
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def generate_authentication_options(self, user_id: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate authentication options for WebAuthn with support for multiple YubiKeys.
        
        Args:
            user_id: The ID of the user authenticating
            
        Returns:
            A tuple of (options, state) where options are the WebAuthn options to send to the client
            and state is the server state to save for verification
        """
        # Get user
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        
        # Get user credentials
        yubikeys = YubiKey.get_yubikeys_by_user_id(user_id)
        if not yubikeys:
            raise ValueError(f"No YubiKeys registered for user {user_id}")
        
        # Generate a random challenge
        challenge = os.urandom(32)
        challenge_b64 = base64.urlsafe_b64encode(challenge).rstrip(b'=').decode('ascii')
        
        # Create authentication options
        options = {
            'publicKey': {
                'challenge': challenge_b64,
                'timeout': 60000,
                'rpId': self.rp_id,
                'allowCredentials': [
                    {
                        'id': base64.urlsafe_b64decode(yubikey.credential_id),
                        'type': 'public-key',
                        'transports': ['usb', 'nfc', 'ble']
                    }
                    for yubikey in yubikeys
                ],
                'userVerification': 'preferred'
            }
        }
        
        # Save state for verification
        state = {
            'challenge': challenge_b64,
            'user_id': user_id
        }
        
        return options, state
    
    def verify_authentication_response(self, credential: Dict[str, Any], state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify authentication response from WebAuthn.
        
        Args:
            credential: The credential response from the client
            state: The server state saved during authentication options generation
            
        Returns:
            A dictionary with the result of the verification
        """
        try:
            # Extract credential data
            credential_id = base64.urlsafe_b64encode(
                base64.urlsafe_b64decode(credential['rawId'])
            ).rstrip(b'=').decode('ascii')
            
            user_id = state['user_id']
            
            # Get the YubiKey from the database
            yubikey = YubiKey.get_by_credential_id(credential_id)
            if not yubikey:
                return {'success': False, 'error': 'YubiKey not found'}
            
            if yubikey.user_id != user_id:
                return {'success': False, 'error': 'YubiKey does not belong to this user'}
            
            # Update sign count and last used timestamp
            new_sign_count = credential.get('response', {}).get('authenticatorData', {}).get('signCount', 0)
            yubikey.update_sign_count(new_sign_count)
            
            # Get user for additional info
            user = User.get_by_id(user_id)
            if user:
                user.update_last_login()
            
            return {
                'success': True,
                'user_id': user_id,
                'credential_id': credential_id,
                'is_primary': yubikey.is_primary,
                'email': user.email if user else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_yubikeys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all YubiKeys registered for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            A list of YubiKey information dictionaries
        """
        yubikeys = YubiKey.get_yubikeys_by_user_id(user_id)
        
        return [
            {
                'credential_id': yubikey.credential_id,
                'nickname': yubikey.nickname,
                'registration_date': yubikey.registration_date,
                'is_primary': yubikey.is_primary
            }
            for yubikey in yubikeys
        ]
    
    def set_primary_yubikey(self, user_id: str, credential_id: str) -> bool:
        """
        Set a YubiKey as the primary YubiKey for a user.
        
        Args:
            user_id: The ID of the user
            credential_id: The ID of the credential to set as primary
            
        Returns:
            True if successful, False otherwise
        """
        # Get the YubiKey
        yubikey = YubiKey.get_by_credential_id(credential_id)
        
        if not yubikey:
            return False
        
        if yubikey.user_id != user_id:
            return False
        
        # Set as primary
        return yubikey.set_as_primary()
    
    def revoke_yubikey(self, user_id: str, credential_id: str) -> bool:
        """
        Revoke a YubiKey credential.
        
        Args:
            user_id: The ID of the user
            credential_id: The ID of the credential to revoke
            
        Returns:
            True if successful, False otherwise
        """
        # This method is not provided in the original file or the new implementation
        # It's assumed to exist as it's called in the set_primary_yubikey method
        # A placeholder implementation is provided
        return False  # Placeholder implementation, actual implementation needed
    
    def update_yubikey_nickname(self, user_id: str, credential_id: str, nickname: str) -> bool:
        """
        Update the nickname of a YubiKey.
        
        Args:
            user_id: The ID of the user
            credential_id: The ID of the credential to update
            nickname: The new nickname for the YubiKey
            
        Returns:
            True if successful, False otherwise
        """
        # This method is not provided in the original file or the new implementation
        # A placeholder implementation is provided
        return False  # Placeholder implementation, actual implementation needed 
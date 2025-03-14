"""
WebAuthn service for YubiKey Bitcoin Seed Storage
"""

import os
import json
import base64
import yaml
import secrets
from typing import Dict, Any, Tuple, Optional, List
from models.yubikey import YubiKey
from models.user import User

# This is a placeholder for the actual WebAuthn service implementation
# In a real implementation, this would be extracted from yubikey_utils.py

class WebAuthnService:
    """Service for handling WebAuthn operations"""
    
    def __init__(self):
        """Initialize the WebAuthn service"""
        # Load configuration
        with open(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'), 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Set up WebAuthn parameters
        self.rp_id = self.config['webauthn']['rp_id']
        self.rp_name = self.config['webauthn']['rp_name']
        self.origin = self.config['webauthn']['origin']
        
        # Load credentials from file
        self.credentials_file = self.config['data']['credentials_file']
        self.credentials = self._load_credentials()
    
    def _load_credentials(self) -> Dict[str, Any]:
        """Load credentials from file"""
        if os.path.exists(self.credentials_file):
            with open(self.credentials_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_credentials(self) -> None:
        """Save credentials to file"""
        with open(self.credentials_file, 'w') as f:
            json.dump(self.credentials, f, indent=2)
    
    def generate_registration_options(self, user_id: str, username: str) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Generate registration options for WebAuthn with support for multiple YubiKeys.
        
        Args:
            user_id: The ID of the user registering a YubiKey
            username: The username of the user
            
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
        existing_yubikeys = YubiKey.get_by_user_id(user_id)
        exclude_credentials = []
        
        for yubikey in existing_yubikeys:
            exclude_credentials.append({
                'id': yubikey.credential_id,
                'type': 'public-key',
                'transports': ['usb', 'nfc', 'ble']
            })
        
        # Generate a random challenge
        challenge = os.urandom(32)
        challenge_b64 = base64.b64encode(challenge).decode('utf-8')
        
        # Create registration options
        options = {
            'publicKey': {
                'rp': {
                    'name': self.rp_name,
                    'id': self.rp_id
                },
                'user': {
                    'id': base64.b64encode(user_id.encode('utf-8')).decode('utf-8'),
                    'name': username,
                    'displayName': username
                },
                'challenge': challenge_b64,
                'pubKeyCredParams': [
                    {'type': 'public-key', 'alg': -7},  # ES256
                    {'type': 'public-key', 'alg': -257}  # RS256
                ],
                'timeout': 60000,
                'attestation': 'direct',
                'authenticatorSelection': {
                    'authenticatorAttachment': 'cross-platform',
                    'requireResidentKey': True,  # Require resident keys for better UX
                    'residentKey': 'required',   # WebAuthn Level 2 syntax
                    'userVerification': 'preferred'
                },
                'excludeCredentials': exclude_credentials,
                'extensions': {
                    'hmacCreateSecret': True  # Enable FIDO2 hmac-secret extension
                }
            }
        }
        
        # Save state for verification
        state = {
            'challenge': challenge_b64,
            'user_id': user_id,
            'username': username
        }
        
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
        # This is a simplified implementation
        # In a real implementation, this would verify the attestation
        
        # Extract credential data
        credential_id = credential['id']
        user_id = state['user_id']
        username = state['username']
        
        # Extract public key from attestation
        public_key = base64.b64decode(credential['response']['attestationObject'])
        
        # Extract AAGUID if available
        aaguid = credential.get('aaguid')
        
        # Check if this is the first YubiKey for the user
        existing_yubikeys = YubiKey.get_by_user_id(user_id)
        is_primary = len(existing_yubikeys) == 0
        
        # Create the YubiKey in the database
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=user_id,
            public_key=public_key,
            aaguid=aaguid,
            nickname=nickname or f"{username}'s YubiKey {len(existing_yubikeys) + 1}",
            is_primary=is_primary
        )
        
        if not yubikey:
            return {'success': False, 'error': 'Failed to store YubiKey credential'}
        
        # Generate a unique salt for this YubiKey
        salt = secrets.token_bytes(32)
        
        # In a real implementation, we would store this salt securely
        # For now, we'll just return it
        
        return {
            'success': True, 
            'user_id': user_id,
            'credential_id': credential_id,
            'is_primary': is_primary,
            'salt': base64.b64encode(salt).decode('utf-8')
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
        yubikeys = YubiKey.get_by_user_id(user_id)
        
        if not yubikeys:
            raise ValueError(f"No YubiKeys registered for user {user_id}")
        
        # Generate a random challenge
        challenge = os.urandom(32)
        challenge_b64 = base64.b64encode(challenge).decode('utf-8')
        
        # Create authentication options
        options = {
            'publicKey': {
                'challenge': challenge_b64,
                'timeout': 60000,
                'rpId': self.rp_id,
                'allowCredentials': [
                    {
                        'id': yubikey.credential_id,
                        'type': 'public-key',
                        'transports': ['usb', 'nfc', 'ble']
                    }
                    for yubikey in yubikeys
                ],
                'userVerification': 'preferred',
                'extensions': {
                    'hmacGetSecret': {
                        'salt1': base64.b64encode(secrets.token_bytes(32)).decode('utf-8')
                    }
                }
            }
        }
        
        # Save state for verification
        state = {
            'challenge': challenge_b64,
            'user_id': user_id,
            'salt1': options['publicKey']['extensions']['hmacGetSecret']['salt1']
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
        # This is a simplified implementation
        # In a real implementation, this would verify the assertion
        
        # Extract credential data
        credential_id = credential['id']
        user_id = state['user_id']
        
        # Get the YubiKey from the database
        yubikey = YubiKey.get_by_credential_id(credential_id)
        
        if not yubikey:
            return {'success': False, 'error': 'Invalid credential'}
        
        if yubikey.user_id != user_id:
            return {'success': False, 'error': 'Credential does not belong to this user'}
        
        # Update the sign count to prevent replay attacks
        if 'response' in credential and 'authenticatorData' in credential['response']:
            # In a real implementation, we would extract the sign count from authenticatorData
            # For now, we'll just increment it
            yubikey.update_sign_count(yubikey.sign_count + 1)
        
        # Extract hmac-secret if available
        hmac_secret = None
        if ('response' in credential and 'extensions' in credential['response'] and 
            'hmacGetSecret' in credential['response']['extensions']):
            hmac_secret = credential['response']['extensions']['hmacGetSecret']['output1']
        
        # Get user
        user = User.get_by_id(user_id)
        
        # Update last login time
        user.update_last_login()
        
        return {
            'success': True, 
            'user_id': user_id,
            'credential_id': credential_id,
            'is_primary': yubikey.is_primary,
            'hmac_secret': hmac_secret
        }
    
    def list_yubikeys(self, user_id: str) -> List[Dict[str, Any]]:
        """
        List all YubiKeys registered for a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            A list of YubiKey information dictionaries
        """
        yubikeys = YubiKey.get_by_user_id(user_id)
        
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
        # Get the YubiKey
        yubikey = YubiKey.get_by_credential_id(credential_id)
        
        if not yubikey:
            return False
        
        if yubikey.user_id != user_id:
            return False
        
        # Check if this is the only YubiKey for the user
        yubikeys = YubiKey.get_by_user_id(user_id)
        if len(yubikeys) == 1:
            return False  # Cannot revoke the only YubiKey
        
        # Check if this is the primary YubiKey
        if yubikey.is_primary:
            # Find another YubiKey to set as primary
            for other_yubikey in yubikeys:
                if other_yubikey.credential_id != credential_id:
                    other_yubikey.set_as_primary()
                    break
        
        # Delete the YubiKey
        return yubikey.delete() 
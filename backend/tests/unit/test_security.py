# This file is deprecated and its tests have been moved to:
# - tests/unit/test_config.py for configuration tests
# - tests/unit/test_webauthn.py for WebAuthn tests

import unittest
import os
import base64
import json
import yaml
from unittest.mock import patch, mock_open, MagicMock

# Mock configuration for testing
MOCK_CONFIG = {
    "webauthn": {
        "rp_id": "example.com",
        "rp_name": "Example App",
        "origin": "https://example.com",
        "user_verification": "preferred",
        "require_touch": True
    },
    "yubikey": {
        "user_verification": "preferred"
    }
}

# Import functions and classes after mock setup to ensure mocks apply
from utils.security import load_config, WebAuthnManager

class TestSecurity(unittest.TestCase):
    def test_deprecated(self):
        """This test file is deprecated. See the new test files."""
        self.skipTest("Tests have been moved to test_config.py and test_webauthn.py")

class TestLoadConfig(unittest.TestCase):
    """Test cases for configuration loading."""
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_load_config(self, mock_yaml, mock_file):
        """Test loading configuration from YAML file"""
        # Get the backend directory path
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(backend_dir, "config.yaml")
        
        # Set up mock return values
        mock_file_handle = mock_file.return_value.__enter__.return_value
        mock_yaml.return_value = MOCK_CONFIG
        
        # Call the function
        config = load_config()
        
        # Verify the mocks were called correctly
        mock_file.assert_called_once_with(config_path, "r")
        mock_yaml.assert_called_once_with(mock_file_handle)
        
        # Verify the config was loaded correctly
        self.assertEqual(config, MOCK_CONFIG)

class TestWebAuthnManager(unittest.TestCase):
    """Test cases for WebAuthn manager."""
    
    def setUp(self):
        """Set up test environment."""
        self.rp_id = "example.com"
        self.rp_name = "Example App"
        self.origin = "https://example.com"
        
        # Test user data
        self.user_id = "test_user_123"
        self.username = "test@example.com"
        self.display_name = "Test User"
        self.credential_id = base64.b64encode(b"test_credential_id").decode('utf-8')
        self.public_key = base64.b64encode(b"test_public_key").decode('utf-8')
        
        # Create a WebAuthn manager with test values
        with patch('utils.security.load_config', return_value=MOCK_CONFIG):
            self.manager = WebAuthnManager(self.rp_id, self.rp_name)
    
    def test_init(self):
        """Test initialization with custom and default values"""
        # Test with custom values
        self.assertEqual(self.manager.rp_id, self.rp_id)
        self.assertEqual(self.manager.rp_name, self.rp_name)
        self.assertEqual(self.manager.origin, self.origin)
        
        # Test with default values from config
        with patch('utils.security.load_config', return_value=MOCK_CONFIG):
            default_manager = WebAuthnManager()
            self.assertEqual(default_manager.rp_id, MOCK_CONFIG["webauthn"]["rp_id"])
            self.assertEqual(default_manager.rp_name, MOCK_CONFIG["webauthn"]["rp_name"])
            self.assertEqual(default_manager.origin, MOCK_CONFIG["webauthn"]["origin"])

    @patch('utils.security.generate_registration_options')
    def test_generate_registration_options(self, mock_generate_options):
        """Test generation of registration options"""
        # Setup mock return value
        mock_options = {
            'challenge': base64.b64encode(b'challenge').decode('utf-8'),
            'rp': {'id': self.rp_id, 'name': self.rp_name},
            'user': {'id': self.user_id, 'name': self.username, 'displayName': self.display_name},
            'pubKeyCredParams': [{'type': 'public-key', 'alg': -7}]
        }
        mock_generate_options.return_value = mock_options
        
        # Mock the generate_registration_options_for_user method
        with patch.object(self.manager, 'generate_registration_options_for_user', return_value=mock_options) as mock_method:
            # Call the method
            options = self.manager.generate_registration_options_for_user(self.username)
            
            # Verify the result
            self.assertEqual(options, mock_options)
            mock_method.assert_called_once_with(self.username)

    @patch('utils.security.verify_registration_response')
    def test_verify_registration_response(self, mock_verify_response):
        """Test verification of registration response"""
        # Setup mock data
        challenge = base64.b64encode(b'challenge').decode('utf-8')
        credential_data = {
            'id': self.credential_id,
            'rawId': self.credential_id,
            'type': 'public-key',
            'response': {
                'clientDataJSON': base64.b64encode(json.dumps({
                    'type': 'webauthn.create',
                    'challenge': challenge,
                    'origin': f'https://{self.rp_id}'
                }).encode()).decode(),
                'attestationObject': base64.b64encode(b'attestation_data').decode()
            }
        }
        
        # Setup mock return value
        mock_verification_result = {
            'credential_id': self.credential_id,
            'public_key': self.public_key
        }
        mock_verify_response.return_value = mock_verification_result
        
        # Mock the verify_registration_response method
        with patch.object(self.manager, 'verify_registration_response', return_value=mock_verification_result) as mock_method:
            # Call the method
            result = self.manager.verify_registration_response(credential_data)
            
            # Verify the result
            self.assertEqual(result, mock_verification_result)
            mock_method.assert_called_once_with(credential_data)

    @patch('utils.security.generate_authentication_options')
    def test_generate_authentication_options(self, mock_generate_options):
        """Test generation of authentication options"""
        # Setup mock return value
        mock_options = {
            'challenge': base64.b64encode(b'auth_challenge').decode('utf-8'),
            'allowCredentials': [{
                'id': self.credential_id,
                'type': 'public-key'
            }]
        }
        mock_generate_options.return_value = mock_options
        
        # Mock the generate_authentication_options method
        with patch.object(self.manager, 'generate_authentication_options', return_value=mock_options) as mock_method:
            # Call the method
            options = self.manager.generate_authentication_options(self.user_id)
            
            # Verify the result
            self.assertEqual(options, mock_options)
            mock_method.assert_called_once_with(self.user_id)

    @patch('utils.security.verify_authentication_response')
    def test_verify_authentication_response(self, mock_verify_response):
        """Test verification of authentication response"""
        # Setup mock data
        challenge = base64.b64encode(b'auth_challenge').decode('utf-8')
        credential_data = {
            'id': self.credential_id,
            'rawId': self.credential_id,
            'type': 'public-key',
            'response': {
                'clientDataJSON': base64.b64encode(json.dumps({
                    'type': 'webauthn.get',
                    'challenge': challenge,
                    'origin': f'https://{self.rp_id}'
                }).encode()).decode(),
                'authenticatorData': base64.b64encode(b'auth_data').decode(),
                'signature': base64.b64encode(b'signature').decode(),
                'userHandle': base64.b64encode(self.user_id.encode()).decode()
            }
        }
        
        # Setup mock return value
        mock_verification_result = {
            'success': True,
            'user_id': self.user_id
        }
        mock_verify_response.return_value = mock_verification_result
        
        # Mock the verify_authentication_response method
        with patch.object(self.manager, 'verify_authentication_response', return_value=mock_verification_result) as mock_method:
            # Call the method
            result = self.manager.verify_authentication_response(credential_data)
            
            # Verify the result
            self.assertEqual(result, mock_verification_result)
            mock_method.assert_called_once_with(credential_data) 
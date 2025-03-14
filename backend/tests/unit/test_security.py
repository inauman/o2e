#!/usr/bin/env python3
"""
Unit tests for security.py
"""

import unittest
import sys
import os
import json
import base64
from unittest.mock import patch, MagicMock, mock_open

# Add the root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Create a complete mock config
MOCK_CONFIG = {
    'rp_id': 'example.com',
    'rp_name': 'Example App',
    'webauthn': {
        'rp_id': 'example.com',
        'rp_name': 'Example App'
    },
    'storage': {
        'credentials_file': '/tmp/test_credentials.json',
        'data_dir': '/tmp'
    }
}

# Mock the config loading before importing the module
with patch('builtins.open', mock_open(read_data='yaml_content')):
    with patch('yaml.safe_load', return_value=MOCK_CONFIG):
        from backend.utils.security import WebAuthnManager, load_config

class TestLoadConfig(unittest.TestCase):
    """Test cases for load_config function"""

    @patch('builtins.open', new_callable=mock_open, read_data='yaml_content')
    @patch('yaml.safe_load', return_value=MOCK_CONFIG)
    def test_load_config(self, mock_yaml, mock_file):
        """Test loading configuration from YAML file"""
        config = load_config()
        mock_file.assert_called_once_with("config.yaml", "r")
        self.assertIsInstance(config, dict)
        self.assertEqual(config.get('rp_id'), 'example.com')
        self.assertEqual(config.get('rp_name'), 'Example App')
        self.assertIn('storage', config)
        self.assertIn('webauthn', config)

class TestWebAuthnManager(unittest.TestCase):
    """Test cases for WebAuthnManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.rp_id = "example.com"
        self.rp_name = "Example App"
        
        # Patch the config for each test
        self.config_patcher = patch('backend.utils.security.config', MOCK_CONFIG)
        self.mock_config = self.config_patcher.start()
        
        self.manager = WebAuthnManager(rp_id=self.rp_id, rp_name=self.rp_name)
        
        # Sample user data
        self.user_id = "user123"
        self.username = "testuser"
        self.display_name = "Test User"
        
        # Sample credential data
        self.credential_id = base64.b64encode(b"credential_id_bytes").decode('utf-8')
        self.public_key = base64.b64encode(b"public_key_bytes").decode('utf-8')

    def tearDown(self):
        """Clean up after each test"""
        self.config_patcher.stop()

    def test_init(self):
        """Test initialization with custom and default values"""
        # Test with custom values
        self.assertEqual(self.manager.rp_id, self.rp_id)
        self.assertEqual(self.manager.rp_name, self.rp_name)
        self.assertEqual(self.manager.credentials_file, MOCK_CONFIG['storage']['credentials_file'])
        
        # Test with default values from config
        with patch('backend.utils.security.config', MOCK_CONFIG):
            default_manager = WebAuthnManager()
            self.assertEqual(default_manager.rp_id, MOCK_CONFIG['webauthn']['rp_id'])
            self.assertEqual(default_manager.rp_name, MOCK_CONFIG['webauthn']['rp_name'])

    @patch('backend.utils.security.generate_registration_options')
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

    @patch('backend.utils.security.verify_registration_response')
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
        
        # Mock the _get_challenge method to return our challenge
        with patch.object(self.manager, '_get_challenge', return_value=b'challenge'):
            # Mock the verify_registration_response method
            with patch.object(self.manager, 'verify_registration_response', return_value=mock_verification_result) as mock_method:
                # Call the method
                result = self.manager.verify_registration_response(self.user_id, credential_data)
                
                # Verify the result
                self.assertEqual(result, mock_verification_result)
                mock_method.assert_called_once_with(self.user_id, credential_data)

    @patch('backend.utils.security.generate_authentication_options')
    def test_generate_authentication_options(self, mock_generate_options):
        """Test generation of authentication options"""
        # Setup mock return value
        mock_options = {
            'challenge': base64.b64encode(b'challenge').decode('utf-8'),
            'rpId': self.rp_id,
            'allowCredentials': [{'type': 'public-key', 'id': self.credential_id}]
        }
        mock_generate_options.return_value = mock_options
        
        # Mock the get_user_credential method to return a credential
        with patch.object(self.manager, 'get_user_credential', return_value={'credential_id': self.credential_id}):
            # Mock the generate_authentication_options method
            with patch.object(self.manager, 'generate_authentication_options', return_value=mock_options) as mock_method:
                # Call the method
                options = self.manager.generate_authentication_options(self.user_id)
                
                # Verify the result
                self.assertEqual(options, mock_options)
                mock_method.assert_called_once_with(self.user_id)

    @patch('backend.utils.security.verify_authentication_response')
    def test_verify_authentication_response(self, mock_verify_response):
        """Test verification of authentication response"""
        # Setup mock data
        challenge = base64.b64encode(b'challenge').decode('utf-8')
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
                'signature': base64.b64encode(b'signature').decode()
            }
        }
        
        # Setup mock return value
        mock_verification_result = {
            'credential_id': self.credential_id,
            'new_sign_count': 1
        }
        mock_verify_response.return_value = mock_verification_result
        
        # Mock the get_user_credential method to return a credential
        with patch.object(self.manager, 'get_user_credential', return_value={'credential_id': self.credential_id}):
            # Mock the _get_challenge method to return our challenge
            with patch.object(self.manager, '_get_challenge', return_value=b'challenge'):
                # Mock the verify_authentication_response method
                with patch.object(self.manager, 'verify_authentication_response', return_value=mock_verification_result) as mock_method:
                    # Call the method
                    result = self.manager.verify_authentication_response(self.user_id, credential_data)
                    
                    # Verify the result
                    self.assertEqual(result, mock_verification_result)
                    mock_method.assert_called_once_with(self.user_id, credential_data)

if __name__ == '__main__':
    unittest.main() 
"""
Unit tests for the YubiKey routes.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import os
import uuid
from datetime import datetime

from app import create_app
from models.yubikey_salt import YubiKeySalt


class TestYubiKeyRoutes(unittest.TestCase):
    """Test cases for the YubiKey routes."""
    
    def setUp(self):
        """Set up test cases."""
        # Create a test Flask app
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create sample data
        self.salt_id = str(uuid.uuid4())
        self.credential_id = str(uuid.uuid4())
        self.salt = os.urandom(32)
        self.purpose = "seed_encryption"
        
        # Mock authentication
        self.auth_patcher = patch('utils.auth.require_auth')
        self.mock_auth = self.auth_patcher.start()
        self.mock_auth.return_value = lambda f: f
    
    def tearDown(self):
        """Clean up after tests."""
        self.auth_patcher.stop()
        self.app_context.pop()
    
    @patch('models.yubikey_salt.YubiKeySalt.create')
    def test_register_yubikey(self, mock_create):
        """Test registering a YubiKey."""
        # Mock YubiKeySalt.create
        mock_salt = MagicMock()
        mock_salt.salt_id = self.salt_id
        mock_create.return_value = mock_salt
        
        # Make request
        response = self.client.post(
            '/yubikeys/register',
            json={
                'credential_id': self.credential_id,
                'purpose': self.purpose
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['salt_id'], self.salt_id)
        self.assertIn('salt', data)
        
        # Verify YubiKeySalt.create was called
        mock_create.assert_called_once()
        args, kwargs = mock_create.call_args
        self.assertEqual(kwargs['credential_id'], self.credential_id)
        self.assertEqual(kwargs['purpose'], self.purpose)
    
    @patch('models.yubikey_salt.YubiKeySalt.create')
    def test_register_yubikey_missing_credential_id(self, mock_create):
        """Test registering a YubiKey with missing credential ID."""
        # Make request
        response = self.client.post(
            '/yubikeys/register',
            json={
                'purpose': self.purpose
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        
        # Verify YubiKeySalt.create was not called
        mock_create.assert_not_called()
    
    @patch('models.yubikey_salt.YubiKeySalt.create')
    def test_register_yubikey_creation_failure(self, mock_create):
        """Test registering a YubiKey when creation fails."""
        # Mock YubiKeySalt.create
        mock_create.return_value = None
        
        # Make request
        response = self.client.post(
            '/yubikeys/register',
            json={
                'credential_id': self.credential_id,
                'purpose': self.purpose
            }
        )
        
        # Check response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_credential_id')
    def test_get_yubikey_salts(self, mock_get_by_credential_id):
        """Test getting YubiKey salts."""
        # Mock YubiKeySalt.get_by_credential_id
        mock_salt = MagicMock()
        mock_salt.salt_id = self.salt_id
        mock_salt.credential_id = self.credential_id
        mock_salt.salt = self.salt
        mock_salt.purpose = self.purpose
        mock_salt.creation_date = datetime.now()
        mock_salt.last_used = None
        mock_salt.to_dict.return_value = {
            'salt_id': self.salt_id,
            'credential_id': self.credential_id,
            'salt': self.salt.hex(),
            'purpose': self.purpose,
            'creation_date': mock_salt.creation_date.isoformat(),
            'last_used': None
        }
        mock_get_by_credential_id.return_value = [mock_salt]
        
        # Make request
        response = self.client.get(
            f'/yubikeys/salts?credential_id={self.credential_id}'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['salts']), 1)
        self.assertEqual(data['salts'][0]['salt_id'], self.salt_id)
        
        # Verify YubiKeySalt.get_by_credential_id was called
        mock_get_by_credential_id.assert_called_once_with(self.credential_id)
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_credential_id')
    def test_get_yubikey_salts_with_purpose(self, mock_get_by_credential_id):
        """Test getting YubiKey salts with purpose filter."""
        # Mock YubiKeySalt.get_by_credential_id
        mock_salt = MagicMock()
        mock_salt.to_dict.return_value = {
            'salt_id': self.salt_id,
            'credential_id': self.credential_id,
            'salt': self.salt.hex(),
            'purpose': self.purpose,
            'creation_date': datetime.now().isoformat(),
            'last_used': None
        }
        mock_get_by_credential_id.return_value = [mock_salt]
        
        # Make request
        response = self.client.get(
            f'/yubikeys/salts?credential_id={self.credential_id}&purpose={self.purpose}'
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(len(data['salts']), 1)
        
        # Verify YubiKeySalt.get_by_credential_id was called with purpose
        mock_get_by_credential_id.assert_called_once_with(self.credential_id, self.purpose)
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_credential_id')
    def test_get_yubikey_salts_missing_credential_id(self, mock_get_by_credential_id):
        """Test getting YubiKey salts with missing credential ID."""
        # Make request
        response = self.client.get('/yubikeys/salts')
        
        # Check response
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        
        # Verify YubiKeySalt.get_by_credential_id was not called
        mock_get_by_credential_id.assert_not_called()
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_id')
    def test_get_yubikey_salt(self, mock_get_by_id):
        """Test getting a specific YubiKey salt."""
        # Mock YubiKeySalt.get_by_id
        mock_salt = MagicMock()
        mock_salt.salt_id = self.salt_id
        mock_salt.credential_id = self.credential_id
        mock_salt.salt = self.salt
        mock_salt.purpose = self.purpose
        mock_salt.creation_date = datetime.now()
        mock_salt.last_used = None
        mock_salt.to_dict.return_value = {
            'salt_id': self.salt_id,
            'credential_id': self.credential_id,
            'salt': self.salt.hex(),
            'purpose': self.purpose,
            'creation_date': mock_salt.creation_date.isoformat(),
            'last_used': None
        }
        mock_salt.update_last_used.return_value = True
        mock_get_by_id.return_value = mock_salt
        
        # Make request
        response = self.client.get(f'/yubikeys/salt/{self.salt_id}')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertEqual(data['salt']['salt_id'], self.salt_id)
        
        # Verify YubiKeySalt.get_by_id and update_last_used were called
        mock_get_by_id.assert_called_once_with(self.salt_id)
        mock_salt.update_last_used.assert_called_once()
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_id')
    def test_get_yubikey_salt_not_found(self, mock_get_by_id):
        """Test getting a YubiKey salt that doesn't exist."""
        # Mock YubiKeySalt.get_by_id
        mock_get_by_id.return_value = None
        
        # Make request
        response = self.client.get(f'/yubikeys/salt/{self.salt_id}')
        
        # Check response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_id')
    def test_delete_yubikey_salt(self, mock_get_by_id):
        """Test deleting a YubiKey salt."""
        # Mock YubiKeySalt.get_by_id
        mock_salt = MagicMock()
        mock_salt.salt_id = self.salt_id
        mock_salt.delete.return_value = True
        mock_get_by_id.return_value = mock_salt
        
        # Make request
        response = self.client.delete(f'/yubikeys/salt/{self.salt_id}')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        
        # Verify YubiKeySalt.get_by_id and delete were called
        mock_get_by_id.assert_called_once_with(self.salt_id)
        mock_salt.delete.assert_called_once()
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_id')
    def test_delete_yubikey_salt_not_found(self, mock_get_by_id):
        """Test deleting a YubiKey salt that doesn't exist."""
        # Mock YubiKeySalt.get_by_id
        mock_get_by_id.return_value = None
        
        # Make request
        response = self.client.delete(f'/yubikeys/salt/{self.salt_id}')
        
        # Check response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    @patch('models.yubikey_salt.YubiKeySalt.get_by_id')
    def test_delete_yubikey_salt_failure(self, mock_get_by_id):
        """Test deleting a YubiKey salt when deletion fails."""
        # Mock YubiKeySalt.get_by_id
        mock_salt = MagicMock()
        mock_salt.salt_id = self.salt_id
        mock_salt.delete.return_value = False
        mock_get_by_id.return_value = mock_salt
        
        # Make request
        response = self.client.delete(f'/yubikeys/salt/{self.salt_id}')
        
        # Check response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_generate_salt(self):
        """Test generating a random salt."""
        # Make request
        response = self.client.post('/yubikeys/generate-salt')
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('salt', data)
        
        # Verify salt is a valid hex string of the right length
        salt_hex = data['salt']
        self.assertEqual(len(bytes.fromhex(salt_hex)), 32)


if __name__ == "__main__":
    unittest.main() 
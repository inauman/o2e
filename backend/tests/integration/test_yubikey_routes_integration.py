"""
Integration tests for the YubiKey routes.
"""
import unittest
import json
import os
import uuid
from datetime import datetime

from app import create_app
from models.database import DatabaseManager
from models.yubikey_salt import YubiKeySalt
from models.user import User


class TestYubiKeyRoutesIntegration(unittest.TestCase):
    """Integration test cases for the YubiKey routes."""
    
    def setUp(self):
        """Set up test cases."""
        # Create a test Flask app
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Set up the database
        self.db = DatabaseManager(':memory:')
        self.db.initialize_schema()
        
        # Create a test user directly in the database with a unique username
        self.user_id = str(uuid.uuid4())
        self.username = f"test_user_{uuid.uuid4().hex[:8]}"  # Generate a unique username
        self.db.execute_query(
            """
            INSERT INTO users (user_id, username, max_yubikeys)
            VALUES (?, ?, ?)
            """,
            (self.user_id, self.username, 5),
            commit=True
        )
        
        # Create a test YubiKey credential
        self.credential_id = str(uuid.uuid4())
        
        # Insert the YubiKey credential into the database
        self.db.execute_query(
            """
            INSERT INTO yubikeys (credential_id, user_id, public_key, is_primary)
            VALUES (?, ?, ?, ?)
            """,
            (self.credential_id, self.user_id, b'test_public_key', 1),
            commit=True
        )
        
        # Create a test auth token
        self.auth_token = "test_auth_token"
        
        # Mock the authentication
        self.app.config['TESTING_AUTH_USER_ID'] = self.user_id
        self.app.config['TESTING_AUTH_BYPASS'] = True
    
    def tearDown(self):
        """Clean up after tests."""
        # No need to explicitly clean up the in-memory database
        self.app_context.pop()
    
    def test_register_yubikey_flow(self):
        """Test the full flow of registering a YubiKey and retrieving its salt."""
        # Step 1: Register a YubiKey
        register_response = self.client.post(
            '/api/yubikey/register',
            json={
                'credential_id': self.credential_id,
                'purpose': 'seed_encryption'
            },
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check register response
        self.assertEqual(register_response.status_code, 201)
        register_data = json.loads(register_response.data)
        self.assertTrue(register_data['success'])
        self.assertIn('salt_id', register_data)
        self.assertIn('salt', register_data)
        
        salt_id = register_data['salt_id']
        
        # Step 2: Get the salt by ID
        get_salt_response = self.client.get(
            f'/api/yubikey/salt/{salt_id}',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check get salt response
        self.assertEqual(get_salt_response.status_code, 200)
        get_salt_data = json.loads(get_salt_response.data)
        self.assertTrue(get_salt_data['success'])
        self.assertEqual(get_salt_data['salt']['salt_id'], salt_id)
        self.assertEqual(get_salt_data['salt']['credential_id'], self.credential_id)
        self.assertEqual(get_salt_data['salt']['purpose'], 'seed_encryption')
        
        # Step 3: Get all salts for the credential
        get_salts_response = self.client.get(
            f'/api/yubikey/salts?credential_id={self.credential_id}',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check get salts response
        self.assertEqual(get_salts_response.status_code, 200)
        get_salts_data = json.loads(get_salts_response.data)
        self.assertTrue(get_salts_data['success'])
        self.assertEqual(len(get_salts_data['salts']), 1)
        self.assertEqual(get_salts_data['salts'][0]['salt_id'], salt_id)
        
        # Step 4: Delete the salt
        delete_response = self.client.delete(
            f'/api/yubikey/salt/{salt_id}',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check delete response
        self.assertEqual(delete_response.status_code, 200)
        delete_data = json.loads(delete_response.data)
        self.assertTrue(delete_data['success'])
        
        # Step 5: Verify the salt is deleted
        verify_delete_response = self.client.get(
            f'/api/yubikey/salt/{salt_id}',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check verify delete response
        self.assertEqual(verify_delete_response.status_code, 404)
    
    def test_multiple_salts_for_credential(self):
        """Test registering multiple salts for the same credential."""
        # Register first salt
        first_response = self.client.post(
            '/api/yubikey/register',
            json={
                'credential_id': self.credential_id,
                'purpose': 'seed_encryption'
            },
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        first_data = json.loads(first_response.data)
        first_salt_id = first_data['salt_id']
        
        # Register second salt with different purpose
        second_response = self.client.post(
            '/api/yubikey/register',
            json={
                'credential_id': self.credential_id,
                'purpose': 'another_purpose'
            },
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        second_data = json.loads(second_response.data)
        second_salt_id = second_data['salt_id']
        
        # Get all salts for the credential
        get_all_response = self.client.get(
            f'/api/yubikey/salts?credential_id={self.credential_id}',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check get all response
        get_all_data = json.loads(get_all_response.data)
        self.assertTrue(get_all_data['success'])
        self.assertEqual(len(get_all_data['salts']), 2)
        
        # Get salts filtered by purpose
        get_filtered_response = self.client.get(
            f'/api/yubikey/salts?credential_id={self.credential_id}&purpose=seed_encryption',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check get filtered response
        get_filtered_data = json.loads(get_filtered_response.data)
        self.assertTrue(get_filtered_data['success'])
        self.assertEqual(len(get_filtered_data['salts']), 1)
        self.assertEqual(get_filtered_data['salts'][0]['salt_id'], first_salt_id)
    
    def test_generate_salt(self):
        """Test generating a random salt."""
        response = self.client.post(
            '/api/yubikey/generate-salt',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        # Check response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('salt', data)
        
        # Verify salt is a valid hex string of the right length
        salt_hex = data['salt']
        self.assertEqual(len(bytes.fromhex(salt_hex)), 32)
        
        # Generate another salt and verify it's different
        second_response = self.client.post(
            '/api/yubikey/generate-salt',
            headers={'Authorization': f'Bearer {self.auth_token}'}
        )
        
        second_data = json.loads(second_response.data)
        second_salt = second_data['salt']
        
        self.assertNotEqual(salt_hex, second_salt)
    
    def test_unauthorized_access(self):
        """Test accessing routes without authentication."""
        # Try to register a YubiKey without auth
        register_response = self.client.post(
            '/api/yubikey/register',
            json={
                'credential_id': self.credential_id,
                'purpose': 'seed_encryption'
            }
        )
        
        # Check response (should be 401 Unauthorized)
        self.assertEqual(register_response.status_code, 401)
        
        # Try to get salts without auth
        get_salts_response = self.client.get(
            f'/api/yubikey/salts?credential_id={self.credential_id}'
        )
        
        # Check response (should be 401 Unauthorized)
        self.assertEqual(get_salts_response.status_code, 401)


if __name__ == "__main__":
    unittest.main() 
"""
Integration tests for the YubiKey routes.
"""
import pytest
import json
import os
import uuid
from datetime import datetime

from app import create_app
from models.database import DatabaseManager
from models.yubikey_salt import YubiKeySalt
from models.user import User
from config import TestConfig


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestConfig)
    # Enable test auth bypass for integration testing
    app.config['TESTING_AUTH_BYPASS'] = True
    return app


@pytest.fixture
def client(app):
    """Create a test client for the app."""
    return app.test_client()


@pytest.fixture
def app_context(app):
    """Provide an app context for testing."""
    with app.app_context():
        yield


@pytest.fixture
def test_db():
    """Set up the test database."""
    db = DatabaseManager(':memory:')
    db.initialize_schema()
    return db


@pytest.fixture
def test_user(test_db):
    """Create a test user in the database."""
    user_id = str(uuid.uuid4())
    email = f"test_user_{uuid.uuid4().hex[:8]}@example.com"  # Generate a unique email
    
    test_db.execute_query(
        """
        INSERT INTO users (user_id, email, max_yubikeys)
        VALUES (?, ?, ?)
        """,
        (user_id, email, 5),
        commit=True
    )
    return {'user_id': user_id, 'email': email}


@pytest.fixture
def test_yubikey(test_db, test_user):
    """Create a test YubiKey credential in the database."""
    credential_id = str(uuid.uuid4())
    nickname = f"Test YubiKey {uuid.uuid4().hex[:6]}"
    
    # Insert the YubiKey credential into the database
    test_db.execute_query(
        """
        INSERT INTO yubikeys (credential_id, user_id, public_key, nickname, is_primary)
        VALUES (?, ?, ?, ?, ?)
        """,
        (credential_id, test_user['user_id'], b'test_public_key', nickname, 1),
        commit=True
    )
    return {'credential_id': credential_id, 'user_id': test_user['user_id'], 'nickname': nickname}


@pytest.fixture
def auth_headers(app, test_user):
    """Create authentication headers for the test user."""
    # In a real test, we would generate a proper JWT token
    # For now, we'll rely on the TESTING_AUTH_BYPASS config
    app.config['TESTING_AUTH_USER_ID'] = test_user['user_id']
    
    return {
        'Authorization': f'Bearer test_auth_token',
        'Content-Type': 'application/json'
    }


class TestYubiKeyRoutesIntegration:
    """Integration test cases for the YubiKey routes."""
    
    def test_register_yubikey_flow(self, client, auth_headers, test_yubikey, app_context):
        """Test the full flow of registering a YubiKey and retrieving its salt."""
        # Step 1: Register a YubiKey
        register_response = client.post(
            '/api/yubikey/register',
            json={
                'credential_id': test_yubikey['credential_id'],
                'purpose': 'seed_encryption'
            },
            headers=auth_headers
        )
        
        # Check register response
        assert register_response.status_code == 201
        register_data = json.loads(register_response.data)
        assert register_data['success'] is True
        assert 'salt_id' in register_data
        assert 'salt' in register_data
        
        salt_id = register_data['salt_id']
        
        # Step 2: Get the salt by ID
        get_salt_response = client.get(
            f'/api/yubikey/salt/{salt_id}',
            headers=auth_headers
        )
        
        # Check get salt response
        assert get_salt_response.status_code == 200
        get_salt_data = json.loads(get_salt_response.data)
        assert get_salt_data['success'] is True
        assert get_salt_data['salt']['salt_id'] == salt_id
        assert get_salt_data['salt']['credential_id'] == test_yubikey['credential_id']
        assert get_salt_data['salt']['purpose'] == 'seed_encryption'
        
        # Step 3: Get all salts for the credential
        get_salts_response = client.get(
            f'/api/yubikey/salts?credential_id={test_yubikey["credential_id"]}',
            headers=auth_headers
        )
        
        # Check get salts response
        assert get_salts_response.status_code == 200
        get_salts_data = json.loads(get_salts_response.data)
        assert get_salts_data['success'] is True
        assert len(get_salts_data['salts']) == 1
        assert get_salts_data['salts'][0]['salt_id'] == salt_id
        
        # Step 4: Delete the salt
        delete_response = client.delete(
            f'/api/yubikey/salt/{salt_id}',
            headers=auth_headers
        )
        
        # Check delete response
        assert delete_response.status_code == 200
        delete_data = json.loads(delete_response.data)
        assert delete_data['success'] is True
        
        # Step 5: Verify the salt is deleted
        verify_delete_response = client.get(
            f'/api/yubikey/salt/{salt_id}',
            headers=auth_headers
        )
        
        # Check verify delete response
        assert verify_delete_response.status_code == 404
    
    def test_multiple_salts_for_credential(self, client, auth_headers, test_yubikey, app_context):
        """Test registering multiple salts for the same credential."""
        # Register first salt
        first_response = client.post(
            '/api/yubikey/register',
            json={
                'credential_id': test_yubikey['credential_id'],
                'purpose': 'seed_encryption'
            },
            headers=auth_headers
        )
        
        first_data = json.loads(first_response.data)
        first_salt_id = first_data['salt_id']
        
        # Register second salt with different purpose
        second_response = client.post(
            '/api/yubikey/register',
            json={
                'credential_id': test_yubikey['credential_id'],
                'purpose': 'another_purpose'
            },
            headers=auth_headers
        )
        
        second_data = json.loads(second_response.data)
        second_salt_id = second_data['salt_id']
        
        # Get all salts for the credential
        get_all_response = client.get(
            f'/api/yubikey/salts?credential_id={test_yubikey["credential_id"]}',
            headers=auth_headers
        )
        
        # Check get all response
        get_all_data = json.loads(get_all_response.data)
        assert get_all_data['success'] is True
        assert len(get_all_data['salts']) == 2
        
        # Get salts filtered by purpose
        get_filtered_response = client.get(
            f'/api/yubikey/salts?credential_id={test_yubikey["credential_id"]}&purpose=seed_encryption',
            headers=auth_headers
        )
        
        # Check get filtered response
        get_filtered_data = json.loads(get_filtered_response.data)
        assert get_filtered_data['success'] is True
        assert len(get_filtered_data['salts']) == 1
        assert get_filtered_data['salts'][0]['salt_id'] == first_salt_id
    
    def test_generate_salt(self, client, auth_headers, app_context):
        """Test generating a random salt."""
        response = client.post(
            '/api/yubikey/generate-salt',
            headers=auth_headers
        )
        
        # Check response
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'salt' in data
        
        # Verify salt is a valid hex string of the right length
        salt_hex = data['salt']
        assert len(bytes.fromhex(salt_hex)) == 32
        
        # Generate another salt and verify it's different
        second_response = client.post(
            '/api/yubikey/generate-salt',
            headers=auth_headers
        )
        
        second_data = json.loads(second_response.data)
        second_salt = second_data['salt']
        
        assert salt_hex != second_salt
    
    def test_unauthorized_access(self, client, test_yubikey, app_context):
        """Test accessing routes without authentication."""
        # Try to register a YubiKey without auth
        register_response = client.post(
            '/api/yubikey/register',
            json={
                'credential_id': test_yubikey['credential_id'],
                'purpose': 'seed_encryption'
            }
        )
        
        # Check response (should be 401 Unauthorized)
        assert register_response.status_code == 401
        
        # Try to get salts without auth
        get_salts_response = client.get(
            f'/api/yubikey/salts?credential_id={test_yubikey["credential_id"]}'
        )
        
        # Check response (should be 401 Unauthorized)
        assert get_salts_response.status_code == 401 
"""
Unit tests for YubiKey routes.
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock
import base64
import uuid
from datetime import datetime, timedelta, timezone

JWT_SECRET = 'test_secret'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = 3600  # 1 hour


def generate_mock_token(user_id='test_user'):
    """Generate a mock JWT token for testing."""
    import jwt
    
    payload = {
        'sub': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(seconds=JWT_EXPIRATION),
        'iat': datetime.now(timezone.utc)
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


class TestYubiKeyRoutes:
    """Test cases for YubiKey routes."""
    
    @pytest.fixture(autouse=True)
    def setup(self, app, mock_auth_bypass, mock_yubikey_methods, mock_webauthn_service):
        """Set up the test environment."""
        self.app = app
        self.client = app.test_client()
        self.mock_user = mock_auth_bypass
        self.mock_yubikey = mock_yubikey_methods
        self.webauthn_service = mock_webauthn_service
        
        # Set up headers with mock token
        self.headers = {
            'Authorization': f'Bearer {generate_mock_token(self.mock_user.user_id)}',
            'Content-Type': 'application/json'
        }

    def test_list_yubikeys(self, app_context):
        """Test listing YubiKeys."""
        # Setup mock response from service
        mock_yubikeys = [
            {
                "credential_id": "credential1",
                "nickname": "YubiKey 1",
                "is_primary": True,
                "registration_date": "2023-01-01T00:00:00Z"
            }
        ]
        
        with patch("routes.yubikey_routes.webauthn_service.list_yubikeys", return_value=mock_yubikeys):
            response = self.client.get('/api/yubikey/yubikeys', headers=self.headers)
            
            # Debug output
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert "credential_id" in data[0]  # Just verify the field exists
        
    def test_delete_yubikey(self, app_context):
        """Test deleting a YubiKey."""
        credential_id = self.mock_yubikey.credential_id
        
        # First, make sure our mock implementation returns the expected credential
        with patch('models.yubikey.YubiKey.get_by_credential_id', return_value=self.mock_yubikey):
            # Mock the YubiKey.get_yubikeys_by_user_id to return multiple YubiKeys
            # This is needed to pass the "cannot delete last yubikey" check
            other_yubikey = MagicMock()
            other_yubikey.credential_id = str(uuid.uuid4())
            other_yubikey.user_id = self.mock_user.user_id
            
            with patch('models.yubikey.YubiKey.get_yubikeys_by_user_id', return_value=[self.mock_yubikey, other_yubikey]):
                # Mock the WebAuthnService revoke_yubikey method
                with patch("routes.yubikey_routes.webauthn_service.revoke_yubikey", return_value=True):
                    response = self.client.delete(
                        f'/api/yubikey/yubikeys/{credential_id}',
                        headers=self.headers
                    )
                    
                    # Debug output
                    print(f"Response status: {response.status_code}")
                    print(f"Response data: {response.data}")
                    
                    assert response.status_code == 200
                    data = json.loads(response.data)
                    assert data.get('success') is True
        
    def test_delete_yubikey_not_found(self, app_context):
        """Test deleting a non-existent YubiKey."""
        # Mock the get_by_credential_id to return None
        with patch('models.yubikey.YubiKey.get_by_credential_id', return_value=None):
            response = self.client.delete(
                '/api/yubikey/yubikeys/nonexistent',
                headers=self.headers
            )
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
        
    def test_delete_yubikey_last_one(self, app_context):
        """Test deleting the last YubiKey."""
        credential_id = self.mock_yubikey.credential_id
        
        # First, make sure our mock implementation returns the expected credential
        with patch('models.yubikey.YubiKey.get_by_credential_id', return_value=self.mock_yubikey):
            # Mock having only one YubiKey
            with patch('models.yubikey.YubiKey.get_yubikeys_by_user_id', return_value=[self.mock_yubikey]):
                response = self.client.delete(
                    f'/api/yubikey/yubikeys/{credential_id}',
                    headers=self.headers
                )
                
                # Debug output
                print(f"Response status: {response.status_code}")
                print(f"Response data: {response.data}")
                
                assert response.status_code == 403
                data = json.loads(response.data)
                assert 'error' in data
                assert 'only YubiKey' in data['error'] or 'Cannot revoke' in data['error']
    
    def test_set_primary_yubikey(self, app_context):
        """Test setting a YubiKey as primary."""
        credential_id = self.mock_yubikey.credential_id
        
        # Mock YubiKey.get_by_credential_id to return our mock
        with patch('models.yubikey.YubiKey.get_by_credential_id', return_value=self.mock_yubikey):
            # Make sure user_id matches for auth check
            self.mock_yubikey.user_id = self.mock_user.user_id
            
            response = self.client.put(
                f'/api/yubikey/yubikeys/{credential_id}/primary',
                headers=self.headers
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data.get('success') is True
        
    def test_registration_options(self, app_context):
        """Test generating registration options."""
        # Mock the WebAuthnService.generate_registration_options method
        options = {
            "challenge": base64.b64encode(b'test_challenge').decode(),
            "rp": {
                "name": "Test RP",
                "id": "localhost"
            },
            "user": {
                "id": "test-user-id",
                "name": "test-user",
                "displayName": "Test User"
            }
        }
        state = {"user_id": "test-user-id"}
        
        with patch("routes.yubikey_routes.webauthn_service.generate_registration_options", return_value=(options, state)):
            # Mock user.can_register_yubikey to return True
            self.mock_user.can_register_yubikey.return_value = True
            
            # Call the API endpoint
            response = self.client.post(
                '/api/yubikey/yubikeys/register/options',
                headers=self.headers,
                json={'username': 'test_user'}
            )
            
            # Debug output
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.data}")
            
            assert response.status_code == 200 
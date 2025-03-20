"""
This file contains pytest fixtures for unit tests.
These fixtures provide mocks and utilities for testing.
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock
import os
import flask
from flask import Flask, g
import functools

from models.yubikey import YubiKey
from services.webauthn_service import WebAuthnService
from config import TestConfig

# Import directly from app module
from app import create_app


@pytest.fixture
def app():
    """Create and configure a Flask app for testing."""
    app = create_app(TestConfig)
    # Enable test auth bypass
    app.config['TESTING_AUTH_BYPASS'] = True
    app.config['TESTING_AUTH_USER_ID'] = 'test_user_id'
    return app


@pytest.fixture
def app_context(app):
    """Provide an app context for testing."""
    with app.app_context():
        with app.test_request_context():
            yield


@pytest.fixture
def mock_auth_bypass():
    """Bypass authentication by mocking the login_required decorator and User model."""
    # Create a mock user
    mock_user = MagicMock()
    mock_user.user_id = 'test_user_id'
    mock_user.username = 'test_user'
    mock_user.email = 'test@example.com'
    mock_user.can_register_yubikey.return_value = True
    mock_user.count_yubikeys.return_value = 1
    
    # Mock User.get_by_id
    with patch('models.user.User.get_by_id', return_value=mock_user):
        # Mock login_required to set g.user
        def mock_login_required(f):
            @functools.wraps(f)
            def decorated_function(*args, **kwargs):
                # Set mock user in g
                g.user = mock_user
                return f(*args, **kwargs)
            return decorated_function
        
        # Mock the login_required decorator
        with patch('services.auth_service.login_required', mock_login_required):
            yield mock_user


@pytest.fixture
def mock_yubikey_methods():
    """Mock YubiKey model methods for isolated testing."""
    mock_yubikey = MagicMock()
    mock_yubikey.credential_id = str(uuid.uuid4())
    mock_yubikey.user_id = 'test_user_id'  # Match with mock_user.user_id
    mock_yubikey.nickname = "Test YubiKey"
    mock_yubikey.public_key = "test_public_key"
    mock_yubikey.sign_count = 0
    mock_yubikey.aaguid = "test_aaguid"
    mock_yubikey.is_primary = False
    
    # Set up methods on the mock
    mock_yubikey.delete.return_value = True
    mock_yubikey.update.return_value = True
    mock_yubikey.set_as_primary.return_value = True
    
    with patch('models.yubikey.YubiKey.get_by_credential_id', return_value=mock_yubikey), \
         patch('models.yubikey.YubiKey.get_yubikeys_by_user_id', return_value=[mock_yubikey]), \
         patch('models.yubikey.YubiKey.delete', return_value=True), \
         patch('models.yubikey.YubiKey.update', return_value=True), \
         patch('models.yubikey.YubiKey.create', return_value=mock_yubikey):
        yield mock_yubikey


@pytest.fixture
def mock_webauthn_service():
    """Mock WebAuthnService methods for isolated testing."""
    service_mock = MagicMock()
    
    # Define a YubiKey list result with expected fields
    service_mock.list_yubikeys.return_value = [
        {
            "credential_id": str(uuid.uuid4()),
            "nickname": "Test YubiKey",
            "is_primary": False,
            "registration_date": "2023-01-01T00:00:00Z"
        }
    ]
    
    # Return True for delete/revoke operations
    service_mock.revoke_yubikey.return_value = True
    service_mock.set_primary_yubikey.return_value = True
    
    # Create methods with correct signatures and return values
    # For revoke_yubikey implementation
    def mock_revoke_yubikey(user_id, credential_id):
        return True  # Always return success
        
    # For set_primary_yubikey implementation
    def mock_set_primary_yubikey(user_id, credential_id):
        return True  # Always return success
        
    # Add the mock implementations
    service_mock.revoke_yubikey = mock_revoke_yubikey
    service_mock.set_primary_yubikey = mock_set_primary_yubikey
    
    # Setup for registration flow
    options = {
        "challenge": "test_challenge",
        "rp": {
            "name": "Test RP",
            "id": "localhost"
        },
        "user": {
            "id": "test_user_id",
            "name": "test_user",
            "displayName": "test_user"
        },
        "pubKeyCredParams": [
            {
                "type": "public-key",
                "alg": -7
            }
        ],
        "timeout": 60000
    }
    state = {"user_id": "test_user_id"}
    service_mock.generate_registration_options.return_value = (options, state)
    
    # Setup for verification flow
    registration_result = {
        "success": True,
        "credential_id": "test_credential_id",
        "is_primary": False
    }
    service_mock.verify_registration_response.return_value = registration_result
    
    # Setup for authentication flow
    auth_result = {
        "success": True,
        "user_id": "test_user_id",
        "credential_id": "test_credential_id",
        "is_primary": False
    }
    service_mock.verify_authentication_response.return_value = auth_result
    
    # Complete mock by patching the WebAuthnService class
    with patch('services.webauthn_service.WebAuthnService', return_value=service_mock):
        yield service_mock 
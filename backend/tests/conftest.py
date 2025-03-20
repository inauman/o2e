"""
Global pytest fixtures for all tests.

This module contains fixtures that can be shared across all test files.
"""
import pytest
import uuid
import os
import jwt
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from models.database import DatabaseManager
from models.user import User
from app import create_app
from config import TestConfig

# JWT configuration for testing
JWT_SECRET = "test_secret_key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = timedelta(days=1)

@pytest.fixture(scope="session")
def app():
    """Create and configure a Flask app for the test session."""
    # Use the TestConfig for our tests
    test_app = create_app(TestConfig)
    
    # Set up application context
    with test_app.app_context():
        yield test_app


@pytest.fixture(scope="function")
def app_context(app):
    """Provide an application context for tests."""
    with app.app_context():
        with app.test_request_context():
            yield


@pytest.fixture(scope="function")
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture(scope="function")
def db():
    """Provide a database manager with initialized schema."""
    db_manager = DatabaseManager(':memory:')
    db_manager.initialize_schema()
    return db_manager


@pytest.fixture(scope="function")
def test_user(db):
    """Create a test user."""
    user_id = str(uuid.uuid4())
    username = f"test_{user_id}@example.com"
    max_yubikeys = 5
    
    # Create user directly in the database
    db.execute_query(
        """
        INSERT INTO users (user_id, username, max_yubikeys)
        VALUES (?, ?, ?)
        """,
        (user_id, username, max_yubikeys),
        commit=True
    )
    
    # Return a User object
    return User(
        user_id=user_id,
        username=username,
        max_yubikeys=max_yubikeys
    )


@pytest.fixture(scope="function")
def auth_token(test_user):
    """Generate a JWT auth token for the test user."""
    payload = {
        "sub": test_user.user_id,
        "exp": datetime.now(timezone.utc) + JWT_EXPIRATION_DELTA,
        "iat": datetime.now(timezone.utc)
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


@pytest.fixture(scope="function")
def mock_user_in_g(app_context, test_user):
    """Mock setting g.user within the app context."""
    from flask import g
    g.user = test_user
    g.user_id = test_user.user_id
    return test_user 
"""
Configuration settings for the application.
This module defines various configuration classes that can be used
to configure the application for different environments.
"""
import os
from datetime import timedelta


class BaseConfig:
    """Base configuration settings."""
    
    # General application settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'development-key')
    
    # Database settings
    DATABASE_PATH = os.environ.get('DATABASE_PATH', 'database.db')
    
    # WebAuthn settings
    WEBAUTHN_RP_ID = os.environ.get('WEBAUTHN_RP_ID', 'localhost')
    WEBAUTHN_RP_NAME = os.environ.get('WEBAUTHN_RP_NAME', 'YubiKey Bitcoin Seed Storage')
    WEBAUTHN_ORIGIN = os.environ.get('WEBAUTHN_ORIGIN', 'https://localhost:5001')
    WEBAUTHN_USER_VERIFICATION = 'preferred'
    WEBAUTHN_REQUIRE_TOUCH = True
    
    # JWT settings
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    
    # YubiKey settings
    YUBIKEY_MAX_DEVICES = 5
    

class DevelopmentConfig(BaseConfig):
    """Development configuration settings."""
    
    DEBUG = True
    TESTING = False
    
    # Override settings for development
    DATABASE_PATH = 'dev_database.db'


class TestConfig(BaseConfig):
    """Testing configuration settings."""
    
    DEBUG = True
    TESTING = True
    
    # Use in-memory database for testing
    DATABASE_PATH = ':memory:'
    
    # Shorter token expiration for testing
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # Test WebAuthn settings
    WEBAUTHN_RP_ID = 'test.local'
    WEBAUTHN_RP_NAME = 'Test RP'
    WEBAUTHN_ORIGIN = 'https://test.local'
    
    # Enable auth bypass for testing
    TESTING_AUTH_BYPASS = True


class ProductionConfig(BaseConfig):
    """Production configuration settings."""
    
    DEBUG = False
    TESTING = False
    
    # These values should be set through environment variables in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    DATABASE_PATH = os.environ.get('DATABASE_PATH')
    
    def __init__(self):
        """Check that required environment variables are set."""
        if not self.SECRET_KEY or not self.JWT_SECRET_KEY:
            raise ValueError("Production config requires SECRET_KEY and JWT_SECRET_KEY env variables") 
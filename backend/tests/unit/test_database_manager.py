"""
Unit tests for the DatabaseManager class.
"""
import os
import unittest
import tempfile
import sqlite3
import threading
from pathlib import Path
import uuid
import pytest
from unittest.mock import patch

from models.database import DatabaseManager


class TestDatabaseManager:
    """Tests for the DatabaseManager class."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Set up test environment."""
        # Create a database manager with an in-memory database
        self.db_manager = DatabaseManager(":memory:")
        yield
        # Clean up
        self.db_manager.close_all_connections()
    
    def test_connection(self):
        """Test that a connection can be established."""
        conn = self.db_manager.get_connection()
        assert conn is not None
    
    def test_initialize_schema(self):
        """Test that the schema can be initialized correctly."""
        # Initialize the schema
        result = self.db_manager.initialize_schema()
        
        # Check that the schema was created
        assert result is True
        
        # Check that the tables exist
        assert self.db_manager.table_exists("users")
        assert self.db_manager.table_exists("yubikeys")
        assert self.db_manager.table_exists("seeds")
        assert self.db_manager.table_exists("wrapped_keys")
        
        # Check table structure for users (with the correct schema)
        cursor = self.db_manager.execute_query("PRAGMA table_info(users)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert columns["user_id"] == "TEXT"
        assert columns["email"] == "TEXT"  # Updated to match actual schema using email instead of username
        assert columns["max_yubikeys"] == "INTEGER"
        
        # Check table structure for yubikeys
        cursor = self.db_manager.execute_query("PRAGMA table_info(yubikeys)")
        columns = {row[1]: row[2] for row in cursor.fetchall()}
        assert columns["credential_id"] == "TEXT"
        assert columns["user_id"] == "TEXT"
        assert columns["public_key"] == "BLOB"
        assert columns["nickname"] == "TEXT"
    
    def test_table_exists(self):
        """Test checking if a table exists."""
        # Initialize the schema first
        self.db_manager.initialize_schema()
        
        # Check that existing tables are detected
        assert self.db_manager.table_exists("users")
        assert self.db_manager.table_exists("yubikeys")
        
        # Check that non-existent tables are not detected
        assert not self.db_manager.table_exists("non_existent_table")
    
    def test_execute_query(self):
        """Test executing a simple query."""
        # Initialize the schema
        self.db_manager.initialize_schema()
        
        # Create test data with unique values
        user_id = str(uuid.uuid4())
        email = f"test_{user_id}@example.com"
        
        # Insert a test user
        cursor = self.db_manager.execute_query(
            "INSERT INTO users (user_id, email) VALUES (?, ?)",
            (user_id, email),
            commit=True
        )
        
        # Check that the query was executed
        assert cursor is not None
        
        # Verify that the user was inserted
        cursor = self.db_manager.execute_query(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        assert user is not None
        assert user["user_id"] == user_id
        assert user["email"] == email
    
    def test_execute_transaction(self):
        """Test executing a transaction with multiple queries."""
        # Initialize the schema
        self.db_manager.initialize_schema()
        
        # Create test data with unique values
        user_id = str(uuid.uuid4())
        email = f"test_{user_id}@example.com"
        credential_id = f"test_credential_{user_id}"
        public_key = b"test_public_key"
        
        # Create a transaction with multiple queries
        queries = [
            (
                "INSERT INTO users (user_id, email) VALUES (?, ?)",
                (user_id, email)
            ),
            (
                "INSERT INTO yubikeys (credential_id, user_id, public_key, nickname) VALUES (?, ?, ?, ?)",
                (credential_id, user_id, public_key, "Test YubiKey")
            )
        ]
        
        # Execute the transaction
        result = self.db_manager.execute_transaction(queries)
        
        # Check that the transaction succeeded
        assert result is True
        
        # Verify that the data was inserted
        cursor = self.db_manager.execute_query(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        assert user is not None
        
        cursor = self.db_manager.execute_query(
            "SELECT * FROM yubikeys WHERE credential_id = ?",
            (credential_id,)
        )
        yubikey = cursor.fetchone()
        assert yubikey is not None
    
    def test_failed_transaction(self):
        """Test that a transaction is rolled back on failure."""
        # Initialize the schema
        self.db_manager.initialize_schema()
        
        # Create test data with unique values
        user_id = str(uuid.uuid4())
        email = f"test_{user_id}@example.com"
        
        # First, insert a user normally
        self.db_manager.execute_query(
            "INSERT INTO users (user_id, email) VALUES (?, ?)",
            (user_id, email),
            commit=True
        )
        
        # Then create a transaction that should fail
        # The second query tries to insert a user with the same ID, which should fail
        queries = [
            (
                "INSERT INTO yubikeys (credential_id, user_id, public_key, nickname) VALUES (?, ?, ?, ?)",
                (f"test_credential_{user_id}", user_id, b"test_public_key", "Test YubiKey")
            ),
            (
                "INSERT INTO users (user_id, email) VALUES (?, ?)",
                (user_id, "different@example.com")  # This will fail due to user_id being a PRIMARY KEY
            )
        ]
        
        # Execute the transaction, which should fail
        result = self.db_manager.execute_transaction(queries)
        
        # Check that the transaction failed
        assert result is False
        
        # Verify that no yubikey was inserted (transaction rolled back)
        cursor = self.db_manager.execute_query(
            "SELECT * FROM yubikeys WHERE user_id = ?",
            (user_id,)
        )
        yubikey = cursor.fetchone()
        assert yubikey is None


if __name__ == "__main__":
    unittest.main() 
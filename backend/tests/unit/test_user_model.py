"""
Unit tests for the User model.
"""
import os
import unittest
import tempfile
import threading
from datetime import datetime

from models.database import DatabaseManager
from models.user import User


class TestUserModel(unittest.TestCase):
    """Test cases for the User model."""
    
    def setUp(self):
        """Set up the test environment before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_db.sqlite3")
        
        # Make sure the path exists and is writable
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Reset the singleton instance to ensure a clean test
        DatabaseManager._instance = None
        DatabaseManager._lock = threading.Lock()
        
        # Create a database manager instance
        self.db_manager = DatabaseManager(db_path=self.db_path)
        
        # Initialize the schema
        self.db_manager.initialize_schema()
    
    def tearDown(self):
        """Clean up after each test."""
        # Close all connections
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_create_user(self):
        """Test creating a new user."""
        # Create a new user
        email = "test@example.com"
        max_yubikeys = 5  # Default max YubiKeys
        
        user = User.create(email=email)
        
        # Check that the user was created successfully
        self.assertIsNotNone(user)
        self.assertEqual(user.email, email)
        self.assertEqual(user.max_yubikeys, max_yubikeys)
        
        # Check that the user has a valid UUID
        self.assertIsNotNone(user.user_id)
        self.assertEqual(len(user.user_id), 36)  # UUID4 length
        
        # Check that the user has creation timestamps
        self.assertIsNotNone(user.created_at)
        self.assertIsInstance(user.created_at, datetime)
        self.assertIsNone(user.last_login)  # Should be None initially
    
    def test_get_user_by_id(self):
        """Test getting a user by ID."""
        # Create a new user
        email = "test@example.com"
        user = User.create(email=email)
        
        # Get the user by ID
        retrieved_user = User.get_by_id(user.user_id)
        
        # Check that the user was retrieved successfully
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_id, user.user_id)
        self.assertEqual(retrieved_user.email, email)
        
        # Try to get a non-existent user
        non_existent_user = User.get_by_id("non_existent_id")
        self.assertIsNone(non_existent_user)
    
    def test_get_user_by_email(self):
        """Test getting a user by email."""
        # Create a new user
        email = "test@example.com"
        user = User.create(email=email)
        
        # Get the user by email
        retrieved_user = User.get_by_email(email)
        
        # Check that the user was retrieved successfully
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_id, user.user_id)
        self.assertEqual(retrieved_user.email, email)
        
        # Try to get a non-existent user
        non_existent_user = User.get_by_email("nonexistent@example.com")
        self.assertIsNone(non_existent_user)
    
    def test_get_all_users(self):
        """Test getting all users."""
        # Create some users
        user1 = User.create(email="user1@example.com")
        user2 = User.create(email="user2@example.com")
        user3 = User.create(email="user3@example.com")
        
        # Get all users
        users = User.get_all()
        
        # Check that all users were retrieved
        self.assertEqual(len(users), 3)
        
        # Check that the retrieved users are correct
        user_ids = [user.user_id for user in users]
        self.assertIn(user1.user_id, user_ids)
        self.assertIn(user2.user_id, user_ids)
        self.assertIn(user3.user_id, user_ids)
    
    def test_update_user(self):
        """Test updating a user."""
        # Create a new user
        email = "test@example.com"
        user = User.create(email=email)
        
        # Update the user's max_yubikeys
        new_max_yubikeys = 3
        user.max_yubikeys = new_max_yubikeys
        result = user.update()
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Get the user by ID to check the update
        updated_user = User.get_by_id(user.user_id)
        self.assertEqual(updated_user.max_yubikeys, new_max_yubikeys)
    
    def test_delete_user(self):
        """Test deleting a user."""
        # Create a new user
        email = "test@example.com"
        user = User.create(email=email)
        
        # Delete the user
        result = user.delete()
        
        # Check that the deletion was successful
        self.assertTrue(result)
        
        # Try to get the deleted user
        deleted_user = User.get_by_id(user.user_id)
        self.assertIsNone(deleted_user)
    
    def test_update_last_login(self):
        """Test updating a user's last login time."""
        # Create a new user
        email = "test@example.com"
        user = User.create(email=email)
        
        # Initially, last_login should be None
        self.assertIsNone(user.last_login)
        
        # Update the last login time
        result = user.update_last_login()
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Get the user by ID to check the update
        updated_user = User.get_by_id(user.user_id)
        self.assertIsNotNone(updated_user.last_login)
        self.assertIsInstance(updated_user.last_login, datetime)
    
    def test_count_yubikeys(self):
        """Test counting YubiKeys for a user."""
        # Create a new user
        email = "test@example.com"
        user = User.create(email=email)
        
        # Initially, the user should have no YubiKeys
        count = user.count_yubikeys()
        self.assertEqual(count, 0)
        
        # Insert some test YubiKeys
        db = DatabaseManager()
        
        for i in range(3):
            db.execute_query(
                """
                INSERT INTO yubikeys (credential_id, user_id, public_key, nickname, is_primary)
                VALUES (?, ?, ?, ?, ?)
                """,
                (f"credential_{i}", user.user_id, b"public_key", f"YubiKey {i}", i == 0),
                commit=True
            )
        
        # Count the YubiKeys again
        count = user.count_yubikeys()
        self.assertEqual(count, 3)
    
    def test_can_register_yubikey(self):
        """Test checking if a user can register another YubiKey."""
        # Create a new user with default max_yubikeys=5
        email = "test@example.com"
        user = User.create(email=email)
        
        # Initially, the user should be able to register a YubiKey
        self.assertTrue(user.can_register_yubikey())
        
        # Insert test YubiKeys up to max-1
        db = DatabaseManager()
        for i in range(4):  # Add 4 YubiKeys (one less than max)
            db.execute_query(
                """
                INSERT INTO yubikeys (credential_id, user_id, public_key, nickname, is_primary)
                VALUES (?, ?, ?, ?, ?)
                """,
                (f"credential_{i}", user.user_id, b"public_key", f"YubiKey {i}", i == 0),
                commit=True
            )
        
        # The user should still be able to register one more YubiKey
        self.assertTrue(user.can_register_yubikey())
        
        # Insert the final YubiKey
        db.execute_query(
            """
            INSERT INTO yubikeys (credential_id, user_id, public_key, nickname, is_primary)
            VALUES (?, ?, ?, ?, ?)
            """,
            ("credential_5", user.user_id, b"public_key", "YubiKey 5", False),
            commit=True
        )
        
        # The user should not be able to register more YubiKeys
        self.assertFalse(user.can_register_yubikey())
    
    def test_to_dict(self):
        """Test converting a User instance to a dictionary."""
        # Create a new user
        email = "test@example.com"
        user = User.create(email=email)
        
        # Convert the user to a dictionary
        user_dict = user.to_dict()
        
        # Check that the dictionary contains the expected keys and values
        self.assertEqual(user_dict["user_id"], user.user_id)
        self.assertEqual(user_dict["email"], email)
        self.assertEqual(user_dict["max_yubikeys"], 5)
        self.assertIn("created_at", user_dict)
        self.assertIn("last_login", user_dict)
        self.assertEqual(user_dict["yubikey_count"], 0)


if __name__ == "__main__":
    unittest.main() 
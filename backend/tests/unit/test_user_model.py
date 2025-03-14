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
        username = "test_user"
        max_yubikeys = 3
        
        user = User.create(username=username, max_yubikeys=max_yubikeys)
        
        # Check that the user was created successfully
        self.assertIsNotNone(user)
        self.assertEqual(user.username, username)
        self.assertEqual(user.max_yubikeys, max_yubikeys)
        
        # Check that the user has a valid UUID
        self.assertIsNotNone(user.user_id)
        self.assertEqual(len(user.user_id), 36)  # UUID4 length
        
        # Check that the user has a creation date
        self.assertIsNotNone(user.creation_date)
        self.assertIsInstance(user.creation_date, datetime)
    
    def test_get_user_by_id(self):
        """Test getting a user by ID."""
        # Create a new user
        username = "test_user"
        user = User.create(username=username)
        
        # Get the user by ID
        retrieved_user = User.get_by_id(user.user_id)
        
        # Check that the user was retrieved successfully
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_id, user.user_id)
        self.assertEqual(retrieved_user.username, username)
        
        # Try to get a non-existent user
        non_existent_user = User.get_by_id("non_existent_id")
        self.assertIsNone(non_existent_user)
    
    def test_get_user_by_username(self):
        """Test getting a user by username."""
        # Create a new user
        username = "test_user"
        user = User.create(username=username)
        
        # Get the user by username
        retrieved_user = User.get_by_username(username)
        
        # Check that the user was retrieved successfully
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.user_id, user.user_id)
        self.assertEqual(retrieved_user.username, username)
        
        # Try to get a non-existent user
        non_existent_user = User.get_by_username("non_existent_username")
        self.assertIsNone(non_existent_user)
    
    def test_get_all_users(self):
        """Test getting all users."""
        # Create some users
        user1 = User.create(username="user1")
        user2 = User.create(username="user2")
        user3 = User.create(username="user3")
        
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
        username = "test_user"
        user = User.create(username=username)
        
        # Update the user
        new_username = "updated_username"
        user.username = new_username
        result = user.update()
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Get the user by ID to check the update
        updated_user = User.get_by_id(user.user_id)
        self.assertEqual(updated_user.username, new_username)
    
    def test_delete_user(self):
        """Test deleting a user."""
        # Create a new user
        username = "test_user"
        user = User.create(username=username)
        
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
        username = "test_user"
        user = User.create(username=username)
        
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
        username = "test_user"
        user = User.create(username=username)
        
        # Initially, the user should have no YubiKeys
        count = user.count_yubikeys()
        self.assertEqual(count, 0)
        
        # Insert some test YubiKeys
        db = DatabaseManager()
        
        for i in range(3):
            db.execute_query(
                """
                INSERT INTO yubikeys (credential_id, user_id, public_key)
                VALUES (?, ?, ?)
                """,
                (f"credential_{i}", user.user_id, b"public_key"),
                commit=True
            )
        
        # Count the YubiKeys again
        count = user.count_yubikeys()
        self.assertEqual(count, 3)
    
    def test_can_register_yubikey(self):
        """Test checking if a user can register another YubiKey."""
        # Create a new user with max_yubikeys=2
        username = "test_user"
        max_yubikeys = 2
        user = User.create(username=username, max_yubikeys=max_yubikeys)
        
        # Initially, the user should be able to register a YubiKey
        self.assertTrue(user.can_register_yubikey())
        
        # Insert a test YubiKey
        db = DatabaseManager()
        db.execute_query(
            """
            INSERT INTO yubikeys (credential_id, user_id, public_key)
            VALUES (?, ?, ?)
            """,
            ("credential_1", user.user_id, b"public_key"),
            commit=True
        )
        
        # The user should still be able to register another YubiKey
        self.assertTrue(user.can_register_yubikey())
        
        # Insert a second test YubiKey
        db.execute_query(
            """
            INSERT INTO yubikeys (credential_id, user_id, public_key)
            VALUES (?, ?, ?)
            """,
            ("credential_2", user.user_id, b"public_key"),
            commit=True
        )
        
        # The user should not be able to register more YubiKeys
        self.assertFalse(user.can_register_yubikey())
    
    def test_to_dict(self):
        """Test converting a User instance to a dictionary."""
        # Create a new user
        username = "test_user"
        user = User.create(username=username)
        
        # Convert the user to a dictionary
        user_dict = user.to_dict()
        
        # Check that the dictionary contains the expected keys and values
        self.assertEqual(user_dict["user_id"], user.user_id)
        self.assertEqual(user_dict["username"], user.username)
        self.assertEqual(user_dict["creation_date"], user.creation_date)
        self.assertEqual(user_dict["last_login"], user.last_login)
        self.assertEqual(user_dict["max_yubikeys"], user.max_yubikeys)


if __name__ == "__main__":
    unittest.main() 
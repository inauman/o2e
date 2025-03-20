"""
Unit tests for the YubiKey model.
"""
import os
import unittest
import tempfile
import threading
from datetime import datetime

from models.database import DatabaseManager
from models.user import User
from models.yubikey import YubiKey


class TestYubiKeyModel(unittest.TestCase):
    """Test cases for the YubiKey model."""
    
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
        
        # Create a test user
        self.test_user = User.create(email="test@example.com")
    
    def tearDown(self):
        """Clean up after each test."""
        # Close all connections
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_create_yubikey(self):
        """Test creating a new YubiKey."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        nickname = "Test YubiKey"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key,
            nickname=nickname,
            is_primary=True  # First YubiKey should be primary
        )
        
        # Check that the YubiKey was created successfully
        self.assertIsNotNone(yubikey)
        self.assertEqual(yubikey.credential_id, credential_id)
        self.assertEqual(yubikey.user_id, self.test_user.user_id)
        self.assertEqual(yubikey.public_key, public_key)
        self.assertEqual(yubikey.nickname, nickname)
        self.assertTrue(yubikey.is_primary)
        
        # Check timestamps
        self.assertIsNotNone(yubikey.created_at)
        self.assertIsInstance(yubikey.created_at, datetime)
        self.assertIsNone(yubikey.last_used)  # Should be None initially
    
    def test_get_yubikey_by_credential_id(self):
        """Test getting a YubiKey by credential ID."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        nickname = "Test YubiKey"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key,
            nickname=nickname
        )
        
        # Get the YubiKey by credential ID
        retrieved_yubikey = YubiKey.get_by_credential_id(credential_id)
        
        # Check that the YubiKey was retrieved successfully
        self.assertIsNotNone(retrieved_yubikey)
        self.assertEqual(retrieved_yubikey.credential_id, credential_id)
        self.assertEqual(retrieved_yubikey.user_id, self.test_user.user_id)
        self.assertEqual(bytes(retrieved_yubikey.public_key), public_key)
        self.assertEqual(retrieved_yubikey.nickname, nickname)
        
        # Try to get a non-existent YubiKey
        non_existent_yubikey = YubiKey.get_by_credential_id("non_existent_id")
        self.assertIsNone(non_existent_yubikey)
    
    def test_get_yubikeys_by_user_id(self):
        """Test getting YubiKeys for a user."""
        # Create some YubiKeys
        yubikey1 = YubiKey.create(
            credential_id="credential_1",
            user_id=self.test_user.user_id,
            public_key=b"public_key_1",
            nickname="YubiKey 1",
            is_primary=True
        )
        
        yubikey2 = YubiKey.create(
            credential_id="credential_2",
            user_id=self.test_user.user_id,
            public_key=b"public_key_2",
            nickname="YubiKey 2"
        )
        
        # Get YubiKeys for the user
        yubikeys = YubiKey.get_yubikeys_by_user_id(self.test_user.user_id)
        
        # Check that we got both YubiKeys
        self.assertEqual(len(yubikeys), 2)
        
        # Check that one is primary
        primary_count = sum(1 for yk in yubikeys if yk.is_primary)
        self.assertEqual(primary_count, 1)
    
    def test_primary_yubikey(self):
        """Test setting and getting the primary YubiKey."""
        # Create some YubiKeys
        yubikey1 = YubiKey.create(
            credential_id="credential_1",
            user_id=self.test_user.user_id,
            public_key=b"public_key_1",
            nickname="YubiKey 1",
            is_primary=True
        )
        
        yubikey2 = YubiKey.create(
            credential_id="credential_2",
            user_id=self.test_user.user_id,
            public_key=b"public_key_2",
            nickname="YubiKey 2"
        )
        
        # Check that yubikey1 is primary
        primary = YubiKey.get_primary_for_user(self.test_user.user_id)
        self.assertIsNotNone(primary)
        self.assertEqual(primary.credential_id, yubikey1.credential_id)
        
        # Set yubikey2 as primary
        yubikey2.set_as_primary()
        
        # Check that yubikey2 is now primary
        primary = YubiKey.get_primary_for_user(self.test_user.user_id)
        self.assertIsNotNone(primary)
        self.assertEqual(primary.credential_id, yubikey2.credential_id)
        
        # Check that yubikey1 is no longer primary
        yubikey1 = YubiKey.get_by_credential_id(yubikey1.credential_id)
        self.assertFalse(yubikey1.is_primary)
    
    def test_update_yubikey(self):
        """Test updating a YubiKey."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        nickname = "Test YubiKey"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key,
            nickname=nickname
        )
        
        # Update the YubiKey
        new_nickname = "My YubiKey"
        yubikey.nickname = new_nickname
        result = yubikey.update()
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Get the YubiKey by credential ID to check the update
        updated_yubikey = YubiKey.get_by_credential_id(credential_id)
        self.assertEqual(updated_yubikey.nickname, new_nickname)
    
    def test_delete_yubikey(self):
        """Test deleting a YubiKey."""
        # Create two YubiKeys (can't delete the only one)
        yubikey1 = YubiKey.create(
            credential_id="credential_1",
            user_id=self.test_user.user_id,
            public_key=b"public_key_1",
            nickname="YubiKey 1",
            is_primary=True
        )
        
        yubikey2 = YubiKey.create(
            credential_id="credential_2",
            user_id=self.test_user.user_id,
            public_key=b"public_key_2",
            nickname="YubiKey 2"
        )
        
        # Try to delete the primary YubiKey (should fail)
        result = yubikey1.delete()
        self.assertFalse(result)
        
        # Set yubikey2 as primary and try again
        yubikey2.set_as_primary()
        result = yubikey1.delete()
        self.assertTrue(result)
        
        # Try to delete the last YubiKey (should fail)
        result = yubikey2.delete()
        self.assertFalse(result)
    
    def test_update_sign_count(self):
        """Test updating a YubiKey's sign count and last_used timestamp."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        nickname = "Test YubiKey"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key,
            nickname=nickname
        )
        
        # Initially, sign_count should be 0 and last_used should be None
        self.assertEqual(yubikey.sign_count, 0)
        self.assertIsNone(yubikey.last_used)
        
        # Update the sign count
        result = yubikey.update_sign_count(10)
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Get the YubiKey by credential ID to check the update
        updated_yubikey = YubiKey.get_by_credential_id(credential_id)
        self.assertEqual(updated_yubikey.sign_count, 10)
        self.assertIsNotNone(updated_yubikey.last_used)
        self.assertIsInstance(updated_yubikey.last_used, datetime)
        
        # Try to update with a lower sign count (should fail)
        result = updated_yubikey.update_sign_count(5)
        self.assertFalse(result)
        
        # Check that the sign count wasn't changed
        yubikey = YubiKey.get_by_credential_id(credential_id)
        self.assertEqual(yubikey.sign_count, 10)
    
    def test_max_yubikeys_per_user(self):
        """Test the maximum YubiKeys per user limit."""
        # Create YubiKeys up to the limit (5)
        yubikeys = []
        for i in range(5):
            yubikey = YubiKey.create(
                credential_id=f"credential_{i}",
                user_id=self.test_user.user_id,
                public_key=f"public_key_{i}".encode(),
                nickname=f"YubiKey {i}",
                is_primary=(i == 0)
            )
            self.assertIsNotNone(yubikey)
            yubikeys.append(yubikey)
        
        # Try to create one more (should fail)
        yubikey = YubiKey.create(
            credential_id="credential_6",
            user_id=self.test_user.user_id,
            public_key=b"public_key_6",
            nickname="YubiKey 6"
        )
        self.assertIsNone(yubikey)
    
    def test_to_dict(self):
        """Test converting a YubiKey instance to a dictionary."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        nickname = "Test YubiKey"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key,
            nickname=nickname,
            is_primary=True
        )
        
        # Convert the YubiKey to a dictionary
        yubikey_dict = yubikey.to_dict()
        
        # Check that the dictionary contains the expected keys and values
        self.assertEqual(yubikey_dict["credential_id"], credential_id)
        self.assertEqual(yubikey_dict["user_id"], self.test_user.user_id)
        self.assertEqual(yubikey_dict["nickname"], nickname)
        self.assertTrue(yubikey_dict["is_primary"])
        self.assertIn("created_at", yubikey_dict)
        self.assertIn("last_used", yubikey_dict)
        self.assertEqual(yubikey_dict["sign_count"], 0)


if __name__ == "__main__":
    unittest.main() 
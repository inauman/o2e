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
        self.test_user = User.create(username="test_user")
    
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
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key
        )
        
        # Check that the YubiKey was created successfully
        self.assertIsNotNone(yubikey)
        self.assertEqual(yubikey.credential_id, credential_id)
        self.assertEqual(yubikey.user_id, self.test_user.user_id)
        self.assertEqual(yubikey.public_key, public_key)
        
        # Check that the YubiKey has a registration date
        self.assertIsNotNone(yubikey.registration_date)
        self.assertIsInstance(yubikey.registration_date, datetime)
    
    def test_get_yubikey_by_credential_id(self):
        """Test getting a YubiKey by credential ID."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key
        )
        
        # Get the YubiKey by credential ID
        retrieved_yubikey = YubiKey.get_by_credential_id(credential_id)
        
        # Check that the YubiKey was retrieved successfully
        self.assertIsNotNone(retrieved_yubikey)
        self.assertEqual(retrieved_yubikey.credential_id, credential_id)
        self.assertEqual(retrieved_yubikey.user_id, self.test_user.user_id)
        self.assertEqual(bytes(retrieved_yubikey.public_key), public_key)
        
        # Try to get a non-existent YubiKey
        non_existent_yubikey = YubiKey.get_by_credential_id("non_existent_id")
        self.assertIsNone(non_existent_yubikey)
    
    def test_get_yubikeys_by_user_id(self):
        """Test getting YubiKeys for a user."""
        # Create some YubiKeys
        yubikey1 = YubiKey.create(
            credential_id="credential_1",
            user_id=self.test_user.user_id,
            public_key=b"public_key_1"
        )
        
        yubikey2 = YubiKey.create(
            credential_id="credential_2",
            user_id=self.test_user.user_id,
            public_key=b"public_key_2"
        )
        
        # Get YubiKeys for the user
        yubikeys = YubiKey.get_by_user_id(self.test_user.user_id)
        
        # Check that both YubiKeys were retrieved
        self.assertEqual(len(yubikeys), 2)
        
        # Check that the retrieved YubiKeys are correct
        credential_ids = [yubikey.credential_id for yubikey in yubikeys]
        self.assertIn(yubikey1.credential_id, credential_ids)
        self.assertIn(yubikey2.credential_id, credential_ids)
    
    def test_primary_yubikey(self):
        """Test setting and getting the primary YubiKey."""
        # Create some YubiKeys
        yubikey1 = YubiKey.create(
            credential_id="credential_1",
            user_id=self.test_user.user_id,
            public_key=b"public_key_1"
        )
        
        yubikey2 = YubiKey.create(
            credential_id="credential_2",
            user_id=self.test_user.user_id,
            public_key=b"public_key_2",
            is_primary=True
        )
        
        # Check that yubikey2 is primary
        primary = YubiKey.get_primary_for_user(self.test_user.user_id)
        self.assertIsNotNone(primary)
        self.assertEqual(primary.credential_id, yubikey2.credential_id)
        
        # Set yubikey1 as primary
        yubikey1.set_as_primary()
        
        # Check that yubikey1 is now primary
        primary = YubiKey.get_primary_for_user(self.test_user.user_id)
        self.assertIsNotNone(primary)
        self.assertEqual(primary.credential_id, yubikey1.credential_id)
        
        # Check that yubikey2 is no longer primary
        yubikey2 = YubiKey.get_by_credential_id(yubikey2.credential_id)
        self.assertFalse(yubikey2.is_primary)
    
    def test_update_yubikey(self):
        """Test updating a YubiKey."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key
        )
        
        # Update the YubiKey
        new_public_key = b"new_public_key"
        new_nickname = "My YubiKey"
        
        yubikey.public_key = new_public_key
        yubikey.nickname = new_nickname
        result = yubikey.update()
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Get the YubiKey by credential ID to check the update
        updated_yubikey = YubiKey.get_by_credential_id(credential_id)
        self.assertEqual(bytes(updated_yubikey.public_key), new_public_key)
        self.assertEqual(updated_yubikey.nickname, new_nickname)
    
    def test_delete_yubikey(self):
        """Test deleting a YubiKey."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key
        )
        
        # Delete the YubiKey
        result = yubikey.delete()
        
        # Check that the deletion was successful
        self.assertTrue(result)
        
        # Try to get the deleted YubiKey
        deleted_yubikey = YubiKey.get_by_credential_id(credential_id)
        self.assertIsNone(deleted_yubikey)
    
    def test_update_sign_count(self):
        """Test updating a YubiKey's sign count."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key
        )
        
        # Initially, sign_count should be 0
        self.assertEqual(yubikey.sign_count, 0)
        
        # Update the sign count
        result = yubikey.update_sign_count(10)
        
        # Check that the update was successful
        self.assertTrue(result)
        
        # Get the YubiKey by credential ID to check the update
        updated_yubikey = YubiKey.get_by_credential_id(credential_id)
        self.assertEqual(updated_yubikey.sign_count, 10)
        
        # Try to update with a lower sign count (should fail)
        result = updated_yubikey.update_sign_count(5)
        self.assertFalse(result)
        
        # Check that the sign count wasn't changed
        yubikey = YubiKey.get_by_credential_id(credential_id)
        self.assertEqual(yubikey.sign_count, 10)
    
    def test_max_yubikeys_per_user(self):
        """Test the maximum YubiKeys per user limit."""
        # Set the max YubiKeys for the test user to 2
        self.test_user.max_yubikeys = 2
        self.test_user.update()
        
        # Create first YubiKey
        yubikey1 = YubiKey.create(
            credential_id="credential_1",
            user_id=self.test_user.user_id,
            public_key=b"public_key_1"
        )
        self.assertIsNotNone(yubikey1)
        
        # Create second YubiKey
        yubikey2 = YubiKey.create(
            credential_id="credential_2",
            user_id=self.test_user.user_id,
            public_key=b"public_key_2"
        )
        self.assertIsNotNone(yubikey2)
        
        # Try to create a third YubiKey (should fail)
        yubikey3 = YubiKey.create(
            credential_id="credential_3",
            user_id=self.test_user.user_id,
            public_key=b"public_key_3"
        )
        self.assertIsNone(yubikey3)
        
        # Check that only 2 YubiKeys were created
        yubikeys = YubiKey.get_by_user_id(self.test_user.user_id)
        self.assertEqual(len(yubikeys), 2)
    
    def test_to_dict(self):
        """Test converting a YubiKey instance to a dictionary."""
        # Create a new YubiKey
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        nickname = "My YubiKey"
        
        yubikey = YubiKey.create(
            credential_id=credential_id,
            user_id=self.test_user.user_id,
            public_key=public_key,
            nickname=nickname
        )
        
        # Convert the YubiKey to a dictionary
        yubikey_dict = yubikey.to_dict()
        
        # Check that the dictionary contains the expected keys and values
        self.assertEqual(yubikey_dict["credential_id"], credential_id)
        self.assertEqual(yubikey_dict["user_id"], self.test_user.user_id)
        self.assertEqual(yubikey_dict["public_key"], public_key.hex())
        self.assertEqual(yubikey_dict["nickname"], nickname)
        self.assertEqual(yubikey_dict["sign_count"], 0)
        self.assertEqual(yubikey_dict["is_primary"], False)


if __name__ == "__main__":
    unittest.main() 
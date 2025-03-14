"""
Unit tests for the YubiKeySalt model.
"""
import unittest
from unittest.mock import patch, MagicMock
import uuid
from datetime import datetime

from models.yubikey_salt import YubiKeySalt


class TestYubiKeySalt(unittest.TestCase):
    """Test cases for the YubiKeySalt model."""
    
    def setUp(self):
        """Set up test cases."""
        # Create sample data
        self.salt_id = str(uuid.uuid4())
        self.credential_id = str(uuid.uuid4())
        self.salt = b"test_salt_data"
        self.purpose = "seed_encryption"
        
        # Create a mock YubiKeySalt
        self.mock_salt = YubiKeySalt(
            salt_id=self.salt_id,
            credential_id=self.credential_id,
            salt=self.salt,
            creation_date=datetime.now(),
            purpose=self.purpose
        )
    
    def test_init(self):
        """Test YubiKeySalt initialization."""
        salt = YubiKeySalt(
            salt_id=self.salt_id,
            credential_id=self.credential_id,
            salt=self.salt,
            purpose=self.purpose
        )
        
        self.assertEqual(salt.salt_id, self.salt_id)
        self.assertEqual(salt.credential_id, self.credential_id)
        self.assertEqual(salt.salt, self.salt)
        self.assertEqual(salt.purpose, self.purpose)
        self.assertIsInstance(salt.creation_date, datetime)
    
    def test_init_default_values(self):
        """Test YubiKeySalt initialization with default values."""
        salt = YubiKeySalt()
        
        self.assertIsNotNone(salt.salt_id)
        self.assertIsNone(salt.credential_id)
        self.assertIsNone(salt.salt)
        self.assertIsInstance(salt.creation_date, datetime)
        self.assertEqual(salt.purpose, "seed_encryption")
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_create_success(self, mock_execute_query):
        """Test creating a YubiKeySalt successfully."""
        # Mock database operation
        mock_execute_query.return_value = None
        
        # Create a YubiKeySalt
        salt = YubiKeySalt.create(
            credential_id=self.credential_id,
            salt=self.salt,
            purpose=self.purpose
        )
        
        # Verify the YubiKeySalt was created
        self.assertIsNotNone(salt)
        self.assertEqual(salt.credential_id, self.credential_id)
        self.assertEqual(salt.salt, self.salt)
        self.assertEqual(salt.purpose, self.purpose)
        
        # Verify the database was called
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("INSERT INTO yubikey_salts", args[0])
        self.assertEqual(len(args[1]), 4)  # 4 parameters for the query
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_create_exception(self, mock_execute_query):
        """Test exception during YubiKeySalt creation."""
        # Mock database operation raising an exception
        mock_execute_query.side_effect = Exception("Database error")
        
        # Create a YubiKeySalt
        salt = YubiKeySalt.create(
            credential_id=self.credential_id,
            salt=self.salt,
            purpose=self.purpose
        )
        
        # Verify the YubiKeySalt was not created
        self.assertIsNone(salt)
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_get_by_id_found(self, mock_execute_query):
        """Test retrieving a YubiKeySalt by ID when it exists."""
        # Mock database row
        mock_row = {
            "salt_id": self.salt_id,
            "credential_id": self.credential_id,
            "salt": self.salt,
            "creation_date": datetime.now(),
            "last_used": None,
            "purpose": self.purpose
        }
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = mock_row
        mock_execute_query.return_value = mock_cursor
        
        # Get the YubiKeySalt
        salt = YubiKeySalt.get_by_id(self.salt_id)
        
        # Verify the YubiKeySalt was found
        self.assertIsNotNone(salt)
        self.assertEqual(salt.salt_id, self.salt_id)
        self.assertEqual(salt.credential_id, self.credential_id)
        self.assertEqual(salt.salt, self.salt)
        self.assertEqual(salt.purpose, self.purpose)
        
        # Verify the database was called
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("SELECT * FROM yubikey_salts WHERE salt_id = ?", args[0])
        self.assertEqual(args[1], (self.salt_id,))
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_get_by_id_not_found(self, mock_execute_query):
        """Test retrieving a YubiKeySalt by ID when it doesn't exist."""
        # Mock cursor with no results
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_execute_query.return_value = mock_cursor
        
        # Get the YubiKeySalt
        salt = YubiKeySalt.get_by_id(self.salt_id)
        
        # Verify the YubiKeySalt was not found
        self.assertIsNone(salt)
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_get_by_credential_id(self, mock_execute_query):
        """Test retrieving YubiKeySalts by credential ID."""
        # Mock database rows
        mock_rows = [
            {
                "salt_id": self.salt_id,
                "credential_id": self.credential_id,
                "salt": self.salt,
                "creation_date": datetime.now(),
                "last_used": None,
                "purpose": self.purpose
            },
            {
                "salt_id": str(uuid.uuid4()),
                "credential_id": self.credential_id,
                "salt": b"another_salt",
                "creation_date": datetime.now(),
                "last_used": None,
                "purpose": "another_purpose"
            }
        ]
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_rows
        mock_execute_query.return_value = mock_cursor
        
        # Get the YubiKeySalts
        salts = YubiKeySalt.get_by_credential_id(self.credential_id)
        
        # Verify the YubiKeySalts were found
        self.assertEqual(len(salts), 2)
        self.assertEqual(salts[0].credential_id, self.credential_id)
        self.assertEqual(salts[1].credential_id, self.credential_id)
        
        # Verify the database was called
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("SELECT * FROM yubikey_salts WHERE credential_id = ?", args[0])
        self.assertEqual(args[1], (self.credential_id,))
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_get_by_credential_id_with_purpose(self, mock_execute_query):
        """Test retrieving YubiKeySalts by credential ID and purpose."""
        # Mock database rows
        mock_rows = [
            {
                "salt_id": self.salt_id,
                "credential_id": self.credential_id,
                "salt": self.salt,
                "creation_date": datetime.now(),
                "last_used": None,
                "purpose": self.purpose
            }
        ]
        
        # Mock cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_rows
        mock_execute_query.return_value = mock_cursor
        
        # Get the YubiKeySalts
        salts = YubiKeySalt.get_by_credential_id(self.credential_id, self.purpose)
        
        # Verify the YubiKeySalts were found
        self.assertEqual(len(salts), 1)
        self.assertEqual(salts[0].credential_id, self.credential_id)
        self.assertEqual(salts[0].purpose, self.purpose)
        
        # Verify the database was called
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("SELECT * FROM yubikey_salts WHERE credential_id = ? AND purpose = ?", args[0])
        self.assertEqual(args[1], (self.credential_id, self.purpose))
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_update_success(self, mock_execute_query):
        """Test updating a YubiKeySalt successfully."""
        # Mock database operation
        mock_execute_query.return_value = None
        
        # Update the YubiKeySalt
        result = self.mock_salt.update()
        
        # Verify the update was successful
        self.assertTrue(result)
        
        # Verify the database was called
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("UPDATE yubikey_salts", args[0])
        self.assertEqual(len(args[1]), 4)  # 4 parameters for the query
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_update_exception(self, mock_execute_query):
        """Test exception during YubiKeySalt update."""
        # Mock database operation raising an exception
        mock_execute_query.side_effect = Exception("Database error")
        
        # Update the YubiKeySalt
        result = self.mock_salt.update()
        
        # Verify the update failed
        self.assertFalse(result)
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_delete_success(self, mock_execute_query):
        """Test deleting a YubiKeySalt successfully."""
        # Mock database operation
        mock_execute_query.return_value = None
        
        # Delete the YubiKeySalt
        result = self.mock_salt.delete()
        
        # Verify the deletion was successful
        self.assertTrue(result)
        
        # Verify the database was called
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("DELETE FROM yubikey_salts WHERE salt_id = ?", args[0])
        self.assertEqual(args[1], (self.salt_id,))
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_delete_exception(self, mock_execute_query):
        """Test exception during YubiKeySalt deletion."""
        # Mock database operation raising an exception
        mock_execute_query.side_effect = Exception("Database error")
        
        # Delete the YubiKeySalt
        result = self.mock_salt.delete()
        
        # Verify the deletion failed
        self.assertFalse(result)
    
    @patch('models.yubikey_salt.YubiKeySalt.update')
    def test_update_last_used(self, mock_update):
        """Test updating a YubiKeySalt's last used time."""
        # Mock the update method
        mock_update.return_value = True
        
        # Store the original last_used value
        original_last_used = self.mock_salt.last_used
        
        # Update the last used time
        result = self.mock_salt.update_last_used()
        
        # Verify the update was successful
        self.assertTrue(result)
        self.assertNotEqual(self.mock_salt.last_used, original_last_used)
        mock_update.assert_called_once()
    
    def test_to_dict(self):
        """Test converting a YubiKeySalt to a dictionary."""
        # Convert the YubiKeySalt to a dictionary
        salt_dict = self.mock_salt.to_dict()
        
        # Verify the dictionary
        self.assertEqual(salt_dict["salt_id"], self.salt_id)
        self.assertEqual(salt_dict["credential_id"], self.credential_id)
        self.assertEqual(salt_dict["salt"], self.salt.hex())
        self.assertEqual(salt_dict["purpose"], self.purpose)


if __name__ == "__main__":
    unittest.main() 
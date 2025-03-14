"""
Unit tests for the Seed model.
"""
import unittest
from unittest.mock import patch
import uuid
from datetime import datetime

from models.seed import Seed
from models.user import User


class TestSeed(unittest.TestCase):
    """Test cases for the Seed model."""
    
    def setUp(self):
        """Set up test cases."""
        # Create a sample user and seed data
        self.user_id = str(uuid.uuid4())
        self.seed_id = str(uuid.uuid4())
        self.encrypted_seed = b"encrypted_seed_data"
        self.metadata = {"label": "Test Seed", "type": "BIP39"}
        
        # Mock objects
        self.mock_seed = Seed(
            seed_id=self.seed_id,
            user_id=self.user_id,
            encrypted_seed=self.encrypted_seed,
            creation_date=datetime.now(),
            metadata=self.metadata
        )
        
    def test_init(self):
        """Test Seed initialization."""
        seed = Seed(
            seed_id=self.seed_id,
            user_id=self.user_id,
            encrypted_seed=self.encrypted_seed,
            metadata=self.metadata
        )
        
        self.assertEqual(seed.seed_id, self.seed_id)
        self.assertEqual(seed.user_id, self.user_id)
        self.assertEqual(seed.encrypted_seed, self.encrypted_seed)
        self.assertIsInstance(seed.creation_date, datetime)
        self.assertEqual(seed.metadata, self.metadata)
    
    def test_init_default_values(self):
        """Test Seed initialization with default values."""
        seed = Seed()
        
        self.assertIsNotNone(seed.seed_id)
        self.assertIsNone(seed.user_id)
        self.assertIsNone(seed.encrypted_seed)
        self.assertIsInstance(seed.creation_date, datetime)
        self.assertEqual(seed.metadata, {})
    
    @patch('models.database.DatabaseManager.execute_query')
    @patch('models.user.User.get_by_id')
    def test_create_success(self, mock_get_user, mock_execute_query):
        """Test creating a seed successfully."""
        # Mock user exists
        mock_get_user.return_value = User(user_id=self.user_id)
        # Mock database operation
        mock_execute_query.return_value = None
        
        seed = Seed.create(
            user_id=self.user_id,
            encrypted_seed=self.encrypted_seed,
            metadata=self.metadata
        )
        
        self.assertIsNotNone(seed)
        self.assertEqual(seed.user_id, self.user_id)
        self.assertEqual(seed.encrypted_seed, self.encrypted_seed)
        self.assertEqual(seed.metadata, self.metadata)
        
        # Verify DB was called with correct parameters
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("INSERT INTO seeds", args[0])
        self.assertEqual(len(args[1]), 4)  # 4 parameters for the query
        
    @patch('models.database.DatabaseManager.execute_query')
    @patch('models.user.User.get_by_id')
    def test_create_user_not_found(self, mock_get_user, mock_execute_query):
        """Test creating a seed with a non-existent user."""
        # Mock user does not exist
        mock_get_user.return_value = None
        
        seed = Seed.create(
            user_id=self.user_id,
            encrypted_seed=self.encrypted_seed,
            metadata=self.metadata
        )
        
        self.assertIsNone(seed)
        # Verify DB was not called
        mock_execute_query.assert_not_called()
        
    @patch('models.database.DatabaseManager.execute_query')
    def test_create_exception(self, mock_execute_query):
        """Test exception during seed creation."""
        # Mock database operation raising an exception
        mock_execute_query.side_effect = Exception("Database error")
        
        # Patch User.get_by_id to return a user so we get past that check
        with patch('models.user.User.get_by_id') as mock_get_user:
            mock_get_user.return_value = User(user_id=self.user_id)
            
            seed = Seed.create(
                user_id=self.user_id,
                encrypted_seed=self.encrypted_seed,
                metadata=self.metadata
            )
            
            self.assertIsNone(seed)
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_get_by_id_found(self, mock_execute_query):
        """Test retrieving a seed by ID when it exists."""
        # Mock database row
        mock_row = {
            "seed_id": self.seed_id,
            "user_id": self.user_id,
            "encrypted_seed": self.encrypted_seed,
            "creation_date": datetime.now(),
            "last_accessed": None,
            "metadata": '{"label": "Test Seed", "type": "BIP39"}'
        }
        
        # Mock cursor
        mock_cursor = unittest.mock.MagicMock()
        mock_cursor.fetchone.return_value = mock_row
        mock_execute_query.return_value = mock_cursor
        
        seed = Seed.get_by_id(self.seed_id)
        
        self.assertIsNotNone(seed)
        self.assertEqual(seed.seed_id, self.seed_id)
        self.assertEqual(seed.user_id, self.user_id)
        self.assertEqual(seed.encrypted_seed, self.encrypted_seed)
        self.assertEqual(seed.metadata, self.metadata)
        
        # Verify DB was called with correct parameters
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("SELECT * FROM seeds WHERE seed_id = ?", args[0])
        self.assertEqual(args[1], (self.seed_id,))
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_get_by_id_not_found(self, mock_execute_query):
        """Test retrieving a seed by ID when it doesn't exist."""
        # Mock cursor with no results
        mock_cursor = unittest.mock.MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_execute_query.return_value = mock_cursor
        
        seed = Seed.get_by_id(self.seed_id)
        
        self.assertIsNone(seed)
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_get_by_user_id(self, mock_execute_query):
        """Test retrieving seeds by user ID."""
        # Mock database rows
        mock_rows = [
            {
                "seed_id": self.seed_id,
                "user_id": self.user_id,
                "encrypted_seed": self.encrypted_seed,
                "creation_date": datetime.now(),
                "last_accessed": None,
                "metadata": '{"label": "Test Seed", "type": "BIP39"}'
            },
            {
                "seed_id": str(uuid.uuid4()),
                "user_id": self.user_id,
                "encrypted_seed": b"another_encrypted_seed",
                "creation_date": datetime.now(),
                "last_accessed": None,
                "metadata": '{"label": "Another Seed", "type": "BIP39"}'
            }
        ]
        
        # Mock cursor
        mock_cursor = unittest.mock.MagicMock()
        mock_cursor.fetchall.return_value = mock_rows
        mock_execute_query.return_value = mock_cursor
        
        seeds = Seed.get_by_user_id(self.user_id)
        
        self.assertEqual(len(seeds), 2)
        self.assertEqual(seeds[0].user_id, self.user_id)
        self.assertEqual(seeds[1].user_id, self.user_id)
        
        # Verify DB was called with correct parameters
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("SELECT * FROM seeds WHERE user_id = ?", args[0])
        self.assertEqual(args[1], (self.user_id,))
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_update_success(self, mock_execute_query):
        """Test updating a seed successfully."""
        # Mock database operation
        mock_execute_query.return_value = None
        
        result = self.mock_seed.update()
        
        self.assertTrue(result)
        
        # Verify DB was called with correct parameters
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("UPDATE seeds", args[0])
        self.assertEqual(len(args[1]), 4)  # 4 parameters for the query
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_update_exception(self, mock_execute_query):
        """Test exception during seed update."""
        # Mock database operation raising an exception
        mock_execute_query.side_effect = Exception("Database error")
        
        result = self.mock_seed.update()
        
        self.assertFalse(result)
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_delete_success(self, mock_execute_query):
        """Test deleting a seed successfully."""
        # Mock database operation
        mock_execute_query.return_value = None
        
        result = self.mock_seed.delete()
        
        self.assertTrue(result)
        
        # Verify DB was called with correct parameters
        mock_execute_query.assert_called_once()
        args = mock_execute_query.call_args[0]
        self.assertIn("DELETE FROM seeds WHERE seed_id = ?", args[0])
        self.assertEqual(args[1], (self.seed_id,))
    
    @patch('models.database.DatabaseManager.execute_query')
    def test_delete_exception(self, mock_execute_query):
        """Test exception during seed deletion."""
        # Mock database operation raising an exception
        mock_execute_query.side_effect = Exception("Database error")
        
        result = self.mock_seed.delete()
        
        self.assertFalse(result)
    
    @patch('models.seed.Seed.update')
    def test_update_last_accessed(self, mock_update):
        """Test updating a seed's last accessed time."""
        # Mock the update method
        mock_update.return_value = True
        
        # Store the original last_accessed value
        original_last_accessed = self.mock_seed.last_accessed
        
        result = self.mock_seed.update_last_accessed()
        
        self.assertTrue(result)
        self.assertNotEqual(self.mock_seed.last_accessed, original_last_accessed)
        mock_update.assert_called_once()
    
    @patch('models.seed.Seed.update')
    def test_update_metadata(self, mock_update):
        """Test updating a seed's metadata."""
        # Mock the update method
        mock_update.return_value = True
        
        new_metadata = {"label": "Updated Seed", "type": "BIP39", "tags": ["important"]}
        
        result = self.mock_seed.update_metadata(new_metadata)
        
        self.assertTrue(result)
        self.assertEqual(self.mock_seed.metadata, new_metadata)
        mock_update.assert_called_once()
    
    def test_to_dict(self):
        """Test converting a seed to a dictionary."""
        seed_dict = self.mock_seed.to_dict()
        
        self.assertEqual(seed_dict["seed_id"], self.seed_id)
        self.assertEqual(seed_dict["user_id"], self.user_id)
        self.assertEqual(seed_dict["encrypted_seed"], self.encrypted_seed.hex())
        self.assertEqual(seed_dict["metadata"], self.metadata)


if __name__ == '__main__':
    unittest.main() 
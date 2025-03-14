"""
Unit tests for seed routes.
"""
import unittest
import json
import os
import tempfile
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.append(str(Path(__file__).parent.parent))

# Import application modules
from app import create_app
from models.user import User
from models.seed import Seed


class TestSeedRoutes(unittest.TestCase):
    """Test cases for seed routes."""
    
    def setUp(self):
        """Set up test cases."""
        # Create a test client
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        
        # Create a test database in memory
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app.config["DATABASE"] = self.db_path
        
        # Mock user authentication
        self.user_id = "test_user_id"
        self.username = "testuser"
        
        # Create a mock user for testing
        with patch("models.user.User.get_by_id") as mock_get_user:
            mock_user = MagicMock()
            mock_user.user_id = self.user_id
            mock_user.username = self.username
            mock_get_user.return_value = mock_user
            
            # Mock Flask g.user
            with patch("flask.g") as mock_g:
                mock_g.user = mock_user
                
                # Mock the login_required decorator
                with patch("services.auth_service.login_required", lambda f: f):
                    # We're ready for testing
                    pass
    
    def tearDown(self):
        """Clean up after tests."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    @patch("models.seed.Seed.create")
    @patch("services.crypto_service.encrypt_seed")
    def test_create_seed(self, mock_encrypt, mock_create):
        """Test creating a seed."""
        # Mock encryption
        mock_encrypt.return_value = b"encrypted_seed_data"
        
        # Mock seed creation
        mock_seed = MagicMock()
        mock_seed.to_dict.return_value = {
            "seed_id": "test_seed_id",
            "user_id": self.user_id,
            "encrypted_seed": "encrypted_seed_data_hex",
            "creation_date": "2023-01-01T00:00:00",
            "metadata": {"label": "Test Seed"}
        }
        mock_create.return_value = mock_seed
        
        # Make the request
        response = self.client.post(
            "/api/v1/seeds",
            json={
                "seed_phrase": "test test test test test test test test test test test test",
                "metadata": {
                    "label": "Test Seed"
                }
            }
        )
        
        # Check the response
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        
        # Verify the response data
        self.assertEqual(data["seed_id"], "test_seed_id")
        self.assertEqual(data["user_id"], self.user_id)
        self.assertEqual(data["metadata"]["label"], "Test Seed")
        
        # Verify the mock calls
        mock_encrypt.assert_called_once_with(
            "test test test test test test test test test test test test"
        )
        mock_create.assert_called_once_with(
            user_id=self.user_id,
            encrypted_seed=b"encrypted_seed_data",
            metadata={"label": "Test Seed"}
        )
    
    @patch("models.seed.Seed.get_by_user_id")
    def test_get_seeds(self, mock_get_seeds):
        """Test getting all seeds for a user."""
        # Mock seeds
        mock_seed1 = MagicMock()
        mock_seed1.to_dict.return_value = {
            "seed_id": "test_seed_id_1",
            "user_id": self.user_id,
            "encrypted_seed": "encrypted_seed_data_hex_1",
            "creation_date": "2023-01-01T00:00:00",
            "metadata": {"label": "Test Seed 1"}
        }
        
        mock_seed2 = MagicMock()
        mock_seed2.to_dict.return_value = {
            "seed_id": "test_seed_id_2",
            "user_id": self.user_id,
            "encrypted_seed": "encrypted_seed_data_hex_2",
            "creation_date": "2023-01-02T00:00:00",
            "metadata": {"label": "Test Seed 2"}
        }
        
        mock_get_seeds.return_value = [mock_seed1, mock_seed2]
        
        # Make the request
        response = self.client.get("/api/v1/seeds")
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify the response data
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["seed_id"], "test_seed_id_1")
        self.assertEqual(data[1]["seed_id"], "test_seed_id_2")
        
        # Verify the mock calls
        mock_get_seeds.assert_called_once_with(self.user_id)
    
    @patch("models.seed.Seed.get_by_id")
    def test_get_seed(self, mock_get_seed):
        """Test getting a specific seed."""
        # Mock seed
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = self.user_id
        mock_seed.to_dict.return_value = {
            "seed_id": "test_seed_id",
            "user_id": self.user_id,
            "encrypted_seed": "encrypted_seed_data_hex",
            "creation_date": "2023-01-01T00:00:00",
            "metadata": {"label": "Test Seed"}
        }
        mock_get_seed.return_value = mock_seed
        
        # Make the request
        response = self.client.get("/api/v1/seeds/test_seed_id")
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify the response data
        self.assertEqual(data["seed_id"], "test_seed_id")
        self.assertEqual(data["user_id"], self.user_id)
        
        # Verify the mock calls
        mock_get_seed.assert_called_once_with("test_seed_id")
        mock_seed.update_last_accessed.assert_called_once()
    
    @patch("models.seed.Seed.get_by_id")
    @patch("services.crypto_service.decrypt_seed")
    def test_decrypt_seed(self, mock_decrypt, mock_get_seed):
        """Test decrypting a seed."""
        # Mock seed
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = self.user_id
        mock_seed.encrypted_seed = b"encrypted_seed_data"
        mock_get_seed.return_value = mock_seed
        
        # Mock decryption
        mock_decrypt.return_value = "test test test test test test test test test test test test"
        
        # Make the request
        response = self.client.post("/api/v1/seeds/test_seed_id/decrypt")
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify the response data
        self.assertEqual(data["seed_phrase"], "test test test test test test test test test test test test")
        
        # Verify the mock calls
        mock_get_seed.assert_called_once_with("test_seed_id")
        mock_decrypt.assert_called_once_with(b"encrypted_seed_data")
        mock_seed.update_last_accessed.assert_called_once()
    
    @patch("models.seed.Seed.get_by_id")
    def test_get_seed_not_found(self, mock_get_seed):
        """Test getting a seed that doesn't exist."""
        # Mock seed not found
        mock_get_seed.return_value = None
        
        # Make the request
        response = self.client.get("/api/v1/seeds/nonexistent_seed_id")
        
        # Check the response
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Seed not found")
    
    @patch("models.seed.Seed.get_by_id")
    def test_get_seed_unauthorized(self, mock_get_seed):
        """Test getting a seed that belongs to another user."""
        # Mock seed belonging to another user
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = "another_user_id"
        mock_get_seed.return_value = mock_seed
        
        # Make the request
        response = self.client.get("/api/v1/seeds/test_seed_id")
        
        # Check the response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "You are not authorized to access this seed")
    
    @patch("models.seed.Seed.get_by_id")
    @patch("services.crypto_service.encrypt_seed")
    def test_update_seed(self, mock_encrypt, mock_get_seed):
        """Test updating a seed."""
        # Mock seed
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = self.user_id
        mock_seed.update.return_value = True
        mock_seed.to_dict.return_value = {
            "seed_id": "test_seed_id",
            "user_id": self.user_id,
            "encrypted_seed": "new_encrypted_seed_data_hex",
            "creation_date": "2023-01-01T00:00:00",
            "metadata": {"label": "Updated Seed"}
        }
        mock_get_seed.return_value = mock_seed
        
        # Mock encryption
        mock_encrypt.return_value = b"new_encrypted_seed_data"
        
        # Make the request
        response = self.client.put(
            "/api/v1/seeds/test_seed_id",
            json={
                "seed_phrase": "new test test test test test test test test test test test",
                "metadata": {
                    "label": "Updated Seed"
                }
            }
        )
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify the response data
        self.assertEqual(data["seed_id"], "test_seed_id")
        self.assertEqual(data["metadata"]["label"], "Updated Seed")
        
        # Verify the mock calls
        mock_get_seed.assert_called_once_with("test_seed_id")
        mock_encrypt.assert_called_once_with("new test test test test test test test test test test test")
        self.assertEqual(mock_seed.encrypted_seed, b"new_encrypted_seed_data")
        mock_seed.update_metadata.assert_called_once_with({"label": "Updated Seed"})
        mock_seed.update.assert_called_once()
    
    @patch("models.seed.Seed.get_by_id")
    def test_delete_seed(self, mock_get_seed):
        """Test deleting a seed."""
        # Mock seed
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = self.user_id
        mock_seed.delete.return_value = True
        mock_get_seed.return_value = mock_seed
        
        # Make the request
        response = self.client.delete("/api/v1/seeds/test_seed_id")
        
        # Check the response
        self.assertEqual(response.status_code, 204)
        
        # Verify the mock calls
        mock_get_seed.assert_called_once_with("test_seed_id")
        mock_seed.delete.assert_called_once()
    
    @patch("models.seed.Seed.get_by_id")
    def test_delete_seed_failure(self, mock_get_seed):
        """Test failing to delete a seed."""
        # Mock seed with delete failure
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = self.user_id
        mock_seed.delete.return_value = False
        mock_get_seed.return_value = mock_seed
        
        # Make the request
        response = self.client.delete("/api/v1/seeds/test_seed_id")
        
        # Check the response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Failed to delete seed")


if __name__ == "__main__":
    unittest.main() 
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
from services.auth_service import generate_token


class TestSeedRoutes(unittest.TestCase):
    """Test cases for seed routes."""
    
    def setUp(self):
        """Set up test cases."""
        # Create a test client
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["TESTING_AUTH_BYPASS"] = True
        
        # Create a test database in memory
        self.db_fd, self.db_path = tempfile.mkstemp()
        self.app.config["DATABASE"] = self.db_path
        
        # Mock user authentication
        self.user_id = "test_user_id"
        self.username = "testuser"
        self.app.config["TESTING_AUTH_USER_ID"] = self.user_id
        
        # Create a mock user for testing
        self.mock_user = MagicMock()
        self.mock_user.user_id = self.user_id
        self.mock_user.username = self.username
        
        # Generate a valid token for the test user
        self.token = generate_token(self.user_id)
        
        # Create test client
        self.client = self.app.test_client()
        
        # Mock User.get_by_id to return our mock user
        self.user_get_by_id_patcher = patch('models.user.User.get_by_id')
        self.mock_user_get_by_id = self.user_get_by_id_patcher.start()
        self.mock_user_get_by_id.return_value = self.mock_user
        
        # Store headers for use in requests
        self.headers = {'Authorization': f'Bearer {self.token}'}
        
        # Set up the application context
        self.ctx = self.app.app_context()
        self.ctx.push()
        
        # Mock the user in the application context
        with patch("flask.g") as mock_g:
            mock_g.user = self.mock_user
    
    def tearDown(self):
        """Clean up after test cases."""
        # Stop the User.get_by_id patcher
        self.user_get_by_id_patcher.stop()
        
        self.ctx.pop()  # Remove the application context
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    @patch("models.seed.Seed.create")
    @patch("routes.seed_routes.encrypt_seed")
    @patch("routes.seed_routes.decrypt_seed")
    def test_create_seed(self, mock_decrypt, mock_encrypt, mock_create):
        """Test creating a seed."""
        # Mock encryption
        encrypted_data = {
            "version": 1,
            "algorithm": "AES-256-GCM",
            "nonce": "base64_encoded_nonce",
            "ciphertext": "base64_encoded_ciphertext",
            "salt": "base64_encoded_salt"
        }
        mock_encrypt.return_value = json.dumps(encrypted_data).encode("utf-8")
        
        # Mock seed creation
        mock_seed = MagicMock()
        mock_seed.to_dict.return_value = {
            "seed_id": "test_seed_id",
            "user_id": self.user_id,
            "encrypted_seed": json.dumps(encrypted_data),
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
            },
            headers=self.headers
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
            encrypted_seed=json.dumps(encrypted_data).encode("utf-8"),
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
        response = self.client.get("/api/v1/seeds", headers=self.headers)
        
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
        response = self.client.get(f"/api/v1/seeds/{mock_seed.seed_id}", headers=self.headers)
        
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
    @patch("routes.seed_routes.decrypt_seed")
    @patch("routes.seed_routes.encrypt_seed")
    def test_decrypt_seed(self, mock_encrypt, mock_decrypt, mock_get_seed):
        """Test decrypting a seed."""
        # Create encrypted data
        encrypted_data = {
            "version": 1,
            "algorithm": "AES-256-GCM",
            "nonce": "base64_encoded_nonce",
            "ciphertext": "base64_encoded_ciphertext",
            "salt": "base64_encoded_salt"
        }
        
        # Mock seed
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = self.user_id
        mock_seed.encrypted_seed = json.dumps(encrypted_data).encode("utf-8")
        mock_get_seed.return_value = mock_seed
        
        # Mock decryption
        mock_decrypt.return_value = "test test test test test test test test test test test test"
        
        # Make the request
        response = self.client.post(f"/api/v1/seeds/{mock_seed.seed_id}/decrypt", headers=self.headers)
        
        # Check the response
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        # Verify the response data
        self.assertEqual(data["seed_phrase"], "test test test test test test test test test test test test")
        
        # Verify the mock calls
        mock_decrypt.assert_called_once_with(json.dumps(encrypted_data).encode("utf-8"))
        mock_get_seed.assert_called_once_with("test_seed_id")
        mock_seed.update_last_accessed.assert_called_once()
    
    @patch("models.seed.Seed.get_by_id")
    def test_get_seed_not_found(self, mock_get_seed):
        """Test getting a seed that doesn't exist."""
        # Mock seed not found
        mock_get_seed.return_value = None
        
        # Make the request
        response = self.client.get("/api/v1/seeds/nonexistent_seed_id", headers=self.headers)
        
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
        response = self.client.get("/api/v1/seeds/test_seed_id", headers=self.headers)
        
        # Check the response
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "You are not authorized to access this seed")
    
    @patch("models.seed.Seed.get_by_id")
    @patch("routes.seed_routes.encrypt_seed")
    @patch("routes.seed_routes.decrypt_seed")
    def test_update_seed(self, mock_decrypt, mock_encrypt, mock_get_seed):
        """Test updating a seed."""
        # Create encrypted data
        encrypted_data = {
            "version": 1,
            "algorithm": "AES-256-GCM",
            "nonce": "base64_encoded_nonce",
            "ciphertext": "base64_encoded_ciphertext",
            "salt": "base64_encoded_salt"
        }
        
        # Create new encrypted data
        new_encrypted_data = {
            "version": 1,
            "algorithm": "AES-256-GCM",
            "nonce": "new_base64_encoded_nonce",
            "ciphertext": "new_base64_encoded_ciphertext",
            "salt": "new_base64_encoded_salt"
        }
        
        # Mock seed
        mock_seed = MagicMock()
        mock_seed.seed_id = "test_seed_id"
        mock_seed.user_id = self.user_id
        mock_seed.encrypted_seed = json.dumps(encrypted_data).encode("utf-8")
        mock_seed.update.return_value = True
        mock_seed.to_dict.return_value = {
            "seed_id": "test_seed_id",
            "user_id": self.user_id,
            "encrypted_seed": json.dumps(new_encrypted_data),
            "creation_date": "2023-01-01T00:00:00",
            "metadata": {"label": "Updated Seed"}
        }
        mock_get_seed.return_value = mock_seed
        
        # Mock encryption
        mock_encrypt.return_value = json.dumps(new_encrypted_data).encode("utf-8")
        
        # Make the request
        response = self.client.put(
            f"/api/v1/seeds/{mock_seed.seed_id}",
            json={
                "seed_phrase": "new test test test test test test test test test test test",
                "metadata": {
                    "label": "Updated Seed"
                }
            },
            headers=self.headers
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
        
        # Verify that the encrypted_seed attribute was set correctly
        self.assertEqual(mock_seed.encrypted_seed, json.dumps(new_encrypted_data).encode("utf-8"))
        
        # Verify that update_metadata was called with the correct metadata
        mock_seed.update_metadata.assert_called_once_with({"label": "Updated Seed"})
        
        # Verify that update was called (without parameters)
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
        response = self.client.delete(f"/api/v1/seeds/{mock_seed.seed_id}", headers=self.headers)
        
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
        response = self.client.delete("/api/v1/seeds/test_seed_id", headers=self.headers)
        
        # Check the response
        self.assertEqual(response.status_code, 500)
        data = json.loads(response.data)
        self.assertEqual(data["error"], "Failed to delete seed")


if __name__ == "__main__":
    unittest.main() 
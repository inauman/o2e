"""
Unit tests for the DatabaseManager class.
"""
import os
import unittest
import tempfile
import sqlite3
import threading
from pathlib import Path

from models.database import DatabaseManager


class TestDatabaseManager(unittest.TestCase):
    """Test cases for the DatabaseManager class."""
    
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
        
    def tearDown(self):
        """Clean up after each test."""
        # Close all connections
        if hasattr(self, 'db_manager'):
            self.db_manager.close_all_connections()
        
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_singleton_pattern(self):
        """Test that DatabaseManager implements the singleton pattern."""
        # Create a second instance with the same path
        db_manager2 = DatabaseManager(db_path=self.db_path)
        
        # Check that both instances are the same object
        self.assertIs(self.db_manager, db_manager2)
        
        # Check that the path is the same
        self.assertEqual(self.db_manager.db_path, db_manager2.db_path)
    
    def test_initialize_schema(self):
        """Test that the schema can be initialized correctly."""
        # Initialize the schema
        result = self.db_manager.initialize_schema()
        
        # Check that the schema was created
        self.assertTrue(result)
        
        # Check that the tables exist
        self.assertTrue(self.db_manager.table_exists("users"))
        self.assertTrue(self.db_manager.table_exists("yubikeys"))
        self.assertTrue(self.db_manager.table_exists("seeds"))
        self.assertTrue(self.db_manager.table_exists("wrapped_keys"))
        self.assertTrue(self.db_manager.table_exists("challenges"))
        
        # Try to initialize again - should return False
        result = self.db_manager.initialize_schema()
        self.assertFalse(result)
    
    def test_execute_query(self):
        """Test executing a simple query."""
        # Initialize the schema
        self.db_manager.initialize_schema()
        
        # Insert a test user
        user_id = "test_user_id"
        username = "test_user"
        
        cursor = self.db_manager.execute_query(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
            commit=True
        )
        
        # Check that one row was affected
        self.assertEqual(cursor.rowcount, 1)
        
        # Query the user
        cursor = self.db_manager.execute_query(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        # Fetch the result
        row = cursor.fetchone()
        
        # Check the result
        self.assertIsNotNone(row)
        self.assertEqual(row["user_id"], user_id)
        self.assertEqual(row["username"], username)
    
    def test_execute_transaction(self):
        """Test executing a transaction with multiple queries."""
        # Initialize the schema
        self.db_manager.initialize_schema()
        
        # Create test data
        user_id = "test_user_id"
        username = "test_user"
        credential_id = "test_credential_id"
        public_key = b"test_public_key"
        
        # Create a transaction with multiple queries
        queries = [
            (
                "INSERT INTO users (user_id, username) VALUES (?, ?)",
                (user_id, username)
            ),
            (
                "INSERT INTO yubikeys (credential_id, user_id, public_key) VALUES (?, ?, ?)",
                (credential_id, user_id, public_key)
            )
        ]
        
        # Execute the transaction
        result = self.db_manager.execute_transaction(queries)
        
        # Check that the transaction succeeded
        self.assertTrue(result)
        
        # Query the user
        cursor = self.db_manager.execute_query(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        # Fetch the result
        user_row = cursor.fetchone()
        
        # Check the user result
        self.assertIsNotNone(user_row)
        self.assertEqual(user_row["user_id"], user_id)
        self.assertEqual(user_row["username"], username)
        
        # Query the yubikey
        cursor = self.db_manager.execute_query(
            "SELECT * FROM yubikeys WHERE credential_id = ?",
            (credential_id,)
        )
        
        # Fetch the result
        yubikey_row = cursor.fetchone()
        
        # Check the yubikey result
        self.assertIsNotNone(yubikey_row)
        self.assertEqual(yubikey_row["credential_id"], credential_id)
        self.assertEqual(yubikey_row["user_id"], user_id)
        self.assertEqual(bytes(yubikey_row["public_key"]), public_key)
    
    def test_failed_transaction(self):
        """Test that a transaction is rolled back on failure."""
        # Initialize the schema
        self.db_manager.initialize_schema()
        
        # Create test data
        user_id = "test_user_id"
        username = "test_user"
        
        # First, insert a user normally
        self.db_manager.execute_query(
            "INSERT INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username),
            commit=True
        )
        
        # Now try to insert the same user again (should fail due to PRIMARY KEY constraint)
        # and also try to insert a yubikey (which should be rolled back)
        queries = [
            (
                "INSERT INTO users (user_id, username) VALUES (?, ?)",
                (user_id, "another_username")  # Same user_id, different username
            ),
            (
                "INSERT INTO yubikeys (credential_id, user_id, public_key) VALUES (?, ?, ?)",
                ("test_credential_id", user_id, b"test_public_key")
            )
        ]
        
        # Execute the transaction (should fail)
        result = self.db_manager.execute_transaction(queries)
        
        # Check that the transaction failed
        self.assertFalse(result)
        
        # Check that the yubikey was not inserted
        cursor = self.db_manager.execute_query(
            "SELECT COUNT(*) as count FROM yubikeys WHERE user_id = ?",
            (user_id,)
        )
        
        # Fetch the result
        row = cursor.fetchone()
        
        # Check that no yubikeys were inserted
        self.assertEqual(row["count"], 0)
    
    def test_connection_pooling(self):
        """Test that connections are properly pooled per thread."""
        # Initialize the schema
        self.db_manager.initialize_schema()
        
        # Store the main thread's connection
        main_conn = self.db_manager.get_connection()
        
        # Connection IDs to be set by threads
        thread_connections = {}
        
        def thread_func(thread_id):
            """Function to run in each thread."""
            # Get a connection in this thread
            conn = self.db_manager.get_connection()
            
            # Store the connection object's ID
            thread_connections[thread_id] = id(conn)
        
        # Create and start threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=thread_func, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that each thread got a different connection
        unique_conn_ids = set(thread_connections.values())
        self.assertEqual(len(unique_conn_ids), 3)
        
        # Check that the main thread's connection is different from the thread connections
        self.assertNotIn(id(main_conn), unique_conn_ids)


if __name__ == "__main__":
    unittest.main() 
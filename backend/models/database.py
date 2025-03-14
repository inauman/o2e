"""
Database connection manager for SQLite database.
"""
import os
import sqlite3
import threading
import typing as t
from datetime import datetime, timezone
from pathlib import Path


def adapt_datetime(dt: datetime) -> str:
    """Convert datetime to ISO format string for SQLite storage."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def convert_datetime(val: bytes) -> datetime:
    """Convert SQLite timestamp string to datetime object."""
    if val is None:
        return None
    try:
        dt = datetime.fromisoformat(val.decode())
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None


class DatabaseManager:
    """
    Manages SQLite database connections and operations.
    
    This class is responsible for:
    - Creating and maintaining database connections
    - Connection pooling
    - Transaction management
    - Database schema initialization
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Implement singleton pattern for database manager."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DatabaseManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self, db_path: str = "data/yubikey_storage.db", create_if_missing: bool = True):
        """
        Initialize the database manager with optional path.
        
        Args:
            db_path: Path to the SQLite database file
            create_if_missing: Whether to create the database if it doesn't exist
        """
        # Skip initialization if already initialized (singleton pattern)
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        self.db_path = os.path.abspath(db_path)
        self._create_if_missing = create_if_missing
        self._connection_pool = {}  # Thread-local connections
        self._initialized = True
        
        # Register adapters and converters for timestamps
        sqlite3.register_adapter(datetime, adapt_datetime)
        sqlite3.register_converter("TIMESTAMP", convert_datetime)
        
        # Create directory if it doesn't exist
        if create_if_missing:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection for the current thread.
        
        Returns:
            A SQLite connection object
        """
        # Get current thread ID
        thread_id = threading.get_ident()
        
        # Check if connection exists for this thread
        if thread_id not in self._connection_pool:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
            
            # Create a new connection with timestamp handling
            conn = sqlite3.connect(
                self.db_path,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
                check_same_thread=False  # We'll manage thread safety ourselves
            )
            conn.row_factory = sqlite3.Row  # Use row factory for dictionary-like rows
            
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
            # Store in connection pool
            self._connection_pool[thread_id] = conn
        
        return self._connection_pool[thread_id]
    
    def close_all_connections(self):
        """Close all database connections in the pool."""
        with self._lock:
            for conn in self._connection_pool.values():
                conn.close()
            self._connection_pool.clear()
    
    def close_current_connection(self):
        """Close the connection for the current thread."""
        thread_id = threading.get_ident()
        if thread_id in self._connection_pool:
            self._connection_pool[thread_id].close()
            del self._connection_pool[thread_id]
    
    def initialize_schema(self) -> bool:
        """
        Initialize the database schema if it doesn't exist.
        
        Returns:
            True if schema was created, False if it already existed
        """
        # Check if tables already exist
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if users table exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        if cursor.fetchone() is not None:
            return False  # Schema already exists
        
        # Create schema
        with conn:  # Auto-commits
            # Users table
            conn.execute('''
            CREATE TABLE users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                max_yubikeys INTEGER DEFAULT 5
            )
            ''')
            
            # YubiKeys table
            conn.execute('''
            CREATE TABLE yubikeys (
                credential_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                public_key BLOB NOT NULL,
                aaguid TEXT,
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                nickname TEXT,
                sign_count INTEGER DEFAULT 0,
                is_primary BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            # YubiKey Salts table
            conn.execute('''
            CREATE TABLE yubikey_salts (
                salt_id TEXT PRIMARY KEY,
                credential_id TEXT NOT NULL,
                salt BLOB NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                purpose TEXT DEFAULT 'seed_encryption',
                FOREIGN KEY (credential_id) REFERENCES yubikeys(credential_id) ON DELETE CASCADE
            )
            ''')
            
            # Seeds table
            conn.execute('''
            CREATE TABLE seeds (
                seed_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                encrypted_seed BLOB NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            # Wrapped keys table
            conn.execute('''
            CREATE TABLE wrapped_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                credential_id TEXT NOT NULL,
                seed_id TEXT NOT NULL,
                wrapped_key BLOB NOT NULL,
                salt BLOB NOT NULL,
                key_wrapping_algorithm TEXT DEFAULT 'HKDF-SHA256+AES-256-GCM',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (credential_id) REFERENCES yubikeys(credential_id) ON DELETE CASCADE,
                FOREIGN KEY (seed_id) REFERENCES seeds(seed_id) ON DELETE CASCADE
            )
            ''')
            
            # Challenges table
            conn.execute('''
            CREATE TABLE challenges (
                user_id TEXT NOT NULL,
                challenge BLOB NOT NULL,
                creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expiry_date TIMESTAMP,
                PRIMARY KEY (user_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
        
        return True
    
    def execute_query(self, query: str, params: t.Tuple = (), commit: bool = False) -> sqlite3.Cursor:
        """
        Execute a SQL query with parameters.
        
        Args:
            query: SQL query to execute
            params: Parameters for the query
            commit: Whether to commit the transaction
            
        Returns:
            SQLite cursor object
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            
        return cursor
    
    def execute_transaction(self, queries: t.List[t.Tuple[str, t.Tuple]]) -> bool:
        """
        Execute multiple queries as a single transaction.
        
        Args:
            queries: List of (query, params) tuples
            
        Returns:
            True if transaction succeeded, False otherwise
        """
        conn = self.get_connection()
        
        try:
            with conn:  # Auto-commits or rolls back on exception
                for query, params in queries:
                    conn.execute(query, params)
            return True
        except Exception:
            # Transaction was automatically rolled back
            return False
            
    def table_exists(self, table_name: str) -> bool:
        """
        Check if a table exists in the database.
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            True if table exists, False otherwise
        """
        cursor = self.execute_query(
            "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
            (table_name,)
        )
        return cursor.fetchone() is not None

    def _initialize_database(self):
        """Initialize the database with tables if they don't exist."""
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            username TEXT UNIQUE,
            password_hash TEXT,
            email TEXT,
            full_name TEXT,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            role TEXT DEFAULT 'user',
            is_active INTEGER DEFAULT 1
        )
        """)
        
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS yubikeys (
            yubikey_id TEXT PRIMARY KEY,
            user_id TEXT,
            public_key BLOB,
            key_handle BLOB,
            credential_id TEXT,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            nickname TEXT,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        
        self.execute_query("""
        CREATE TABLE IF NOT EXISTS seeds (
            seed_id TEXT PRIMARY KEY,
            user_id TEXT,
            encrypted_seed BLOB,
            creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_accessed TIMESTAMP,
            metadata TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """) 
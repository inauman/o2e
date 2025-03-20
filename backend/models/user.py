"""
User model for the application.
"""
import uuid
import typing as t
from datetime import datetime, timezone

from models.database import DatabaseManager


class User:
    """
    User model representing a user in the application.
    
    Attributes:
        user_id (str): The unique identifier for the user
        email (str): The email address for the user
        created_at (datetime): When the user was created
        last_login (datetime): When the user last logged in
        max_yubikeys (int): The maximum number of YubiKeys allowed for this user
    """
    
    def __init__(
        self,
        user_id: str = None,
        email: str = None,
        created_at: datetime = None,
        last_login: datetime = None,
        max_yubikeys: int = 5
    ):
        """
        Initialize a new User instance.
        
        Args:
            user_id: The unique identifier for the user (auto-generated if None)
            email: The email address for the user
            created_at: When the user was created (auto-generated if None)
            last_login: When the user last logged in
            max_yubikeys: The maximum number of YubiKeys allowed for this user
        """
        self.user_id = user_id or str(uuid.uuid4())
        self.email = email
        self.created_at = created_at or datetime.now(timezone.utc)
        self.last_login = last_login
        self.max_yubikeys = max_yubikeys
    
    @classmethod
    def create(cls, email: str, max_yubikeys: int = 5) -> t.Optional['User']:
        """
        Create a new user in the database.
        
        Args:
            email: The email address for the new user
            max_yubikeys: The maximum number of YubiKeys allowed for this user
            
        Returns:
            A new User instance if successful, None otherwise
        """
        db = DatabaseManager()
        
        # Create a new User instance with UTC timestamp
        user = cls(
            email=email,
            max_yubikeys=max_yubikeys,
            created_at=datetime.now(timezone.utc)
        )
        
        try:
            # Insert the user into the database
            db.execute_query(
                """
                INSERT INTO users (
                    user_id, email, max_yubikeys, created_at
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user.user_id,
                    user.email,
                    user.max_yubikeys,
                    user.created_at
                ),
                commit=True
            )
            
            return user
        except Exception:
            # If an error occurred, return None
            return None
    
    @classmethod
    def get_by_id(cls, user_id: str) -> t.Optional['User']:
        """
        Get a user by their ID.
        
        Args:
            user_id: The ID of the user to get
            
        Returns:
            A User instance if found, None otherwise
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        # Convert row to dictionary
        user_dict = dict(row)
        
        # Create a User instance from the row data
        return cls(
            user_id=user_dict["user_id"],
            email=user_dict["email"],
            created_at=user_dict["created_at"],
            last_login=user_dict["last_login"],
            max_yubikeys=user_dict["max_yubikeys"]
        )
    
    @classmethod
    def get_by_email(cls, email: str) -> t.Optional['User']:
        """
        Get a user by their email address.
        
        Args:
            email: The email address of the user to get
            
        Returns:
            A User instance if found, None otherwise
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        # Convert row to dictionary
        user_dict = dict(row)
        
        # Create a User instance from the row data
        return cls(
            user_id=user_dict["user_id"],
            email=user_dict["email"],
            created_at=user_dict["created_at"],
            last_login=user_dict["last_login"],
            max_yubikeys=user_dict["max_yubikeys"]
        )
    
    @classmethod
    def get_all(cls) -> t.List['User']:
        """
        Get all users.
        
        Returns:
            A list of User instances
        """
        db = DatabaseManager()
        
        cursor = db.execute_query("SELECT * FROM users")
        
        users = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            user_dict = dict(row)
            
            # Create a User instance from the row data
            user = cls(
                user_id=user_dict["user_id"],
                email=user_dict["email"],
                created_at=user_dict["created_at"],
                last_login=user_dict["last_login"],
                max_yubikeys=user_dict["max_yubikeys"]
            )
            
            users.append(user)
        
        return users
    
    def update(self) -> bool:
        """
        Update the user in the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # Update the user in the database
            db.execute_query(
                """
                UPDATE users
                SET email = ?, last_login = ?, max_yubikeys = ?
                WHERE user_id = ?
                """,
                (self.email, self.last_login, self.max_yubikeys, self.user_id),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def delete(self) -> bool:
        """
        Delete the user from the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # Delete the user from the database
            db.execute_query(
                "DELETE FROM users WHERE user_id = ?",
                (self.user_id,),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def update_last_login(self) -> bool:
        """
        Update the user's last login time.
        
        Returns:
            True if successful, False otherwise
        """
        self.last_login = datetime.now(timezone.utc)
        return self.update()
    
    def count_yubikeys(self) -> int:
        """
        Count the number of YubiKeys registered to this user.
        
        Returns:
            The number of YubiKeys registered to this user
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT COUNT(*) FROM yubikeys WHERE user_id = ?",
            (self.user_id,)
        )
        
        return cursor.fetchone()[0]
    
    def can_register_yubikey(self) -> bool:
        """
        Check if the user can register another YubiKey.
        
        Returns:
            True if the user can register another YubiKey, False otherwise
        """
        return self.count_yubikeys() < self.max_yubikeys
    
    def to_dict(self) -> dict:
        """
        Convert the user to a dictionary.
        
        Returns:
            A dictionary representation of the user
        """
        return {
            "user_id": self.user_id,
            "email": self.email,
            "created_at": self.created_at,
            "last_login": self.last_login,
            "max_yubikeys": self.max_yubikeys,
            "yubikey_count": self.count_yubikeys()
        } 
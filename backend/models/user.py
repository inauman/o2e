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
        username (str): The username for the user
        creation_date (datetime): The date the user was created
        last_login (datetime): The date the user last logged in
        max_yubikeys (int): The maximum number of YubiKeys allowed for this user
    """
    
    def __init__(
        self,
        user_id: str = None,
        username: str = None,
        creation_date: datetime = None,
        last_login: datetime = None,
        max_yubikeys: int = 5
    ):
        """
        Initialize a new User instance.
        
        Args:
            user_id: The unique identifier for the user (auto-generated if None)
            username: The username for the user
            creation_date: The date the user was created (auto-generated if None)
            last_login: The date the user last logged in
            max_yubikeys: The maximum number of YubiKeys allowed for this user
        """
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.creation_date = creation_date or datetime.now(timezone.utc)
        self.last_login = last_login
        self.max_yubikeys = max_yubikeys
    
    @classmethod
    def create(cls, username: str, max_yubikeys: int = 5) -> t.Optional['User']:
        """
        Create a new user in the database.
        
        Args:
            username: The username for the new user
            max_yubikeys: The maximum number of YubiKeys allowed for this user
            
        Returns:
            A new User instance if successful, None otherwise
        """
        db = DatabaseManager()
        
        # Create a new User instance with UTC timestamp
        user = cls(
            username=username,
            max_yubikeys=max_yubikeys,
            creation_date=datetime.now(timezone.utc)
        )
        
        try:
            # Insert the user into the database
            db.execute_query(
                """
                INSERT INTO users (
                    user_id, username, max_yubikeys, creation_date
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    user.user_id,
                    user.username,
                    user.max_yubikeys,
                    user.creation_date
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
            username=user_dict["username"],
            creation_date=user_dict["creation_date"],
            last_login=user_dict["last_login"],
            max_yubikeys=user_dict["max_yubikeys"]
        )
    
    @classmethod
    def get_by_username(cls, username: str) -> t.Optional['User']:
        """
        Get a user by their username.
        
        Args:
            username: The username of the user to get
            
        Returns:
            A User instance if found, None otherwise
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        # Convert row to dictionary
        user_dict = dict(row)
        
        # Create a User instance from the row data
        return cls(
            user_id=user_dict["user_id"],
            username=user_dict["username"],
            creation_date=user_dict["creation_date"],
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
                username=user_dict["username"],
                creation_date=user_dict["creation_date"],
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
                SET username = ?, last_login = ?, max_yubikeys = ?
                WHERE user_id = ?
                """,
                (self.username, self.last_login, self.max_yubikeys, self.user_id),
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
            "SELECT COUNT(*) as count FROM yubikeys WHERE user_id = ?",
            (self.user_id,)
        )
        
        row = cursor.fetchone()
        return row["count"]
    
    def can_register_yubikey(self) -> bool:
        """
        Check if the user can register another YubiKey.
        
        Returns:
            True if the user can register another YubiKey, False otherwise
        """
        return self.count_yubikeys() < self.max_yubikeys
    
    def to_dict(self) -> dict:
        """
        Convert the User instance to a dictionary.
        
        Returns:
            A dictionary representation of the User
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "creation_date": self.creation_date,
            "last_login": self.last_login,
            "max_yubikeys": self.max_yubikeys
        } 
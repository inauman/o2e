"""
YubiKey Salt model for the application.
"""
import uuid
import typing as t
from datetime import datetime, timezone

from models.database import DatabaseManager


class YubiKeySalt:
    """
    YubiKeySalt model representing a unique salt for a YubiKey in the application.
    
    This is used with the FIDO2 hmac-secret extension to derive unique keys per YubiKey.
    
    Attributes:
        salt_id (str): The unique identifier for the salt
        credential_id (str): The credential ID of the YubiKey
        salt (bytes): The salt value
        creation_date (datetime): The date the salt was created
        last_used (datetime): The date the salt was last used
        purpose (str): The purpose of the salt (e.g., "seed_encryption")
    """
    
    def __init__(
        self,
        salt_id: str = None,
        credential_id: str = None,
        salt: bytes = None,
        creation_date: datetime = None,
        last_used: datetime = None,
        purpose: str = "seed_encryption"
    ):
        """
        Initialize a new YubiKeySalt instance.
        
        Args:
            salt_id: The unique identifier for the salt (auto-generated if None)
            credential_id: The credential ID of the YubiKey
            salt: The salt value
            creation_date: The date the salt was created (auto-generated if None)
            last_used: The date the salt was last used
            purpose: The purpose of the salt (e.g., "seed_encryption")
        """
        self.salt_id = salt_id or str(uuid.uuid4())
        self.credential_id = credential_id
        self.salt = salt
        self.creation_date = creation_date or datetime.now(timezone.utc)
        self.last_used = last_used
        self.purpose = purpose
    
    @classmethod
    def create(
        cls,
        credential_id: str,
        salt: bytes,
        purpose: str = "seed_encryption"
    ) -> t.Optional['YubiKeySalt']:
        """
        Create a new YubiKeySalt in the database.
        
        Args:
            credential_id: The credential ID of the YubiKey
            salt: The salt value
            purpose: The purpose of the salt
            
        Returns:
            A new YubiKeySalt instance if successful, None otherwise
        """
        db = DatabaseManager()
        
        try:
            # First verify the credential exists
            cursor = db.execute_query(
                "SELECT credential_id FROM yubikeys WHERE credential_id = ?",
                (credential_id,)
            )
            
            if cursor is None or cursor.fetchone() is None:
                return None  # Credential doesn't exist
            
            # Create a new YubiKeySalt instance with UTC timestamp
            yubikey_salt = cls(
                credential_id=credential_id,
                salt=salt,
                purpose=purpose,
                creation_date=datetime.now(timezone.utc)
            )
            
            # Insert the YubiKeySalt into the database
            db.execute_query(
                """
                INSERT INTO yubikey_salts (
                    salt_id, credential_id, salt, purpose, creation_date
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    yubikey_salt.salt_id,
                    yubikey_salt.credential_id,
                    yubikey_salt.salt,
                    yubikey_salt.purpose,
                    yubikey_salt.creation_date
                ),
                commit=True
            )
            
            return yubikey_salt
        except Exception as e:
            print(f"Error creating YubiKey salt: {str(e)}")  # For debugging
            return None
    
    @classmethod
    def get_by_id(cls, salt_id: str) -> t.Optional['YubiKeySalt']:
        """
        Get a YubiKeySalt by its ID.
        
        Args:
            salt_id: The ID of the YubiKeySalt to get
            
        Returns:
            A YubiKeySalt instance if found, None otherwise
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM yubikey_salts WHERE salt_id = ?",
            (salt_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        # Convert row to dictionary
        salt_dict = dict(row)
        
        # Create a YubiKeySalt instance from the row data
        return cls(
            salt_id=salt_dict["salt_id"],
            credential_id=salt_dict["credential_id"],
            salt=bytes(salt_dict["salt"]),
            creation_date=salt_dict["creation_date"],
            last_used=salt_dict["last_used"],
            purpose=salt_dict["purpose"]
        )
    
    @classmethod
    def get_by_credential_id(cls, credential_id: str, purpose: str = None) -> t.List['YubiKeySalt']:
        """
        Get YubiKeySalts by credential ID and optionally by purpose.
        
        Args:
            credential_id: The credential ID to get salts for
            purpose: Optional purpose to filter by
            
        Returns:
            A list of YubiKeySalt instances
        """
        db = DatabaseManager()
        
        if purpose:
            cursor = db.execute_query(
                "SELECT * FROM yubikey_salts WHERE credential_id = ? AND purpose = ?",
                (credential_id, purpose)
            )
        else:
            cursor = db.execute_query(
                "SELECT * FROM yubikey_salts WHERE credential_id = ?",
                (credential_id,)
            )
        
        salts = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            salt_dict = dict(row)
            
            # Create a YubiKeySalt instance from the row data
            salt = cls(
                salt_id=salt_dict["salt_id"],
                credential_id=salt_dict["credential_id"],
                salt=bytes(salt_dict["salt"]),
                creation_date=salt_dict["creation_date"],
                last_used=salt_dict["last_used"],
                purpose=salt_dict["purpose"]
            )
            
            salts.append(salt)
        
        return salts
    
    def update(self) -> bool:
        """
        Update the YubiKeySalt in the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # Update the YubiKeySalt in the database
            db.execute_query(
                """
                UPDATE yubikey_salts
                SET salt = ?, last_used = ?, purpose = ?
                WHERE salt_id = ?
                """,
                (
                    self.salt,
                    self.last_used,
                    self.purpose,
                    self.salt_id
                ),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def delete(self) -> bool:
        """
        Delete the YubiKeySalt from the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # Delete the YubiKeySalt from the database
            db.execute_query(
                "DELETE FROM yubikey_salts WHERE salt_id = ?",
                (self.salt_id,),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def update_last_used(self) -> bool:
        """
        Update the YubiKeySalt's last used time.
        
        Returns:
            True if successful, False otherwise
        """
        self.last_used = datetime.now(timezone.utc)
        return self.update()
    
    def to_dict(self) -> dict:
        """
        Convert the YubiKeySalt instance to a dictionary.
        
        Returns:
            A dictionary representation of the YubiKeySalt
        """
        return {
            "salt_id": self.salt_id,
            "credential_id": self.credential_id,
            "salt": self.salt.hex() if self.salt else None,
            "creation_date": self.creation_date,
            "last_used": self.last_used,
            "purpose": self.purpose
        } 
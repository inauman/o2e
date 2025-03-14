"""
YubiKey model for the application.
"""
import uuid
import typing as t
from datetime import datetime

from models.database import DatabaseManager
from models.user import User


class YubiKey:
    """
    YubiKey model representing a YubiKey credential in the application.
    
    Attributes:
        credential_id (str): The unique credential ID from the YubiKey
        user_id (str): The user ID this YubiKey belongs to
        public_key (bytes): The public key associated with this YubiKey
        aaguid (str): The Authenticator Attestation GUID
        registration_date (datetime): The date the YubiKey was registered
        nickname (str): A user-friendly name for the YubiKey
        sign_count (int): The signature counter for detecting cloned authenticators
        is_primary (bool): Whether this is the primary YubiKey for the user
    """
    
    def __init__(
        self,
        credential_id: str,
        user_id: str,
        public_key: bytes,
        aaguid: t.Optional[str] = None,
        registration_date: t.Optional[datetime] = None,
        nickname: t.Optional[str] = None,
        sign_count: int = 0,
        is_primary: bool = False
    ):
        """
        Initialize a new YubiKey instance.
        
        Args:
            credential_id: The unique credential ID from the YubiKey
            user_id: The user ID this YubiKey belongs to
            public_key: The public key associated with this YubiKey
            aaguid: The Authenticator Attestation GUID
            registration_date: The date the YubiKey was registered
            nickname: A user-friendly name for the YubiKey
            sign_count: The signature counter for detecting cloned authenticators
            is_primary: Whether this is the primary YubiKey for the user
        """
        self.credential_id = credential_id
        self.user_id = user_id
        self.public_key = public_key
        self.aaguid = aaguid
        self.registration_date = registration_date or datetime.now()
        self.nickname = nickname
        self.sign_count = sign_count
        self.is_primary = is_primary
    
    @classmethod
    def create(
        cls,
        credential_id: str,
        user_id: str,
        public_key: bytes,
        aaguid: t.Optional[str] = None,
        nickname: t.Optional[str] = None,
        is_primary: bool = False
    ) -> t.Optional['YubiKey']:
        """
        Create a new YubiKey in the database.
        
        Args:
            credential_id: The unique credential ID from the YubiKey
            user_id: The user ID this YubiKey belongs to
            public_key: The public key associated with this YubiKey
            aaguid: The Authenticator Attestation GUID
            nickname: A user-friendly name for the YubiKey
            is_primary: Whether this is the primary YubiKey for the user
            
        Returns:
            A new YubiKey instance if successful, None otherwise
        """
        db = DatabaseManager()
        
        # Get the user to check if they can register another YubiKey
        user = User.get_by_id(user_id)
        if user is None:
            return None
        
        if not user.can_register_yubikey():
            return None
        
        # Create a new YubiKey instance
        yubikey = cls(
            credential_id=credential_id,
            user_id=user_id,
            public_key=public_key,
            aaguid=aaguid,
            nickname=nickname,
            is_primary=is_primary
        )
        
        try:
            # If this is the primary YubiKey, unset any existing primary
            if is_primary:
                db.execute_query(
                    "UPDATE yubikeys SET is_primary = 0 WHERE user_id = ?",
                    (user_id,),
                    commit=True
                )
            
            # Insert the YubiKey into the database
            db.execute_query(
                """
                INSERT INTO yubikeys (
                    credential_id, user_id, public_key, aaguid, 
                    nickname, sign_count, is_primary
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    yubikey.credential_id,
                    yubikey.user_id,
                    yubikey.public_key,
                    yubikey.aaguid,
                    yubikey.nickname,
                    yubikey.sign_count,
                    yubikey.is_primary
                ),
                commit=True
            )
            
            return yubikey
        except Exception:
            # If an error occurred, return None
            return None
    
    @classmethod
    def get_by_credential_id(cls, credential_id: str) -> t.Optional['YubiKey']:
        """
        Get a YubiKey by its credential ID.
        
        Args:
            credential_id: The credential ID to look up
            
        Returns:
            A YubiKey instance if found, None otherwise
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM yubikeys WHERE credential_id = ?",
            (credential_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        # Convert row to dictionary
        yubikey_dict = dict(row)
        
        # Create a YubiKey instance from the row data
        return cls(
            credential_id=yubikey_dict["credential_id"],
            user_id=yubikey_dict["user_id"],
            public_key=bytes(yubikey_dict["public_key"]),
            aaguid=yubikey_dict["aaguid"],
            registration_date=yubikey_dict["registration_date"],
            nickname=yubikey_dict["nickname"],
            sign_count=yubikey_dict["sign_count"],
            is_primary=bool(yubikey_dict["is_primary"])
        )
    
    @classmethod
    def get_by_user_id(cls, user_id: str) -> t.List['YubiKey']:
        """
        Get all YubiKeys for a user.
        
        Args:
            user_id: The user ID to get YubiKeys for
            
        Returns:
            A list of YubiKey instances
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM yubikeys WHERE user_id = ?",
            (user_id,)
        )
        
        yubikeys = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            yubikey_dict = dict(row)
            
            # Create a YubiKey instance from the row data
            yubikey = cls(
                credential_id=yubikey_dict["credential_id"],
                user_id=yubikey_dict["user_id"],
                public_key=bytes(yubikey_dict["public_key"]),
                aaguid=yubikey_dict["aaguid"],
                registration_date=yubikey_dict["registration_date"],
                nickname=yubikey_dict["nickname"],
                sign_count=yubikey_dict["sign_count"],
                is_primary=bool(yubikey_dict["is_primary"])
            )
            
            yubikeys.append(yubikey)
        
        return yubikeys
    
    @classmethod
    def get_primary_for_user(cls, user_id: str) -> t.Optional['YubiKey']:
        """
        Get the primary YubiKey for a user.
        
        Args:
            user_id: The user ID to get the primary YubiKey for
            
        Returns:
            The primary YubiKey instance if found, None otherwise
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM yubikeys WHERE user_id = ? AND is_primary = 1",
            (user_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        # Convert row to dictionary
        yubikey_dict = dict(row)
        
        # Create a YubiKey instance from the row data
        return cls(
            credential_id=yubikey_dict["credential_id"],
            user_id=yubikey_dict["user_id"],
            public_key=bytes(yubikey_dict["public_key"]),
            aaguid=yubikey_dict["aaguid"],
            registration_date=yubikey_dict["registration_date"],
            nickname=yubikey_dict["nickname"],
            sign_count=yubikey_dict["sign_count"],
            is_primary=bool(yubikey_dict["is_primary"])
        )
    
    def update(self) -> bool:
        """
        Update the YubiKey in the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # If this is being set as primary, unset any existing primary
            if self.is_primary:
                db.execute_query(
                    "UPDATE yubikeys SET is_primary = 0 WHERE user_id = ? AND credential_id != ?",
                    (self.user_id, self.credential_id),
                    commit=True
                )
            
            # Update the YubiKey in the database
            db.execute_query(
                """
                UPDATE yubikeys
                SET public_key = ?, aaguid = ?, nickname = ?, 
                    sign_count = ?, is_primary = ?
                WHERE credential_id = ?
                """,
                (
                    self.public_key,
                    self.aaguid,
                    self.nickname,
                    self.sign_count,
                    self.is_primary,
                    self.credential_id
                ),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def delete(self) -> bool:
        """
        Delete the YubiKey from the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # Delete the YubiKey from the database
            db.execute_query(
                "DELETE FROM yubikeys WHERE credential_id = ?",
                (self.credential_id,),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def update_sign_count(self, new_sign_count: int) -> bool:
        """
        Update the sign count for this YubiKey.
        
        Args:
            new_sign_count: The new sign count value
            
        Returns:
            True if successful, False otherwise
        """
        # Only update if the new count is higher (prevents replay attacks)
        if new_sign_count <= self.sign_count:
            return False
        
        self.sign_count = new_sign_count
        return self.update()
    
    def set_as_primary(self) -> bool:
        """
        Set this YubiKey as the primary YubiKey for its user.
        
        Returns:
            True if successful, False otherwise
        """
        self.is_primary = True
        return self.update()
    
    def to_dict(self) -> dict:
        """
        Convert the YubiKey instance to a dictionary.
        
        Returns:
            A dictionary representation of the YubiKey
        """
        return {
            "credential_id": self.credential_id,
            "user_id": self.user_id,
            "public_key": self.public_key.hex() if self.public_key else None,
            "aaguid": self.aaguid,
            "registration_date": self.registration_date,
            "nickname": self.nickname,
            "sign_count": self.sign_count,
            "is_primary": self.is_primary
        } 
"""
YubiKey model for the application.
"""
import typing as t
from datetime import datetime, timezone

from models.database import DatabaseManager
from models.user import User


class YubiKey:
    """
    YubiKey model representing a registered YubiKey in the application.
    
    Attributes:
        credential_id (str): The WebAuthn credential ID (primary key)
        user_id (str): The ID of the user who owns this YubiKey
        public_key (bytes): The WebAuthn public key
        nickname (str): User-assigned nickname for this YubiKey
        aaguid (str): The AAGUID of the authenticator
        sign_count (int): The signature counter
        is_primary (bool): Whether this is the user's primary YubiKey
        created_at (datetime): When the YubiKey was registered
        last_used (datetime): When the YubiKey was last used for authentication
    """
    
    def __init__(
        self,
        credential_id: str,
        user_id: str,
        public_key: bytes,
        nickname: str,
        aaguid: str = None,
        sign_count: int = 0,
        is_primary: bool = False,
        created_at: datetime = None,
        last_used: datetime = None
    ):
        """
        Initialize a new YubiKey instance.
        
        Args:
            credential_id: The WebAuthn credential ID
            user_id: The ID of the user who owns this YubiKey
            public_key: The WebAuthn public key
            nickname: User-assigned nickname for this YubiKey
            aaguid: The AAGUID of the authenticator
            sign_count: The signature counter
            is_primary: Whether this is the user's primary YubiKey
            created_at: When the YubiKey was registered
            last_used: When the YubiKey was last used for authentication
        """
        self.credential_id = credential_id
        self.user_id = user_id
        self.public_key = public_key
        self.nickname = nickname
        self.aaguid = aaguid
        self.sign_count = sign_count
        self.is_primary = is_primary
        self.created_at = created_at or datetime.now(timezone.utc)
        self.last_used = last_used
    
    @classmethod
    def create(
        cls,
        credential_id: str,
        user_id: str,
        public_key: bytes,
        nickname: str,
        aaguid: str = None,
        sign_count: int = 0,
        is_primary: bool = False
    ) -> t.Optional['YubiKey']:
        """
        Create a new YubiKey in the database.
        
        Args:
            credential_id: The WebAuthn credential ID
            user_id: The ID of the user who owns this YubiKey
            public_key: The WebAuthn public key
            nickname: User-assigned nickname for this YubiKey
            aaguid: The AAGUID of the authenticator
            sign_count: The signature counter
            is_primary: Whether this is the user's primary YubiKey
            
        Returns:
            A new YubiKey instance if successful, None otherwise
        """
        # First check if the user exists and can register another YubiKey
        user = User.get_by_id(user_id)
        if user is None or not user.can_register_yubikey():
            return None
        
        db = DatabaseManager()
        
        # Create a new YubiKey instance
        yubikey = cls(
            credential_id=credential_id,
            user_id=user_id,
            public_key=public_key,
            nickname=nickname,
            aaguid=aaguid,
            sign_count=sign_count,
            is_primary=is_primary,
            created_at=datetime.now(timezone.utc)
        )
        
        try:
            # If this is the primary key, unset any existing primary keys
            if is_primary:
                db.execute_query(
                    """
                    UPDATE yubikeys
                    SET is_primary = 0
                    WHERE user_id = ?
                    """,
                    (user_id,),
                    commit=True
                )
            
            # Insert the YubiKey into the database
            db.execute_query(
                """
                INSERT INTO yubikeys (
                    credential_id, user_id, public_key, nickname,
                    aaguid, sign_count, is_primary, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    yubikey.credential_id,
                    yubikey.user_id,
                    yubikey.public_key,
                    yubikey.nickname,
                    yubikey.aaguid,
                    yubikey.sign_count,
                    yubikey.is_primary,
                    yubikey.created_at
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
            credential_id: The credential ID of the YubiKey to get
            
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
            public_key=yubikey_dict["public_key"],
            nickname=yubikey_dict["nickname"],
            aaguid=yubikey_dict["aaguid"],
            sign_count=yubikey_dict["sign_count"],
            is_primary=bool(yubikey_dict["is_primary"]),
            created_at=yubikey_dict["created_at"],
            last_used=yubikey_dict["last_used"]
        )
    
    @classmethod
    def get_yubikeys_by_user_id(cls, user_id: str) -> t.List['YubiKey']:
        """
        Get all YubiKeys registered to a user.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            A list of YubiKey instances
        """
        db = DatabaseManager()
        cursor = db.execute_query(
            """
            SELECT * FROM yubikeys
            WHERE user_id = ?
            """,
            (user_id,)
        )
        
        yubikeys = []
        for row in cursor:
            yubikey = cls(
                credential_id=row['credential_id'],
                user_id=row['user_id'],
                public_key=row['public_key'],
                nickname=row['nickname'],
                aaguid=row['aaguid'],
                sign_count=row['sign_count'],
                is_primary=bool(row['is_primary']),
                created_at=row['created_at'],
                last_used=row['last_used']
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
            nickname=yubikey_dict["nickname"],
            aaguid=yubikey_dict["aaguid"],
            sign_count=yubikey_dict["sign_count"],
            is_primary=bool(yubikey_dict["is_primary"]),
            created_at=yubikey_dict["created_at"],
            last_used=yubikey_dict["last_used"]
        )
    
    def set_as_primary(self) -> bool:
        """
        Set this YubiKey as the primary YubiKey for its user.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # First, unset any existing primary YubiKey
            db.execute_query(
                """
                UPDATE yubikeys
                SET is_primary = 0
                WHERE user_id = ?
                """,
                (self.user_id,),
                commit=True
            )
            
            # Then set this YubiKey as primary
            db.execute_query(
                """
                UPDATE yubikeys
                SET is_primary = 1
                WHERE credential_id = ?
                """,
                (self.credential_id,),
                commit=True
            )
            
            self.is_primary = True
            return True
        except Exception:
            return False
    
    def update(self) -> bool:
        """
        Update the YubiKey in the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # Update the YubiKey in the database
            db.execute_query(
                """
                UPDATE yubikeys
                SET public_key = ?, nickname = ?, aaguid = ?,
                    sign_count = ?, is_primary = ?, last_used = ?
                WHERE credential_id = ?
                """,
                (
                    self.public_key,
                    self.nickname,
                    self.aaguid,
                    self.sign_count,
                    self.is_primary,
                    self.last_used,
                    self.credential_id
                ),
                commit=True
            )
            
            return True
        except Exception:
            return False
    
    def delete(self) -> bool:
        """Delete this YubiKey from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get all YubiKeys for this user
            yubikeys = self.get_yubikeys_by_user_id(self.user_id)
            
            # Don't allow deleting the only YubiKey
            if len(yubikeys) <= 1:
                print("Cannot delete the only YubiKey")
                return False

            # If this is the primary YubiKey, check if another YubiKey is already primary
            if self.is_primary:
                has_other_primary = False
                for yubikey in yubikeys:
                    if yubikey.credential_id != self.credential_id and yubikey.is_primary:
                        has_other_primary = True
                        break
                if not has_other_primary:
                    print("Cannot delete the primary YubiKey unless another YubiKey is set as primary")
                    return False

            # Delete the YubiKey
            db = DatabaseManager()
            cursor = db.execute_query(
                """
                DELETE FROM yubikeys
                WHERE credential_id = ?
                """,
                (self.credential_id,),
                commit=True
            )
            
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Error deleting YubiKey: {e}")
            return False
    
    def update_sign_count(self, new_count: int) -> bool:
        """
        Update the YubiKey's sign count and last_used timestamp.
        
        Args:
            new_count: The new sign count value
            
        Returns:
            True if successful, False otherwise
        """
        # Sign count must increase
        if new_count <= self.sign_count:
            return False
        
        self.sign_count = new_count
        self.last_used = datetime.now(timezone.utc)
        
        return self.update()
    
    def to_dict(self) -> dict:
        """
        Convert the YubiKey to a dictionary.
        
        Returns:
            A dictionary representation of the YubiKey
        """
        return {
            "credential_id": self.credential_id,
            "user_id": self.user_id,
            "nickname": self.nickname,
            "aaguid": self.aaguid,
            "sign_count": self.sign_count,
            "is_primary": self.is_primary,
            "created_at": self.created_at,
            "last_used": self.last_used
        } 
"""
Seed model for the application.
"""
import json
import uuid
import typing as t
from datetime import datetime

from models.database import DatabaseManager
from models.user import User


class Seed:
    """
    Seed model representing an encrypted Bitcoin seed phrase in the application.
    
    Attributes:
        seed_id (str): The unique identifier for the seed
        user_id (str): The ID of the user this seed belongs to
        encrypted_seed (bytes): The encrypted seed phrase
        creation_date (datetime): The date the seed was created
        last_accessed (datetime): The date the seed was last accessed
        metadata (dict): Additional metadata about the seed
    """
    
    def __init__(
        self,
        seed_id: str = None,
        user_id: str = None,
        encrypted_seed: bytes = None,
        creation_date: datetime = None,
        last_accessed: datetime = None,
        metadata: t.Optional[dict] = None
    ):
        """
        Initialize a new Seed instance.
        
        Args:
            seed_id: The unique identifier for the seed (auto-generated if None)
            user_id: The ID of the user this seed belongs to
            encrypted_seed: The encrypted seed phrase
            creation_date: The date the seed was created (auto-generated if None)
            last_accessed: The date the seed was last accessed
            metadata: Additional metadata about the seed
        """
        self.seed_id = seed_id or str(uuid.uuid4())
        self.user_id = user_id
        self.encrypted_seed = encrypted_seed
        self.creation_date = creation_date or datetime.now()
        self.last_accessed = last_accessed
        self.metadata = metadata or {}
    
    @classmethod
    def create(
        cls,
        user_id: str,
        encrypted_seed: bytes,
        metadata: t.Optional[dict] = None
    ) -> t.Optional['Seed']:
        """
        Create a new seed in the database.
        
        Args:
            user_id: The ID of the user this seed belongs to
            encrypted_seed: The encrypted seed phrase
            metadata: Additional metadata about the seed
            
        Returns:
            A new Seed instance if successful, None otherwise
        """
        db = DatabaseManager()
        
        # Check if the user exists
        user = User.get_by_id(user_id)
        if user is None:
            return None
        
        # Create a new Seed instance
        seed = cls(
            user_id=user_id,
            encrypted_seed=encrypted_seed,
            metadata=metadata
        )
        
        # Convert metadata to JSON string
        metadata_json = json.dumps(seed.metadata) if seed.metadata else None
        
        try:
            # Insert the seed into the database
            db.execute_query(
                """
                INSERT INTO seeds (
                    seed_id, user_id, encrypted_seed, metadata
                )
                VALUES (?, ?, ?, ?)
                """,
                (seed.seed_id, seed.user_id, seed.encrypted_seed, metadata_json),
                commit=True
            )
            
            return seed
        except Exception:
            # If an error occurred, return None
            return None
    
    @classmethod
    def get_by_id(cls, seed_id: str) -> t.Optional['Seed']:
        """
        Get a seed by its ID.
        
        Args:
            seed_id: The ID of the seed to get
            
        Returns:
            A Seed instance if found, None otherwise
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM seeds WHERE seed_id = ?",
            (seed_id,)
        )
        
        row = cursor.fetchone()
        if row is None:
            return None
        
        # Convert row to dictionary
        seed_dict = dict(row)
        
        # Parse metadata from JSON
        metadata = None
        if seed_dict["metadata"]:
            try:
                metadata = json.loads(seed_dict["metadata"])
            except json.JSONDecodeError:
                metadata = {}
        
        # Create a Seed instance from the row data
        return cls(
            seed_id=seed_dict["seed_id"],
            user_id=seed_dict["user_id"],
            encrypted_seed=bytes(seed_dict["encrypted_seed"]),
            creation_date=seed_dict["creation_date"],
            last_accessed=seed_dict["last_accessed"],
            metadata=metadata
        )
    
    @classmethod
    def get_by_user_id(cls, user_id: str) -> t.List['Seed']:
        """
        Get all seeds for a user.
        
        Args:
            user_id: The ID of the user to get seeds for
            
        Returns:
            A list of Seed instances
        """
        db = DatabaseManager()
        
        cursor = db.execute_query(
            "SELECT * FROM seeds WHERE user_id = ?",
            (user_id,)
        )
        
        seeds = []
        for row in cursor.fetchall():
            # Convert row to dictionary
            seed_dict = dict(row)
            
            # Parse metadata from JSON
            metadata = None
            if seed_dict["metadata"]:
                try:
                    metadata = json.loads(seed_dict["metadata"])
                except json.JSONDecodeError:
                    metadata = {}
            
            # Create a Seed instance from the row data
            seed = cls(
                seed_id=seed_dict["seed_id"],
                user_id=seed_dict["user_id"],
                encrypted_seed=bytes(seed_dict["encrypted_seed"]),
                creation_date=seed_dict["creation_date"],
                last_accessed=seed_dict["last_accessed"],
                metadata=metadata
            )
            
            seeds.append(seed)
        
        return seeds
    
    def update(self) -> bool:
        """
        Update the seed in the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        # Convert metadata to JSON string
        metadata_json = json.dumps(self.metadata) if self.metadata else None
        
        try:
            # Update the seed in the database
            db.execute_query(
                """
                UPDATE seeds
                SET encrypted_seed = ?, last_accessed = ?, metadata = ?
                WHERE seed_id = ?
                """,
                (
                    self.encrypted_seed,
                    self.last_accessed,
                    metadata_json,
                    self.seed_id
                ),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def delete(self) -> bool:
        """
        Delete the seed from the database.
        
        Returns:
            True if successful, False otherwise
        """
        db = DatabaseManager()
        
        try:
            # Delete the seed from the database
            db.execute_query(
                "DELETE FROM seeds WHERE seed_id = ?",
                (self.seed_id,),
                commit=True
            )
            
            return True
        except Exception:
            # If an error occurred, return False
            return False
    
    def update_last_accessed(self) -> bool:
        """
        Update the seed's last accessed time.
        
        Returns:
            True if successful, False otherwise
        """
        self.last_accessed = datetime.now()
        return self.update()
    
    def update_metadata(self, metadata: dict) -> bool:
        """
        Update the seed's metadata.
        
        Args:
            metadata: The new metadata
            
        Returns:
            True if successful, False otherwise
        """
        self.metadata = metadata
        return self.update()
    
    def to_dict(self) -> dict:
        """
        Convert the Seed instance to a dictionary.
        
        Returns:
            A dictionary representation of the Seed
        """
        return {
            "seed_id": self.seed_id,
            "user_id": self.user_id,
            "encrypted_seed": self.encrypted_seed.hex() if self.encrypted_seed else None,
            "creation_date": self.creation_date,
            "last_accessed": self.last_accessed,
            "metadata": self.metadata
        } 
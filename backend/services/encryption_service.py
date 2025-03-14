"""
Encryption service for YubiKey Bitcoin Seed Storage
"""

import os
import yaml
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from models.seed import Seed

class EncryptionService:
    """Service for handling encryption operations"""
    
    def __init__(self):
        """Initialize the encryption service"""
        # Load configuration
        with open(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'), 'r') as f:
            self.config = yaml.safe_load(f)
    
    def _derive_key(self, encryption_key: str, salt: bytes) -> bytes:
        """
        Derive an encryption key from a password
        
        Args:
            encryption_key: The password to derive the key from
            salt: The salt to use for key derivation
            
        Returns:
            The derived key
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self.config['security']['iterations'],
        )
        return kdf.derive(encryption_key.encode('utf-8'))
    
    def encrypt_seed(self, user_id: str, mnemonic: str, encryption_key: str) -> Dict[str, Any]:
        """
        Encrypt and store a seed phrase
        
        Args:
            user_id: The user ID to associate with the seed
            mnemonic: The mnemonic seed phrase to encrypt
            encryption_key: The key to use for encryption
            
        Returns:
            A dictionary with the result of the operation
        """
        try:
            # Generate a random salt
            salt = os.urandom(16)
            
            # Derive the encryption key
            key = self._derive_key(encryption_key, salt)
            
            # Generate a random nonce
            nonce = os.urandom(12)
            
            # Encrypt the mnemonic
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, mnemonic.encode('utf-8'), None)
            
            # Create the encrypted seed in the database
            seed = Seed.create(
                user_id=user_id,
                encrypted_seed={
                    'salt': salt.hex(),
                    'nonce': nonce.hex(),
                    'ciphertext': ciphertext.hex()
                }
            )
            
            if not seed:
                return {'success': False, 'error': 'Failed to store encrypted seed'}
            
            return {'success': True, 'seed_id': seed.seed_id}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def decrypt_seed(self, seed_id: str, encryption_key: str) -> Dict[str, Any]:
        """
        Retrieve and decrypt a stored seed phrase
        
        Args:
            seed_id: The ID of the seed to decrypt
            encryption_key: The key to use for decryption
            
        Returns:
            A dictionary with the result of the operation
        """
        try:
            # Get the seed from the database
            seed = Seed.get_by_id(seed_id)
            
            if not seed:
                return {'success': False, 'error': 'Seed not found'}
            
            # Get the encrypted seed data
            seed_data = seed.encrypted_seed
            
            # Convert hex values to bytes
            salt = bytes.fromhex(seed_data['salt'])
            nonce = bytes.fromhex(seed_data['nonce'])
            ciphertext = bytes.fromhex(seed_data['ciphertext'])
            
            # Derive the encryption key
            key = self._derive_key(encryption_key, salt)
            
            # Decrypt the mnemonic
            aesgcm = AESGCM(key)
            mnemonic = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
            
            # Update last accessed time
            seed.update_last_accessed()
            
            return {'success': True, 'mnemonic': mnemonic}
        except Exception as e:
            return {'success': False, 'error': 'Invalid encryption key or corrupted data'} 
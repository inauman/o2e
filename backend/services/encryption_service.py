"""
Encryption service for YubiKey Bitcoin Seed Storage
"""

import os
import json
import yaml
from typing import Dict, Any, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class EncryptionService:
    """Service for handling encryption operations"""
    
    def __init__(self):
        """Initialize the encryption service"""
        # Load configuration
        with open(os.path.join(os.path.dirname(__file__), '..', 'config.yaml'), 'r') as f:
            self.config = yaml.safe_load(f)
            
        # Set up encryption parameters
        self.seeds_file = self.config['data']['seeds_file']
        self.seeds = self._load_seeds()
    
    def _load_seeds(self) -> Dict[str, Any]:
        """Load encrypted seeds from file"""
        if os.path.exists(self.seeds_file):
            with open(self.seeds_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_seeds(self) -> None:
        """Save encrypted seeds to file"""
        with open(self.seeds_file, 'w') as f:
            json.dump(self.seeds, f, indent=2)
    
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
            iterations=100000,
        )
        return kdf.derive(encryption_key.encode('utf-8'))
    
    def store_encrypted_seed(self, username: str, mnemonic: str, encryption_key: str) -> Dict[str, Any]:
        """
        Encrypt and store a seed phrase
        
        Args:
            username: The username to associate with the seed
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
            
            # Store the encrypted seed
            self.seeds[username] = {
                'salt': salt.hex(),
                'nonce': nonce.hex(),
                'ciphertext': ciphertext.hex()
            }
            
            # Save the seeds
            self._save_seeds()
            
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def retrieve_encrypted_seed(self, username: str, encryption_key: str) -> Dict[str, Any]:
        """
        Retrieve and decrypt a stored seed phrase
        
        Args:
            username: The username associated with the seed
            encryption_key: The key to use for decryption
            
        Returns:
            A dictionary with the result of the operation
        """
        try:
            # Check if the user has a stored seed
            if username not in self.seeds:
                return {'success': False, 'error': 'No seed found for this user'}
            
            # Get the encrypted seed
            seed_data = self.seeds[username]
            
            # Convert hex values to bytes
            salt = bytes.fromhex(seed_data['salt'])
            nonce = bytes.fromhex(seed_data['nonce'])
            ciphertext = bytes.fromhex(seed_data['ciphertext'])
            
            # Derive the encryption key
            key = self._derive_key(encryption_key, salt)
            
            # Decrypt the mnemonic
            aesgcm = AESGCM(key)
            mnemonic = aesgcm.decrypt(nonce, ciphertext, None).decode('utf-8')
            
            return {'success': True, 'mnemonic': mnemonic}
        except Exception as e:
            return {'success': False, 'error': 'Invalid encryption key or corrupted data'} 
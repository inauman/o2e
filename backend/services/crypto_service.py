"""
Crypto service for encrypting and decrypting data.
"""
import os
import hashlib
import hmac
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes
import yaml
import typing as t

CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config.yaml"))

def load_config():
    """Load configuration from file."""
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

def get_encryption_key(encryption_context: t.Optional[dict] = None):
    """
    Get encryption key from configuration.
    
    Args:
        encryption_context: Optional context for key derivation
        
    Returns:
        The encryption key
    """
    config = load_config()
    
    # Use configured key derivation method
    key_derivation = config.get("key_derivation", "HKDF-SHA256")
    master_key = config.get("master_key", "this_should_be_changed_in_production")
    
    # Convert string master key to bytes
    if isinstance(master_key, str):
        master_key = master_key.encode()
    
    # Create a context-specific key
    if key_derivation == "HKDF-SHA256":
        # Generate a salt or use one from context
        salt = os.urandom(16)
        if encryption_context and "salt" in encryption_context:
            salt = encryption_context["salt"]
            
        # Derive the key using HKDF
        hkdf = HKDF(
            algorithm=hashes.SHA256(),
            length=32,  # 256 bits
            salt=salt,
            info=b"seed_encryption"
        )
        key = hkdf.derive(master_key)
        
        # If this is a new key, return the salt as well
        if encryption_context is None or "salt" not in encryption_context:
            return key, {"salt": salt}
        return key, None
        
    else:  # Default to PBKDF2
        # Use a fixed salt for now
        salt = b"yubikey_bitcoin_seed_storage_salt"
        if encryption_context and "salt" in encryption_context:
            salt = encryption_context["salt"]
            
        # Derive the key using PBKDF2
        key = hashlib.pbkdf2_hmac(
            "sha256",
            master_key,
            salt,
            100000,  # Iterations
            dklen=32  # 256 bits
        )
        
        # If this is a new key, return the salt as well
        if encryption_context is None or "salt" not in encryption_context:
            return key, {"salt": salt}
        return key, None

def encrypt_seed(seed_phrase: str) -> bytes:
    """
    Encrypt a seed phrase.
    
    Args:
        seed_phrase: The seed phrase to encrypt
        
    Returns:
        Encrypted seed phrase with metadata
    """
    # Convert the seed phrase to bytes
    plaintext = seed_phrase.encode("utf-8")
    
    # Get encryption key
    key, context = get_encryption_key()
    
    # Generate a random nonce
    nonce = os.urandom(12)
    
    # Encrypt the data
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    
    # Combine metadata and ciphertext
    result = {
        "version": 1,
        "algorithm": "AES-256-GCM",
        "nonce": base64.b64encode(nonce).decode("utf-8"),
        "ciphertext": base64.b64encode(ciphertext).decode("utf-8")
    }
    
    # Add context if provided
    if context:
        for k, v in context.items():
            if isinstance(v, bytes):
                result[k] = base64.b64encode(v).decode("utf-8")
            else:
                result[k] = v
    
    # Serialize to JSON
    import json
    return json.dumps(result).encode("utf-8")

def decrypt_seed(encrypted_data: bytes) -> str:
    """
    Decrypt a seed phrase.
    
    Args:
        encrypted_data: The encrypted seed phrase with metadata
        
    Returns:
        Decrypted seed phrase
    """
    # Parse the encrypted data
    import json
    data = json.loads(encrypted_data.decode("utf-8"))
    
    # Extract metadata
    version = data.get("version", 1)
    algorithm = data.get("algorithm", "AES-256-GCM")
    nonce = base64.b64decode(data.get("nonce"))
    ciphertext = base64.b64decode(data.get("ciphertext"))
    
    # Build encryption context
    context = {}
    if "salt" in data:
        context["salt"] = base64.b64decode(data.get("salt"))
    
    # Get decryption key
    key, _ = get_encryption_key(context)
    
    # Decrypt the data
    aesgcm = AESGCM(key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    
    # Convert plaintext to string
    return plaintext.decode("utf-8") 
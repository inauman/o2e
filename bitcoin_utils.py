#!/usr/bin/env python3
"""
Bitcoin utilities for YubiKey Bitcoin Seed Storage POC.
This module handles BIP39 seed generation and validation.
"""

import os
import hashlib
import hmac
import binascii
from mnemonic import Mnemonic
from typing import Tuple, Optional, List, Dict, Any

class BitcoinSeedManager:
    """
    Manages Bitcoin seed generation, validation, and conversion.
    Strictly follows BIP39 standards.
    """
    
    def __init__(self, language: str = "english", strength: int = 256):
        """
        Initialize the BitcoinSeedManager.
        
        Args:
            language: The language for the mnemonic words (default: english)
            strength: The strength of the seed in bits, either 128 (12 words) or 256 (24 words)
        """
        if strength not in [128, 256]:
            raise ValueError("Strength must be either 128 (12 words) or 256 (24 words)")
        
        self.language = language
        self.strength = strength
        self.mnemonic = Mnemonic(language)
    
    def generate_seed(self) -> Tuple[str, bytes]:
        """
        Generate a new BIP39 mnemonic and seed.
        Uses a cryptographically secure random number generator.
        
        Returns:
            Tuple containing the mnemonic phrase and the binary seed
        """
        # Generate random entropy with the specified strength
        entropy = os.urandom(self.strength // 8)
        
        # Generate mnemonic from entropy
        mnemonic_phrase = self.mnemonic.to_mnemonic(entropy)
        
        # Convert mnemonic to seed (no passphrase)
        seed = self.mnemonic_to_seed(mnemonic_phrase)
        
        return mnemonic_phrase, seed
    
    def validate_mnemonic(self, mnemonic: str) -> bool:
        """
        Validate if a mnemonic phrase is valid according to BIP39.
        
        Args:
            mnemonic: The mnemonic phrase to validate
            
        Returns:
            True if valid, False otherwise
        """
        return self.mnemonic.check(mnemonic)
    
    def mnemonic_to_seed(self, mnemonic: str, passphrase: str = "") -> bytes:
        """
        Convert a mnemonic phrase to a binary seed.
        
        Args:
            mnemonic: The mnemonic phrase
            passphrase: Optional passphrase for extra security
            
        Returns:
            Binary seed derived from the mnemonic
        """
        return self.mnemonic.to_seed(mnemonic, passphrase)
    
    def mnemonic_to_entropy(self, mnemonic: str) -> bytes:
        """
        Convert a mnemonic phrase back to its original entropy.
        
        Args:
            mnemonic: The mnemonic phrase
            
        Returns:
            Original entropy bytes
        """
        return bytes(self.mnemonic.to_entropy(mnemonic))
    
    def entropy_to_mnemonic(self, entropy: bytes) -> str:
        """
        Convert entropy bytes to a mnemonic phrase.
        
        Args:
            entropy: The entropy bytes
            
        Returns:
            Mnemonic phrase
        """
        return self.mnemonic.to_mnemonic(entropy)
    
    @staticmethod
    def secure_erase(data: bytearray) -> None:
        """
        Securely erase sensitive data from memory.
        
        Args:
            data: The bytearray to erase
        """
        for i in range(len(data)):
            data[i] = 0


# Test vectors for verification (based on BIP39 test vectors)
def get_test_vectors() -> List[Dict[str, Any]]:
    """
    Return test vectors for verifying the implementation.
    
    Returns:
        List of test vectors with entropy, mnemonic, and seed
    """
    return [
        {
            "entropy": binascii.unhexlify("00000000000000000000000000000000"),
            "mnemonic": "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about",
            "seed": binascii.unhexlify("c55257c360c07c72029aebc1b53c05ed0362ada38ead3e3e9efa3708e53495531f09a6987599d18264c1e1c92f2cf141630c7a3c4ab7c81b2f001698e7463b04"),
        },
        {
            "entropy": binascii.unhexlify("7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f"),
            "mnemonic": "legal winner thank year wave sausage worth useful legal winner thank yellow",
            "seed": binascii.unhexlify("2e8905819b8723fe2c1d161860e5ee1830318dbf49a83bd451cfb8440c28bd6fa457fe1296106559a3c80937a1c1069be3a3a5bd381ee6260e8d9739fce1f607"),
        }
    ]


if __name__ == "__main__":
    # Simple test to verify the implementation
    manager = BitcoinSeedManager()
    mnemonic_phrase, seed = manager.generate_seed()
    
    print(f"Generated mnemonic: {mnemonic_phrase}")
    print(f"Seed (hex): {binascii.hexlify(seed).decode()}")
    
    # Validate the generated mnemonic
    is_valid = manager.validate_mnemonic(mnemonic_phrase)
    print(f"Mnemonic is valid: {is_valid}")
    
    # Test against test vectors
    print("\nVerifying against test vectors:")
    test_vectors = get_test_vectors()
    for i, vector in enumerate(test_vectors):
        entropy = vector["entropy"]
        expected_mnemonic = vector["mnemonic"]
        expected_seed = vector["seed"]
        
        # Test entropy to mnemonic
        derived_mnemonic = manager.entropy_to_mnemonic(entropy)
        mnemonic_match = derived_mnemonic == expected_mnemonic
        
        # Test mnemonic to seed
        derived_seed = manager.mnemonic_to_seed(expected_mnemonic)
        seed_match = derived_seed == expected_seed
        
        print(f"Test vector {i+1}:")
        print(f"  Mnemonic match: {mnemonic_match}")
        print(f"  Seed match: {seed_match}") 
#!/usr/bin/env python3
"""
Unit tests for the Bitcoin utilities.
"""

import unittest
import sys
import os
import tempfile
import threading

# Add the root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from utils.bitcoin_utils import BitcoinSeedManager

class TestBitcoinSeedManager(unittest.TestCase):
    """Test cases for the BitcoinSeedManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = BitcoinSeedManager()
    
    def test_init(self):
        """Test initialization with default values."""
        self.assertEqual(self.manager.language, "english")
        self.assertEqual(self.manager.strength, 256)
    
    def test_generate_seed(self):
        """Test seed generation"""
        mnemonic, seed = self.manager.generate_seed()
        self.assertIsNotNone(mnemonic)
        self.assertIsInstance(mnemonic, str)
        self.assertIsInstance(seed, bytes)
        # Validate the generated mnemonic
        self.assertTrue(self.manager.validate_mnemonic(mnemonic))
    
    def test_validate_seed_valid(self):
        """Test validation of valid seed phrases"""
        # Generate a valid seed
        mnemonic, _ = self.manager.generate_seed()
        self.assertTrue(self.manager.validate_mnemonic(mnemonic))
    
    def test_validate_seed_invalid(self):
        """Test validation of invalid seed phrases"""
        # Test invalid length (not 12 or 24 words)
        invalid_seed = "word1 word2 word3"
        self.assertFalse(self.manager.validate_mnemonic(invalid_seed))

if __name__ == '__main__':
    unittest.main() 
#!/usr/bin/env python3
"""
Unit tests for bitcoin_utils.py
"""

import unittest
import sys
import os

# Add the root directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from bitcoin_utils import BitcoinSeedManager

class TestBitcoinSeedManager(unittest.TestCase):
    """Test cases for BitcoinSeedManager class"""

    def setUp(self):
        """Set up test fixtures"""
        self.manager = BitcoinSeedManager()
        self.manager_custom = BitcoinSeedManager(strength=128)

    def test_init(self):
        """Test initialization with default and custom strength"""
        self.assertEqual(self.manager.strength, 256)
        self.assertEqual(self.manager_custom.strength, 128)

    def test_generate_seed(self):
        """Test seed generation"""
        seed = self.manager.generate_seed()
        self.assertIsNotNone(seed)
        self.assertIsInstance(seed, str)
        # In the minimal implementation, it should return a fixed test seed
        self.assertEqual(seed, "test test test test test test test test test test test test")

    def test_validate_seed_valid(self):
        """Test validation of valid seed phrases"""
        # Test 12-word seed
        valid_seed_12 = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12"
        self.assertTrue(self.manager.validate_seed(valid_seed_12))
        
        # Test 24-word seed
        valid_seed_24 = "word1 word2 word3 word4 word5 word6 word7 word8 word9 word10 word11 word12 word13 word14 word15 word16 word17 word18 word19 word20 word21 word22 word23 word24"
        self.assertTrue(self.manager.validate_seed(valid_seed_24))

    def test_validate_seed_invalid(self):
        """Test validation of invalid seed phrases"""
        # Test invalid length (not 12 or 24 words)
        invalid_seed = "word1 word2 word3"
        self.assertFalse(self.manager.validate_seed(invalid_seed))
        
        # Test empty string
        self.assertFalse(self.manager.validate_seed(""))
        
        # Test None
        with self.assertRaises(AttributeError):
            self.manager.validate_seed(None)

if __name__ == '__main__':
    unittest.main() 
import os
import unittest
import yaml
from unittest.mock import patch, MagicMock
from utils.security import load_config

class TestConfig(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            'webauthn': {
                'rp': {
                    'name': 'Test Relying Party',
                    'id': 'localhost'
                },
                'origin': 'http://localhost:5000',
                'user_verification': 'preferred',
                'require_touch': True
            }
        }
        
    def test_load_config_with_valid_file(self):
        """Test loading configuration from a valid YAML file."""
        # Create a mock YAML file content
        yaml_content = yaml.dump(self.test_config)
        
        # Mock the file operations
        with patch('builtins.open', unittest.mock.mock_open(read_data=yaml_content)):
            # Load the configuration
            config = load_config()
            
            # Verify the loaded configuration matches expected values
            self.assertEqual(config['webauthn']['rp']['name'], 'Test Relying Party')
            self.assertEqual(config['webauthn']['rp']['id'], 'localhost')
            self.assertEqual(config['webauthn']['origin'], 'http://localhost:5000')
            
    def test_load_config_with_missing_file(self):
        """Test loading configuration when file is missing returns default config."""
        # Mock a FileNotFoundError when trying to open the file
        with patch('builtins.open', side_effect=FileNotFoundError()):
            # Load the configuration
            config = load_config()
            
            # Verify we get the default configuration
            self.assertIn('webauthn', config)
            self.assertEqual(config['webauthn']['rp_id'], '127.0.0.1')
            self.assertEqual(config['webauthn']['rp_name'], 'YubiKey Bitcoin Seed Storage')
            
    def test_load_config_with_invalid_yaml(self):
        """Test loading configuration with invalid YAML content."""
        # Create invalid YAML content
        invalid_yaml = """
        invalid:
          - yaml: [content
        """
        
        # Mock the load_config function itself to raise a YAML parsing exception
        with patch('builtins.open', unittest.mock.mock_open(read_data=invalid_yaml)):
            # Patch yaml.safe_load to raise an exception
            with patch('yaml.safe_load', side_effect=yaml.YAMLError):
                # Load the configuration
                config = load_config()
                
                # Verify we get the default configuration
                self.assertIn('webauthn', config)
                self.assertEqual(config['webauthn']['rp_id'], '127.0.0.1')
                self.assertEqual(config['webauthn']['rp_name'], 'YubiKey Bitcoin Seed Storage') 
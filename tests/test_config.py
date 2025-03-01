"""Tests for the configuration module."""

import os
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from walgreens_print.config import Config, ConfigError


@pytest.fixture
def config():
    """Create a Config instance for testing."""
    config_obj = Config()
    # Override the config file path for testing
    config_obj.config_dir = Path('/tmp/test-walgreens-print')
    config_obj.config_file = config_obj.config_dir / 'config.yaml'
    return config_obj


def test_load_config_file_not_exists(config):
    """Test loading config when file doesn't exist creates a new one."""
    with patch.object(Path, 'exists', return_value=False):
        with patch.object(config, '_create_config') as mock_create_config:
            with patch.object(Path, 'mkdir'):
                config.load()
                mock_create_config.assert_called_once()


def test_load_config_valid(config):
    """Test loading a valid config file."""
    valid_config = {'api_key': 'testkey', 'affiliate_id': 'testid', 'store_id': 'storeid'}
    
    with patch.object(Path, 'exists', return_value=True):
        with patch('builtins.open', mock_open(read_data=yaml.dump(valid_config))):
            loaded_config = config.load()
            assert loaded_config == valid_config


def test_load_config_invalid_yaml(config):
    """Test loading an invalid YAML file."""
    with patch.object(Path, 'exists', return_value=True):
        with patch('builtins.open', mock_open(read_data='invalid: yaml: content')):
            with patch('yaml.safe_load', side_effect=yaml.YAMLError):
                with pytest.raises(ConfigError, match="not valid YAML"):
                    config.load()


def test_validate_config_missing_field(config):
    """Test validation with a missing required field."""
    config.config = {'api_key': 'testkey', 'store_id': 'storeid'}  # missing affiliate_id
    
    with pytest.raises(ConfigError, match="Missing required field 'affiliate_id'"):
        config._validate_config()


def test_validate_config_empty_field(config):
    """Test validation with an empty required field."""
    config.config = {'api_key': 'testkey', 'affiliate_id': '', 'store_id': 'storeid'}
    
    with pytest.raises(ConfigError, match="Field 'affiliate_id' cannot be empty"):
        config._validate_config()


def test_create_config(config):
    """Test creating a new config file."""
    user_inputs = ['testkey', 'testid', 'storeid']
    
    with patch('builtins.input', side_effect=user_inputs):
        with patch('builtins.open', mock_open()) as mock_file:
            with patch.object(Path, 'mkdir'):
                with patch.object(config, '_validate_config'):
                    config._create_config()
                    
                    # Check if the config was created with the right values
                    assert config.config['api_key'] == 'testkey'
                    assert config.config['affiliate_id'] == 'testid'
                    assert config.config['store_id'] == 'storeid'
                    
                    # Check if the file was written
                    mock_file.assert_called_once_with(config.config_file, 'w') 
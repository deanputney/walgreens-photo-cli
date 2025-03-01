"""Configuration management for Walgreens Photo Printing tool."""

import os
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any


class ConfigError(Exception):
    """Exception raised for configuration errors."""
    pass


class Config:
    """Manages the configuration for the Walgreens Photo Printing tool."""
    
    REQUIRED_FIELDS = ["api_key", "affiliate_id"]
    
    def __init__(self):
        """Initialize configuration paths."""
        # User config directory
        self.user_config_dir = Path.home() / ".config" / "walgreens-print"
        self.user_config_file = self.user_config_dir / "config.yaml"
        
        # Local config directory
        self.local_config_file = Path("config.yaml")
        
        self.config = {}
        self.logger = logging.getLogger(__name__)
    
    def load(self) -> Dict[str, Any]:
        """
        Load and validate the configuration file.
        
        Checks for a config file in the following order:
        1. Local directory (./config.yaml)
        2. User's config directory (~/.config/walgreens-print/config.yaml)
        
        Returns:
            Dict containing configuration values
        """
        # Try local config first
        if self.local_config_file.exists():
            self.logger.debug(f"Loading configuration from local file: {self.local_config_file}")
            return self._load_file(self.local_config_file)
        
        # Then try user config
        if self.user_config_file.exists():
            self.logger.debug(f"Loading configuration from user config file: {self.user_config_file}")
            return self._load_file(self.user_config_file)
        
        # If no config files exist, create one
        self.logger.debug("No configuration file found, creating one")
        return self._create_config()
    
    def _load_file(self, config_file: Path) -> Dict[str, Any]:
        """Load and validate a specific configuration file."""
        try:
            with open(config_file, "r") as f:
                self.config = yaml.safe_load(f)
            
            if self.config is None:
                raise ConfigError("Config file is empty or not valid YAML")
            
            self._validate_config()
            return self.config
            
        except yaml.YAMLError:
            raise ConfigError("Config file is not valid YAML")
        except Exception as e:
            if isinstance(e, ConfigError):
                raise
            raise ConfigError(f"Unable to read config file at {config_file}")
    
    def _create_config(self) -> Dict[str, Any]:
        """Create config directory and prompt for credentials and user information."""
        self.user_config_dir.mkdir(parents=True, exist_ok=True)
        
        print("First time setup - Please enter your Walgreens API credentials:")
        api_key = input("API Key: ").strip()
        affiliate_id = input("Affiliate ID: ").strip()
        
        print("\nEnter your personal information for Walgreens orders:")
        first_name = input("First Name: ").strip()
        last_name = input("Last Name: ").strip()
        phone = input("Phone Number: ").strip()
        email = input("Email: ").strip()
        
        self.config = {
            "api_key": api_key,
            "affiliate_id": affiliate_id,
            "customer": {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "email": email
            },
            "default_store": None  # Will be set when user selects a store
        }
        
        # Validate the entered values
        self._validate_config()
        
        # Save the config
        with open(self.user_config_file, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
            
        print(f"Configuration saved to {self.user_config_file}")
        return self.config
    
    def _validate_config(self):
        """Validate that all required fields are present and non-empty."""
        for field in self.REQUIRED_FIELDS:
            if field not in self.config:
                raise ConfigError(f"Missing required field '{field}' in config file")
            if not self.config[field] or self.config[field].strip() == "":
                raise ConfigError(f"Field '{field}' cannot be empty")
        
        # Validate customer information if present
        if "customer" in self.config:
            customer = self.config["customer"]
            for field in ["first_name", "last_name", "phone", "email"]:
                if field not in customer or not customer[field]:
                    raise ConfigError(f"Missing or empty customer {field} in config file")
    
    def save(self) -> None:
        """Save the current configuration to the user's config file."""
        self.user_config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.user_config_file, "w") as f:
            yaml.dump(self.config, f, default_flow_style=False)
            
        self.logger.debug(f"Configuration saved to {self.user_config_file}")
    
    def update_default_store(self, store_info: Dict[str, Any]) -> None:
        """Update the default store in the configuration."""
        if not self.config:
            self.load()
            
        self.config["default_store"] = store_info
        self.save()
        self.logger.debug(f"Updated default store to: {store_info['store_num']}")


def get_api_key() -> str:
    """Get Walgreens API key from config file or environment."""
    api_key = os.environ.get("WALGREENS_API_KEY")
    if api_key:
        return api_key
        
    # If not in environment, load from config
    config = Config()
    config_data = config.load()
    return config_data["api_key"]

def get_api_secret() -> str:
    """Get Walgreens API secret (affiliate ID) from config file or environment."""
    api_secret = os.environ.get("WALGREENS_API_SECRET")
    if api_secret:
        return api_secret
        
    # If not in environment, load from config
    config = Config()
    config_data = config.load()
    return config_data["affiliate_id"]

def get_base_url() -> str:
    """Get Walgreens API base URL, allowing for environment selection."""
    environment = os.environ.get("WALGREENS_API_ENVIRONMENT", "production")
    
    if environment.lower() == "sandbox":
        return "https://services-qa.walgreens.com/api"
    else:
        return "https://services.walgreens.com/api" 
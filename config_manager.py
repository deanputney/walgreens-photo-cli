import os
import yaml
from pathlib import Path

CONFIG_PATH = Path.home() / '.config' / 'walgreens-print' / 'config.yaml'

def create_config():
    # Ensure the directory exists
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Prompt user for configuration details
    api_key = input("Enter API key: ").strip()
    affiliate_id = input("Enter Affiliate ID: ").strip()
    store_id = input("Enter Store ID: ").strip()

    config_data = {
        'api_key': api_key,
        'affiliate_id': affiliate_id,
        'store_id': store_id
    }

    # Write the configuration to a YAML file
    with open(CONFIG_PATH, 'w') as config_file:
        yaml.dump(config_data, config_file)

def load_config():
    if not CONFIG_PATH.exists():
        create_config()

    try:
        with open(CONFIG_PATH, 'r') as config_file:
            config_data = yaml.safe_load(config_file)
        
        # Validate required fields
        for field in ['api_key', 'affiliate_id', 'store_id']:
            if not config_data.get(field):
                raise ValueError(f"Error: Missing required field '{field}' in config file")
        
        return config_data

    except yaml.YAMLError as e:
        print(f"Error reading the configuration file: {e}")
        exit(1)
    except ValueError as e:
        print(e)
        exit(1)

if __name__ == '__main__':
    # For testing purposes, you can call load_config() here
    config = load_config()
    print("Configuration loaded successfully:", config)

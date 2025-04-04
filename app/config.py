"""
Configuration handling for the Redmine MCP Server
"""

import os
import logging
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'redmine_url': 'http://localhost:3000',
    'redmine_api_key': None,
    'server_port': 5050,
    'log_level': 'INFO',
    'project_id': 1,
    'default_category_id': 3,  # Default to 'insight' category
    'default_tracker_id': 2,   # Default to 'Feature' tracker
}

def load_config():
    """
    Load configuration from YAML files and environment variables
    
    Returns:
        dict: The configuration dictionary
    """
    # Start with default configuration
    config = DEFAULT_CONFIG.copy()
    
    # Try to load from standard config file
    config_path = os.environ.get('CONFIG_PATH', 'config.yaml')
    if Path(config_path).exists():
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    config.update(yaml_config)
        except Exception as e:
            logger.warning(f"Error loading config file: {str(e)}")
    
    # Try to load from credentials file
    credentials_path = os.environ.get('CREDENTIALS_PATH', 'credentials.yaml')
    if Path(credentials_path).exists():
        try:
            with open(credentials_path, 'r') as f:
                credentials = yaml.safe_load(f)
                if credentials:
                    config.update(credentials)
        except Exception as e:
            logger.warning(f"Error loading credentials file: {str(e)}")
    
    # Override with environment variables
    env_vars = {
        'REDMINE_URL': 'redmine_url',
        'REDMINE_API_KEY': 'redmine_api_key',
        'SERVER_PORT': 'server_port',
        'LOG_LEVEL': 'log_level',
        'PROJECT_ID': 'project_id',
        'DEFAULT_CATEGORY_ID': 'default_category_id',
        'DEFAULT_TRACKER_ID': 'default_tracker_id',
    }
    
    for env_var, config_key in env_vars.items():
        env_value = os.environ.get(env_var)
        if env_value is not None:
            # Convert numeric strings to integers
            if config_key in ['server_port', 'project_id', 'default_category_id', 'default_tracker_id']:
                try:
                    env_value = int(env_value)
                except ValueError:
                    logger.warning(f"Could not convert {env_var}='{env_value}' to int")
            
            config[config_key] = env_value
    
    return config

def setup_logging(level=None):
    """
    Set up logging for the application
    
    Args:
        level (str, optional): Log level (e.g., 'INFO', 'DEBUG')
    """
    if not level:
        config = load_config()
        level = config.get('log_level', 'INFO')
    
    logging.basicConfig(
        level=getattr(logging, level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('redmine_mcp.log')
        ]
    )

import json
import os
from pathlib import Path
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class ConfigSetup:
    def __init__(self, config_path="config/config.json", env_path=".env"):
        self.config_path = Path(config_path)
        self.env_path = Path(env_path)
        self.config = self.load_config()

    def load_config(self):
        """Load existing configuration or create default."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Create default config
            default_config = {
                "twitter": {
                    "bearer_token": "",
                    "api_key": "",
                    "api_secret": "",
                    "access_token": "",
                    "access_token_secret": ""
                },
                "news_sources": [
                    "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
                ],
                "posting_schedule": {
                    "interval_hours": 2,
                    "active_hours": {
                        "start": 8,
                        "end": 22
                    }
                },
                "content_settings": {
                    "max_post_length": 280,
                    "controversy_threshold": 0.7,
                    "min_news_age_minutes": 15
                }
            }

            # Write default config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)

            logger.info(f"Created default configuration at {self.config_path}")
            return default_config

    def validate_config(self):
        """Validate the configuration settings."""
        errors = []

        # Get Twitter credentials from environment variables or config
        bearer_token = os.getenv('BEARER_TOKEN') or self.config.get('twitter', {}).get('bearer_token', '')
        api_key = os.getenv('API_KEY') or self.config.get('twitter', {}).get('api_key', '')
        api_secret = os.getenv('API_KEY_SECRET') or self.config.get('twitter', {}).get('api_secret', '')
        access_token = os.getenv('ACCESS_TOKEN') or self.config.get('twitter', {}).get('access_token', '')
        access_token_secret = os.getenv('ACCESS_TOKEN_SECRET') or self.config.get('twitter', {}).get('access_token_secret', '')

        # Check if all required Twitter credentials are provided
        required_fields = [
            ('Bearer Token', bearer_token),
            ('API Key', api_key),
            ('API Secret', api_secret),
            ('Access Token', access_token),
            ('Access Token Secret', access_token_secret)
        ]

        for field_name, field_value in required_fields:
            if not field_value:
                errors.append(f"Missing required Twitter credential: {field_name}")

        # Check news sources
        news_sources = self.config.get('news_sources', [])
        if not news_sources:
            errors.append("No news sources configured")

        # Check content settings
        content_settings = self.config.get('content_settings', {})
        if content_settings.get('max_post_length', 280) > 280:
            errors.append("max_post_length cannot exceed 280 for Twitter")

        if not (0 <= content_settings.get('controversy_threshold', 0.7) <= 1):
            errors.append("controversy_threshold must be between 0 and 1")

        return {
            'valid': len(errors) == 0,
            'errors': errors
        }

    def set_twitter_credentials(self, bearer_token="", api_key="", api_secret="",
                               access_token="", access_token_secret=""):
        """Set Twitter API credentials in both config file and .env file."""
        # Update the in-memory config
        self.config['twitter'] = {
            'bearer_token': bearer_token,
            'api_key': api_key,
            'api_secret': api_secret,
            'access_token': access_token,
            'access_token_secret': access_token_secret
        }

        # Write credentials to .env file
        self.save_credentials_to_env(bearer_token, api_key, api_secret, access_token, access_token_secret)
        
        # Also save to config file as fallback
        self.save_config()
        
        logger.info("Twitter credentials updated in both config file and .env file")

    def save_credentials_to_env(self, bearer_token, api_key, api_secret, access_token, access_token_secret):
        """Save Twitter credentials to .env file."""
        env_content = f"""API_KEY="{api_key}"
API_KEY_SECRET="{api_secret}"
BEARER_TOKEN="{bearer_token}"
ACCESS_TOKEN="{access_token}"
ACCESS_TOKEN_SECRET="{access_token_secret}"
"""
        with open(self.env_path, 'w', encoding='utf-8') as f:
            f.write(env_content)
        
        logger.info(f"Twitter credentials saved to {self.env_path}")
        
        # Reload environment variables
        load_dotenv(self.env_path, override=True)

    def save_config(self):
        """Save configuration to file."""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2)

    def update_setting(self, section, key, value):
        """Update a specific configuration setting."""
        if section in self.config:
            if isinstance(self.config[section], dict):
                self.config[section][key] = value
            else:
                self.config[section] = value
        else:
            self.config[section] = {key: value}

        self.save_config()
        logger.info(f"Updated configuration: {section}.{key} = {value}")

    def get_twitter_credentials(self):
        """Get Twitter API credentials from environment variables with fallback to config."""
        return {
            'bearer_token': os.getenv('BEARER_TOKEN') or self.config.get('twitter', {}).get('bearer_token', ''),
            'api_key': os.getenv('API_KEY') or self.config.get('twitter', {}).get('api_key', ''),
            'api_secret': os.getenv('API_KEY_SECRET') or self.config.get('twitter', {}).get('api_secret', ''),
            'access_token': os.getenv('ACCESS_TOKEN') or self.config.get('twitter', {}).get('access_token', ''),
            'access_token_secret': os.getenv('ACCESS_TOKEN_SECRET') or self.config.get('twitter', {}).get('access_token_secret', '')
        }

def setup_twitter_credentials_interactive():
    """Interactive setup for Twitter API credentials."""
    print("Setting up Twitter API credentials...")
    print("You can get these from https://developer.twitter.com/en/portal/dashboard")
    print()

    bearer_token = input("Enter Bearer Token: ").strip()
    api_key = input("Enter API Key: ").strip()
    api_secret = input("Enter API Secret: ").strip()
    access_token = input("Enter Access Token: ").strip()
    access_token_secret = input("Enter Access Token Secret: ").strip()

    config = ConfigSetup()
    config.set_twitter_credentials(
        bearer_token=bearer_token,
        api_key=api_key,
        api_secret=api_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    # Validate the configuration
    validation = config.validate_config()
    if validation['valid']:
        print("\nConfiguration validated successfully!")
        print("You can now run the bot with: python src/twitter_bot/main.py")
    else:
        print("\nConfiguration has errors:")
        for error in validation['errors']:
            print(f" - {error}")
        print("\nPlease fix these issues before running the bot.")

if __name__ == "__main__":
    setup_twitter_credentials_interactive()
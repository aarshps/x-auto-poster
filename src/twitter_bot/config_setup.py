import json
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ConfigSetup:
    def __init__(self, config_path="config/config.json"):
        self.config_path = Path(config_path)
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
                    "https://rss.cnn.com/rss/edition.rss",
                    "http://feeds.reuters.com/reuters/topNews",
                    "https://rss.ap.org/apis/json/f/APF-Top-News-Use-For-App-Use-Only-1.json",
                    "https://www.theguardian.com/international/rss"
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
        
        # Check Twitter credentials
        twitter_config = self.config.get('twitter', {})
        required_twitter_fields = ['bearer_token', 'api_key', 'api_secret', 'access_token', 'access_token_secret']
        
        for field in required_twitter_fields:
            if not twitter_config.get(field):
                errors.append(f"Missing required Twitter configuration: {field}")
        
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
        """Set Twitter API credentials."""
        self.config['twitter'] = {
            'bearer_token': bearer_token,
            'api_key': api_key,
            'api_secret': api_secret,
            'access_token': access_token,
            'access_token_secret': access_token_secret
        }
        
        self.save_config()
        logger.info("Twitter credentials updated")
    
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
        """Get Twitter API credentials."""
        return self.config.get('twitter', {})

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
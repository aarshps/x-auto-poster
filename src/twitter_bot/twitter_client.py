import tweepy
import logging
from pathlib import Path
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class TwitterClient:
    def __init__(self, config_path="config/config.json"):
        self.config = self.load_config(config_path)
        self.client = self.setup_client()
        
    def load_config(self, config_path):
        """Load configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def setup_client(self):
        """Initialize Twitter API v2 client."""
        try:
            # Get credentials from environment variables with fallback to config file
            bearer_token = os.getenv('BEARER_TOKEN') or self.config['twitter']['bearer_token']
            consumer_key = os.getenv('API_KEY') or self.config['twitter']['api_key']
            consumer_secret = os.getenv('API_KEY_SECRET') or self.config['twitter']['api_secret']
            access_token = os.getenv('ACCESS_TOKEN') or self.config['twitter']['access_token']
            access_token_secret = os.getenv('ACCESS_TOKEN_SECRET') or self.config['twitter']['access_token_secret']
            
            client = tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )
            logger.info("Twitter API client initialized successfully")
            return client
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise
    
    def post_tweet(self, content):
        """Post a tweet to Twitter/X."""
        try:
            # Validate content length
            if len(content) > 280:
                logger.warning(f"Content exceeds 280 characters ({len(content)}). Truncating...")
                content = content[:277] + "..."
            
            response = self.client.create_tweet(text=content)
            tweet_id = response.data['id']
            logger.info(f"Successfully posted tweet with ID: {tweet_id}")
            return {
                'success': True,
                'tweet_id': tweet_id,
                'content': content
            }
        except tweepy.Forbidden as e:
            logger.error(f"Authorization error when posting tweet: {e}")
            return {
                'success': False,
                'error': 'Authorization failed - check API credentials',
                'details': str(e)
            }
        except tweepy.TooManyRequests:
            logger.error("Rate limit exceeded when posting tweet")
            return {
                'success': False,
                'error': 'Rate limit exceeded',
                'details': 'Too many requests'
            }
        except Exception as e:
            logger.error(f"Error posting tweet: {e}")
            return {
                'success': False,
                'error': 'Failed to post tweet',
                'details': str(e)
            }
    
    def verify_credentials(self):
        """Verify Twitter API credentials."""
        try:
            # Get the authenticated user's information
            user = self.client.get_me()
            logger.info(f"Credentials verified. Authenticated as: @{user.data.username}")
            return True
        except Exception as e:
            logger.error(f"Failed to verify credentials: {e}")
            return False
    
    def get_rate_limit_status(self):
        """Get current rate limit status."""
        # Note: Tweepy v4 with API v2 doesn't have a direct rate limit endpoint
        # Rate limits are handled automatically by tweepy, but we can at least provide a general check
        try:
            # Try making a simple API call to check if we're within rate limits
            self.client.get_me()
            logger.info("Rate limit check passed - API is accessible")
            return {'success': True, 'message': 'API accessible'}
        except tweepy.TooManyRequests:
            logger.warning("Rate limit exceeded")
            return {'success': False, 'message': 'Rate limit exceeded'}
        except Exception as e:
            logger.error(f"Error checking rate limit status: {e}")
            return {'success': False, 'message': str(e)}

if __name__ == "__main__":
    # Test the Twitter client
    client = TwitterClient()
    client.verify_credentials()
    
    # Test posting (commented out to avoid actually posting)
    # result = client.post_tweet("This is a test tweet from the X Auto-Poster Bot!")
    # print(result)
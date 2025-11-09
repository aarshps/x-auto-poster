import json
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
from .news_fetcher import NewsFetcher
from .twitter_client import TwitterClient
from utils.qwen_interface import generate_post_content

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XAutoPosterBot:
    def __init__(self, config_path="config/config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.news_fetcher = NewsFetcher(config_path)
        self.twitter_client = TwitterClient(config_path)
        
    def load_config(self):
        """Load configuration from JSON file."""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    

    
    def fetch_news(self):
        """Fetch news using the NewsFetcher class."""
        return self.news_fetcher.fetch_all_news()
    
    def filter_trending_news(self, news_items):
        """Filter for trending and controversial news using NewsFetcher."""
        # Use the NewsFetcher's method to filter trending news
        return self.news_fetcher.filter_trending_news(news_items)
    
    def post_to_x(self, content):
        """Post content to X (Twitter) using TwitterClient."""
        result = self.twitter_client.post_tweet(content)
        return result['success']
    
    def run(self):
        """Main execution loop."""
        logger.info("Starting X Auto-Poster Bot...")
        
        while True:
            try:
                # Check if current time is within active hours
                current_hour = datetime.now().hour
                start_hour = self.config['posting_schedule']['active_hours']['start']
                end_hour = self.config['posting_schedule']['active_hours']['end']
                
                if start_hour <= current_hour <= end_hour:
                    # Fetch latest news
                    news_items = self.fetch_news()
                    logger.info(f"Fetched {len(news_items)} news items")
                    
                    # Filter for trending and controversial news
                    trending_news = self.filter_trending_news(news_items)
                    logger.info(f"Found {len(trending_news)} trending news items")
                    
                    if trending_news:
                        # Select the most trending item
                        selected_news = trending_news[0]
                        
                        # Generate post content using Qwen
                        post_content = generate_post_content(
                            title=selected_news['title'],
                            summary=selected_news['summary'],
                            link=selected_news['link']
                        )
                        
                        # Post to X
                        if post_content and len(post_content) <= self.config['content_settings']['max_post_length']:
                            success = self.post_to_x(post_content)
                            if success:
                                logger.info("Successfully posted to X")
                            else:
                                logger.error("Failed to post to X")
                        else:
                            logger.warning("Generated content is too long or empty")
                    else:
                        logger.info("No trending news found to post")
                else:
                    logger.info(f"Outside active hours ({start_hour}-{end_hour}), skipping posting")
                
                # Wait for next posting interval
                interval_seconds = self.config['posting_schedule']['interval_hours'] * 3600
                logger.info(f"Waiting {interval_seconds} seconds until next check...")
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                logger.info("Bot stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                # Wait before retrying
                time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    bot = XAutoPosterBot()
    bot.run()
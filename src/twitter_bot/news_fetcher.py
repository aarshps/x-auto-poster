import feedparser
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self, config_path="config/config.json"):
        self.config = self.load_config(config_path)

    def load_config(self, config_path):
        """Load configuration from JSON file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def fetch_from_rss(self, rss_url):
        """Fetch news from RSS feed."""
        try:
            # Use requests library instead of urllib for better SSL handling
            response = requests.get(
                rss_url, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                timeout=10,
                verify=False  # Disable SSL verification to avoid SSL issues
            )
            response.raise_for_status()
            
            # Parse the RSS content directly from the response text
            feed = feedparser.parse(response.text)
            articles = []

            logger.info(f"RSS feed has {len(feed.entries)} entries from {rss_url}")
            
            for entry in feed.entries:
                # Skip entries without essential content
                title = entry.get('title', '')
                if not title.strip():
                    logger.debug(f"Skipping entry without title: {entry.keys()}")
                    continue
                
                # Handle cases where summary might be in description instead
                summary = entry.get('summary', '') or entry.get('description', '')
                
                # Handle cases where link might be in different fields
                link = entry.get('link', '')
                if not link and hasattr(entry, 'guid'):
                    link = entry.get('guid', '')
                
                # Check published date
                published_parsed = entry.get('published_parsed') or entry.get('updated_parsed')
                
                article = {
                    'title': title,
                    'summary': summary,
                    'link': link,
                    'published': published_parsed,
                    'source': rss_url
                }

                # Check if we should include this article based on age
                should_include = True  # Default to including if no date

                if article['published']:
                    try:
                        published_datetime = datetime(*article['published'][:6])
                        article['published'] = published_datetime  # Store the datetime object
                        
                        # Check if article is within acceptable age range
                        min_news_age_minutes = int(os.getenv('MIN_NEWS_AGE_MINUTES',
                                                           self.config['content_settings']['min_news_age_minutes']))
                        if datetime.now() - published_datetime > timedelta(minutes=min_news_age_minutes):
                            logger.debug(f"Article '{title}' is too old: {published_datetime}")
                            should_include = False
                    except (TypeError, ValueError, IndexError) as e:
                        logger.warning(f"Could not parse date for article '{title}': {e}")
                        # If we can't parse the date, still include it

                if should_include:
                    articles.append(article)

            logger.info(f"Successfully fetched {len(articles)} articles from {rss_url}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching RSS feed from {rss_url}: {e}")
            return []

    def fetch_from_api(self, api_url, headers=None):
        """Fetch news from API endpoint."""
        try:
            # Add timeout to the API request
            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            articles = []
            # Different APIs have different structures, this is a generic approach
            # For specific APIs like NewsAPI, you'd need to customize the parsing
            if 'articles' in data:
                for item in data['articles']:
                    article = {
                        'title': item.get('title', ''),
                        'summary': item.get('description', ''),
                        'link': item.get('url', ''),
                        'published': self._parse_datetime(item.get('publishedAt', '')),
                        'source': api_url
                    }
                    articles.append(article)

            logger.info(f"Fetched {len(articles)} articles from API {api_url}")
            return articles

        except Exception as e:
            logger.error(f"Error fetching from API {api_url}: {e}")
            return []

    def _parse_datetime(self, datetime_str):
        """Parse datetime string to datetime object."""
        if not datetime_str:
            return None
        try:
            # Handle ISO format: 2023-01-01T12:00:00Z
            return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        except ValueError:
            return None

    def fetch_all_news(self):
        """Fetch news from all configured sources."""
        all_articles = []

        # Fetch from RSS sources
        for source_url in self.config['news_sources']:
            # Treat all sources as RSS since they are RSS feeds
            articles = self.fetch_from_rss(source_url)
            all_articles.extend(articles)

        return all_articles

    def filter_trending_news(self, articles):
        """Filter for trending and controversial news."""
        trending_articles = []

        for article in articles:
            # Estimate controversy score
            controversy_score = self.estimate_controversy(article)

            # Get controversy threshold from environment variable or config
            controversy_threshold = float(os.getenv('CONTROVERSY_THRESHOLD',
                                                  self.config['content_settings']['controversy_threshold']))
            # Only include articles that meet the controversy threshold
            if controversy_score >= controversy_threshold:
                article['controversy_score'] = controversy_score
                trending_articles.append(article)

        # Sort by controversy score and recency
        trending_articles.sort(key=lambda x: (x['controversy_score'], x.get('published', datetime.min)), reverse=True)

        return trending_articles

    def estimate_controversy(self, article):
        """Estimate how controversial an article might be."""
        # This is a simple keyword-based approach
        controversial_keywords = [
            'war', 'conflict', 'protest', 'election', 'scandal', 'corruption',
            'violence', 'controversy', 'debate', 'crisis', 'crackdown', 'ban',
            'protesters', 'unrest', 'tension', 'accusation', 'dispute', 'disagreement',
            'terrorism', 'shootings', 'riots', 'militants', 'dictator', 'authoritarian',
            'censorship', 'human rights', 'freedom', 'opposition', 'repression'
        ]

        text = (article['title'] + ' ' + article['summary']).lower()
        controversy_score = 0

        # Count controversial keywords
        for keyword in controversial_keywords:
            if keyword in text:
                controversy_score += 0.1

        # Increase score for certain high-impact words
        high_impact_words = ['war', 'terrorism', 'crisis', 'scandal', 'corruption', 'shootings', 'riots']
        for word in high_impact_words:
            if word in text:
                controversy_score += 0.2

        # Ensure score is between 0 and 1
        return min(max(controversy_score, 0.0), 1.0)

if __name__ == "__main__":
    fetcher = NewsFetcher()
    articles = fetcher.fetch_all_news()
    trending = fetcher.filter_trending_news(articles)

    print(f"Found {len(articles)} total articles")
    print(f"Found {len(trending)} trending articles")

    for article in trending[:5]:  # Print top 5 trending articles
        print(f"Title: {article['title']}")
        print(f"Controversy Score: {article['controversy_score']:.2f}")
        print("---")
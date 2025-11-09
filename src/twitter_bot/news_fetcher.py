import feedparser
import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import logging

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
            feed = feedparser.parse(rss_url)
            articles = []
            
            for entry in feed.entries:
                article = {
                    'title': entry.get('title', ''),
                    'summary': entry.get('summary', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published_parsed'),
                    'source': rss_url
                }
                
                # Convert published time to datetime object if available
                if article['published']:
                    article['published'] = datetime(*article['published'][:6])
                
                # Only include recent news (within specified time)
                if article['published']:
                    if datetime.now() - article['published'] < timedelta(minutes=self.config['content_settings']['min_news_age_minutes']):
                        articles.append(article)
                else:
                    # If no published time, just add the entry
                    articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles from {rss_url}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {rss_url}: {e}")
            return []
    
    def fetch_from_api(self, api_url, headers=None):
        """Fetch news from API endpoint."""
        try:
            response = requests.get(api_url, headers=headers)
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
            if source_url.endswith('.rss') or 'rss' in source_url:
                articles = self.fetch_from_rss(source_url)
                all_articles.extend(articles)
            else:
                # Assume it's an API endpoint
                articles = self.fetch_from_api(source_url)
                all_articles.extend(articles)
        
        return all_articles
    
    def filter_trending_news(self, articles):
        """Filter for trending and controversial news."""
        trending_articles = []
        
        for article in articles:
            # Estimate controversy score
            controversy_score = self.estimate_controversy(article)
            
            # Only include articles that meet the controversy threshold
            if controversy_score >= self.config['content_settings']['controversy_threshold']:
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
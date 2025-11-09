#!/usr/bin/env python3
"""
Test script for the complete X Auto-Poster workflow
"""
import sys
import os
import time
from datetime import datetime
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

def test_news_fetching():
    """Test the news fetching functionality."""
    print("Testing news fetching...")
    try:
        from src.twitter_bot.news_fetcher import NewsFetcher
        
        fetcher = NewsFetcher()
        articles = fetcher.fetch_all_news()
        
        print(f"✓ Fetched {len(articles)} articles from news sources")
        
        trending_articles = fetcher.filter_trending_news(articles)
        print(f"✓ Found {len(trending_articles)} trending articles")
        
        if trending_articles:
            top_article = trending_articles[0]
            print(f"✓ Top trending article: {top_article['title'][:50]}...")
            print(f"  Controversy score: {top_article.get('controversy_score', 0):.2f}")
        
        return True
    except Exception as e:
        print(f"✗ Error in news fetching: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qwen_integration():
    """Test Qwen integration for content generation."""
    print("\nTesting Qwen integration...")
    try:
        from utils.qwen_interface import generate_post_content
        
        # Test with a sample news item
        title = "Global Climate Summit Reaches Historic Agreement"
        summary = "World leaders have agreed on unprecedented measures to combat climate change, including a commitment to net-zero emissions by 2040."
        
        post = generate_post_content(title, summary)
        
        if post:
            print(f"✓ Generated post: {post[:60]}...")
            print(f"✓ Post length: {len(post)} characters")
            return True
        else:
            print("✗ Failed to generate post content")
            return False
    except Exception as e:
        print(f"✗ Error in Qwen integration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_twitter_client():
    """Test Twitter client (without actually posting)."""
    print("\nTesting Twitter client...")
    try:
        from src.twitter_bot.twitter_client import TwitterClient
        
        # Initialize client
        client = TwitterClient()
        
        # Verify credentials
        success = client.verify_credentials()
        if success:
            print("✓ Twitter credentials verified")
        else:
            print("✗ Failed to verify Twitter credentials")
            return False
        
        # Test rate limit status
        status = client.get_rate_limit_status()
        print(f"✓ Rate limit status: {status['message']}")
        
        return True
    except Exception as e:
        print(f"✗ Error with Twitter client: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_workflow():
    """Test the complete workflow of the bot."""
    print("\nTesting complete workflow...")
    try:
        from src.twitter_bot.main import XAutoPosterBot
        
        print("✓ Successfully imported main bot class")
        
        # We won't run the bot itself, but will test its initialization
        # which checks that all dependencies are available
        bot = XAutoPosterBot()
        print("✓ Bot initialized successfully")
        
        # Test fetching news
        news_items = bot.fetch_news()
        print(f"✓ Fetched {len(news_items)} news items")
        
        # Test filtering trending news
        trending_news = bot.filter_trending_news(news_items)
        print(f"✓ Filtered to {len(trending_news)} trending news items")
        
        # Test content generation with the first trending item if available
        if trending_news:
            sample_news = trending_news[0]
            from utils.qwen_interface import generate_post_content
            post_content = generate_post_content(
                sample_news['title'],
                sample_news['summary'],
                sample_news.get('link')
            )
            
            if post_content:
                print(f"✓ Generated post content: {post_content[:50]}...")
                print(f"  Length: {len(post_content)} characters")
                
                # Test character limit
                if len(post_content) <= 280:
                    print("✓ Post content is within Twitter character limit")
                else:
                    print("✗ Post content exceeds Twitter character limit")
                    return False
            else:
                print("✗ Failed to generate post content")
                return False
        else:
            print("! No trending news to test content generation with")
        
        return True
    except Exception as e:
        print(f"✗ Error in complete workflow: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Running comprehensive tests for X Auto-Poster Bot...")
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    all_tests_passed = True
    
    # Run all tests
    tests = [
        ("News Fetching", test_news_fetching),
        ("Qwen Integration", test_qwen_integration),
        ("Twitter Client", test_twitter_client),
        ("Complete Workflow", test_complete_workflow),
    ]
    
    for test_name, test_func in tests:
        print(f"\n[{test_name}]")
        success = test_func()
        if success:
            print(f"✓ {test_name} test PASSED")
        else:
            print(f"✗ {test_name} test FAILED")
            all_tests_passed = False
        time.sleep(1)  # Small delay between tests
    
    print("\n" + "="*60)
    if all_tests_passed:
        print("🎉 All tests PASSED! The X Auto-Poster Bot is ready to run.")
        print("\nTo start the bot, run: python src/twitter_bot/main.py")
    else:
        print("❌ Some tests FAILED. Please fix the issues before running the bot.")
        sys.exit(1)

if __name__ == "__main__":
    main()
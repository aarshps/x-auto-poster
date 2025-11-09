#!/usr/bin/env python3
"""
Simple test to verify module imports work correctly
"""
import sys
import os
from pathlib import Path

# Add the project root to the path so we can import modules
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported without errors."""
    print("Testing module imports...")
    
    success = True
    
    modules_to_test = [
        ('News Fetcher', 'src.twitter_bot.news_fetcher'),
        ('Twitter Client', 'src.twitter_bot.twitter_client'),
        ('Config Setup', 'src.twitter_bot.config_setup'),
        ('Qwen Interface', 'utils.qwen_interface'),
    ]
    
    for name, module_path in modules_to_test:
        try:
            __import__(module_path)
            print(f"✓ {name} module imported successfully")
        except ImportError as e:
            print(f"✗ {name} module import failed: {e}")
            success = False
    
    return success

def test_qwen_interface():
    """Test that the Qwen interface can be called."""
    print("\nTesting Qwen interface...")
    try:
        from utils.qwen_interface import generate_post_content
        
        # Test with a simple input
        title = "Test News Title"
        summary = "This is a test news summary to demonstrate the Qwen interface."
        
        # This will actually call Qwen CLI and generate content
        result = generate_post_content(title, summary)
        
        if result:
            print(f"✓ Qwen interface works: {result[:50]}...")
            print(f"  Length: {len(result)} characters")
            return True
        else:
            print("✗ Qwen interface returned None")
            return False
    except Exception as e:
        print(f"✗ Error testing Qwen interface: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("Testing X Auto-Poster Bot modules...")
    print("="*50)
    
    all_passed = True
    
    # Test imports
    if test_imports():
        print("\n✓ All modules imported successfully!")
    else:
        print("\n✗ Some modules failed to import!")
        all_passed = False
    
    # Test Qwen interface
    if test_qwen_interface():
        print("\n✓ Qwen interface works correctly!")
    else:
        print("\n✗ Qwen interface has issues!")
        all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("✅ All basic tests passed!")
        print("\nYou can now run the full bot with: python -c \"from src.twitter_bot.main import XAutoPosterBot; bot = XAutoPosterBot(); bot.run()\"")
    else:
        print("❌ Some tests failed!")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Test script for Qwen integration
"""
import sys
import os
# Add the project root to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.qwen_interface import generate_post_content

def test_qwen_integration():
    print("Testing Qwen integration...")
    
    # Test with sample news
    title = "Major Breakthrough in Renewable Energy Storage Announced"
    summary = "Scientists have developed a new battery technology that could revolutionize renewable energy storage, promising 3x longer life and significantly reduced costs."
    
    post = generate_post_content(title, summary)
    
    if post:
        print(f"Successfully generated post:")
        print(f"Content: {post}")
        print(f"Length: {len(post)} characters")
    else:
        print("Failed to generate post content")
        
if __name__ == "__main__":
    test_qwen_integration()
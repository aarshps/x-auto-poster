import subprocess
import json
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def generate_post_content(title, summary, link=None):
    """
    Generate engaging X post content based on news title and summary using Qwen CLI.
    
    Args:
        title (str): News title
        summary (str): News summary/description
        link (str, optional): News article link
    
    Returns:
        str: Generated post content (max 280 characters for X)
    """
    try:
        # Create a prompt for Qwen to generate an engaging post
        prompt = f"""
        Create an engaging, concise X (Twitter) post (max 260 characters) about this news:
        Title: {title}
        Summary: {summary}
        
        Requirements:
        - Make it attention-grabbing and shareable
        - Include relevant hashtags (max 2-3)
        - Keep it under 260 characters to allow for potential link
        - Make it sound natural and not clickbaity
        - Include an opinion or reaction that would encourage engagement
        - If a link is provided, mention it appropriately
        """
        
        # Execute Qwen CLI to generate content
        result = subprocess.run([
            'qwen', 
            '-p',  # Use prompt mode
            prompt
        ], 
        capture_output=True, 
        text=True, 
        timeout=30  # 30 second timeout
        )
        
        if result.returncode == 0:
            generated_content = result.stdout.strip()
            
            # Clean up the response (remove potential prefixes like "Response:" or "Sure, here's...")
            lines = generated_content.split('\n')
            # Look for the most relevant content line, typically the first substantial one
            for line in lines:
                line = line.strip()
                if line and len(line) > 20 and not line.startswith(('Response:', 'Sure,', 'Here', 'Okay')):
                    generated_content = line
                    break
            
            # Ensure it's within X's character limit (280)
            if len(generated_content) > 280:
                generated_content = generated_content[:277] + "..."
            
            logger.info(f"Generated post: {generated_content}")
            return generated_content
        else:
            logger.error(f"Qwen CLI error: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        logger.error("Qwen CLI call timed out")
        return None
    except Exception as e:
        logger.error(f"Error calling Qwen CLI: {e}")
        return None

def enhance_post_with_qwen(post_content, context_info):
    """
    Enhance existing post content using Qwen for better engagement.
    
    Args:
        post_content (str): Initial post content
        context_info (dict): Additional context information
    
    Returns:
        str: Enhanced post content
    """
    try:
        prompt = f"""
        Enhance this X (Twitter) post to make it more engaging:
        Original post: {post_content}
        
        Additional context: {context_info}
        
        Requirements:
        - Improve engagement potential
        - Keep under 280 characters
        - Make it more compelling to read and share
        - Add appropriate tone based on the content
        """
        
        result = subprocess.run([
            'qwen',
            '-p',
            prompt
        ],
        capture_output=True,
        text=True,
        timeout=30
        )
        
        if result.returncode == 0:
            enhanced_content = result.stdout.strip()
            
            # Clean up the response similar to above
            lines = enhanced_content.split('\n')
            for line in lines:
                line = line.strip()
                if line and len(line) > 20 and not line.startswith(('Response:', 'Sure,', 'Here', 'Okay')):
                    enhanced_content = line
                    break
            
            if len(enhanced_content) > 280:
                enhanced_content = enhanced_content[:277] + "..."
            
            return enhanced_content
        else:
            logger.error(f"Qwen CLI enhancement error: {result.stderr}")
            return post_content  # Return original if enhancement fails
            
    except Exception as e:
        logger.error(f"Error enhancing post with Qwen: {e}")
        return post_content  # Return original if enhancement fails

if __name__ == "__main__":
    # Test the function
    test_title = "Global Climate Summit Reaches Historic Agreement"
    test_summary = "World leaders have agreed on unprecedented measures to combat climate change, including a commitment to net-zero emissions by 2040."
    
    post = generate_post_content(test_title, test_summary)
    print(f"Generated post: {post}")
    print(f"Character count: {len(post) if post else 0}")
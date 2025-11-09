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
        # Create a prompt for Qwen to generate an engaging post with specific requirements
        prompt = f"""
        Create an engaging, concise X (Twitter) post (max 260 characters) about this news:
        Title: {title}
        Summary: {summary}

        Requirements:
        - Use simple, clear English
        - Avoid GenZ slang, internet abbreviations, and trendy phrases
        - Do not use emojis
        - Do not use first-person language (avoid 'I', 'my', 'me')
        - Make it attention-grabbing and shareable
        - Include relevant hashtags (max 2-3)
        - Keep it under 260 characters to allow for potential link
        - Make it sound professional and not clickbaity
        - Include an opinion or reaction that would encourage engagement
        - If a link is provided, mention it appropriately
        """

        # Execute Qwen CLI to generate content in non-interactive mode
        # On Windows, use the shell=True to properly execute .cmd files
        import platform
        if platform.system() == "Windows":
            result = subprocess.run(
                f'qwen -p "{prompt}"',
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
        else:
            result = subprocess.run(
                ['qwen', '-p', prompt],
                capture_output=True,
                text=True,
                timeout=30
            )

        if result.returncode == 0:
            generated_content = result.stdout.strip()

            # Clean up the response (remove potential prefixes like "Response:" or "Sure, here's...")
            lines = generated_content.split('\n')
            # Look for the most relevant content line, typically the first substantial one
            for line in lines:
                line = line.strip()
                if line and len(line) > 20 and not line.startswith(('Response:', 'Sure,', 'Here', 'Okay', 'Generated')):
                    generated_content = line
                    break

            # Remove emojis if any
            generated_content = remove_emojis(generated_content)
            
            # Ensure it's within X's character limit (280)
            if len(generated_content) > 280:
                generated_content = generated_content[:277] + "..."

            logger.info(f"Generated post: {generated_content}")
            return generated_content
        else:
            logger.error(f"Qwen CLI error: {result.stderr}")
            # Fallback: create a simple post format
            return create_simple_post(title, summary, link)

    except subprocess.TimeoutExpired:
        logger.error("Qwen CLI call timed out")
        # Fallback: create a simple post format
        return create_simple_post(title, summary, link)
    except Exception as e:
        logger.error(f"Error calling Qwen CLI: {e}")
        # Fallback: create a simple post format
        return create_simple_post(title, summary, link)

def create_simple_post(title, summary, link=None):
    """
    Create a simple fallback post when Qwen CLI is not available.
    
    Args:
        title (str): News title
        summary (str): News summary/description
        link (str, optional): News article link
    
    Returns:
        str: Simple formatted post content
    """
    import os
    
    # Get the max post length from environment variable with a default of 280
    max_post_length = int(os.getenv('MAX_POST_LENGTH', 280))
    
    # Extract a short summary for the post
    clean_title = title.strip()
    
    if link:
        # Create a post with link and truncate as needed
        post = f"{clean_title} Read more: {link}"
        # If too long, truncate the title
        if len(post) > max_post_length:
            available_length = max_post_length - len("... Read more: ") - len(link)
            if available_length > 10:  # Ensure we have some title
                post = f"{clean_title[:available_length]}... Read more: {link}"
            else:
                # If link is too long for the limit, just use title
                post = clean_title[:max_post_length-3] + "..."
    else:
        # Create a post without link
        post = clean_title
        if len(post) > max_post_length:
            post = post[:max_post_length-3] + "..."
    
    logger.info(f"Generated fallback post: {post}")
    return post

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
        - Use simple, clear English
        - Avoid GenZ slang, internet abbreviations, and trendy phrases
        - Do not use emojis
        - Do not use first-person language (avoid 'I', 'my', 'me')
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
                if line and len(line) > 20 and not line.startswith(('Response:', 'Sure,', 'Here', 'Okay', 'Generated')):
                    enhanced_content = line
                    break

            # Remove emojis if any
            enhanced_content = remove_emojis(enhanced_content)
            
            if len(enhanced_content) > 280:
                enhanced_content = enhanced_content[:277] + "..."

            return enhanced_content
        else:
            logger.error(f"Qwen CLI enhancement error: {result.stderr}")
            return post_content  # Return original if enhancement fails

    except Exception as e:
        logger.error(f"Error enhancing post with Qwen: {e}")
        return post_content  # Return original if enhancement fails

def remove_emojis(text):
    """
    Remove emojis from text.
    """
    # This is a basic approach to remove common emojis by filtering out characters
    # that are likely to be emojis based on their Unicode ranges
    import re
    # Regular expression pattern for various emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002500-\U00002BEF"  # chinese char
        "\U00002702-\U000027B0"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001f926-\U0001f937"
        "\U00010000-\U0010ffff"
        "\u2640-\u2642"
        "\u2600-\u2B55"
        "\u200d"
        "\u23cf"
        "\u23e9"
        "\u231a"
        "\ufe0f"  # dingbats
        "\u3030"
        "]+", 
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)

if __name__ == "__main__":
    # Test the function
    test_title = "Global Climate Summit Reaches Historic Agreement"
    test_summary = "World leaders have agreed on unprecedented measures to combat climate change, including a commitment to net-zero emissions by 2040."

    post = generate_post_content(test_title, test_summary)
    print(f"Generated post: {post}")
    print(f"Character count: {len(post) if post else 0}")
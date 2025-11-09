# X Auto-Poster Bot

This bot automatically creates X (formerly Twitter) posts based on the latest trending news around the world. It uses Qwen CLI for content generation and intelligently selects controversial and trending topics.

## Features

- Fetches latest trending news from multiple sources
- Uses Qwen LLM to generate engaging posts
- Automatically posts to X (Twitter)
- Configurable posting schedule

## Requirements

- Python 3.8+
- Qwen CLI
- Twitter/X API v2 credentials

## Installation

### Using Virtual Environment (Recommended)

1. Create and set up the virtual environment:
```bash
python setup_venv.py
```

2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

3. Run the configuration setup script:
```bash
python src/twitter_bot/config_setup.py
```

### Alternative: Direct Installation

If you prefer not to use a virtual environment:
```bash
pip install -r requirements.txt
```

## Configuration

1. First, you'll need to get Twitter API credentials from [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)

2. Run the configuration setup script:
```bash
python src/twitter_bot/config_setup.py
```
This will guide you through setting up your Twitter API credentials.

3. Alternatively, manually edit `config/config.json` with your API credentials:
```json
{
  "twitter": {
    "bearer_token": "your_bearer_token",
    "api_key": "your_api_key",
    "api_secret": "your_api_secret",
    "access_token": "your_access_token",
    "access_token_secret": "your_access_token_secret"
  }
  // ... rest of the config
}
```

## Usage

### With Virtual Environment

1. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

2. Run the bot:
```bash
python src/twitter_bot/main.py
```

### Without Virtual Environment
```bash
python src/twitter_bot/main.py
```

## How it Works

1. The bot fetches news from configured RSS feeds and API sources
2. It identifies trending and controversial topics based on keyword analysis
3. Using Qwen CLI, it generates engaging social media content
4. Posts the content to X (Twitter) at configured intervals
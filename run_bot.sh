#!/bin/bash
# Shell script to run the X Auto-Poster Bot with virtual environment

echo "Activating virtual environment and starting X Auto-Poster Bot..."

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Error: Virtual environment not found."
    echo "Run 'python setup_venv.py' first to create the virtual environment."
    exit 1
fi

# Activate the virtual environment and run the bot
source venv/bin/activate
python src/twitter_bot/main.py
#!/usr/bin/env python3
"""
Setup script for X Auto-Poster Bot
"""
import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required Python packages."""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully!")

def setup_configuration():
    """Run the configuration setup."""
    print("\nSetting up configuration...")
    config_script = Path("src") / "twitter_bot" / "config_setup.py"
    
    if config_script.exists():
        # Run the config setup interactively
        print("Please enter your Twitter API credentials when prompted:")
        subprocess.check_call([sys.executable, str(config_script)])
    else:
        print(f"Configuration script not found at {config_script}")

def verify_qwen_cli():
    """Verify that Qwen CLI is available."""
    print("\nVerifying Qwen CLI...")
    try:
        result = subprocess.run(["qwen", "--version"], 
                              capture_output=True, 
                              text=True, 
                              timeout=10)
        if result.returncode == 0:
            print(f"Qwen CLI is available: {result.stdout.strip()}")
            return True
        else:
            print("Error: Qwen CLI is not available or not in PATH")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print("Error: Qwen CLI is not available or not in PATH")
        return False

def main():
    print("Setting up X Auto-Poster Bot...")
    print("Note: For best results, use the virtual environment setup:")
    print("  python setup_venv.py")
    print()
    
    # Install dependencies
    install_dependencies()
    
    # Verify Qwen CLI
    if not verify_qwen_cli():
        print("\nPlease install Qwen CLI before continuing.")
        print("Visit: https://github.com/QwenLM/Qwen to set up Qwen CLI")
        return
    
    # Setup configuration
    setup_configuration()
    
    print("\nSetup complete! You can now run the bot with:")
    print("python src/twitter_bot/main.py")
    print()
    print("For virtual environment usage (recommended), see README.md")

if __name__ == "__main__":
    main()
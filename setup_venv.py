#!/usr/bin/env python3
"""
Setup script for X Auto-Poster Bot with virtual environment
"""
import os
import sys
import subprocess
import venv
from pathlib import Path

def create_virtual_environment():
    """Create a virtual environment for the project."""
    print("Creating virtual environment...")
    venv_path = Path("venv")
    
    # Create virtual environment
    venv.create(venv_path, with_pip=True)
    print(f"Virtual environment created at {venv_path}")
    
    return venv_path

def install_dependencies(venv_path):
    """Install required Python packages in the virtual environment."""
    print("Installing dependencies in virtual environment...")
    
    # Determine the path to pip in the virtual environment
    if sys.platform.startswith('win'):
        pip_path = venv_path / 'Scripts' / 'pip.exe'
    else:
        pip_path = venv_path / 'bin' / 'pip'
    
    subprocess.check_call([str(pip_path), "install", "-r", "requirements.txt"])
    print("Dependencies installed successfully in virtual environment!")

def setup_virtual_environment():
    """Full setup process with virtual environment."""
    print("Setting up X Auto-Poster Bot with virtual environment...")
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    
    # Install dependencies
    install_dependencies(venv_path)
    
    print("\nVirtual environment setup complete!")
    print(f"Virtual environment location: {venv_path}")
    
    if sys.platform.startswith('win'):
        print("To activate the virtual environment, run:")
        print(f"    {venv_path}\\Scripts\\activate")
    else:
        print("To activate the virtual environment, run:")
        print(f"    source {venv_path}/bin/activate")
    
    print("\nAfter activating the virtual environment, you can run the bot with:")
    print("    python src/twitter_bot/main.py")
    
    return venv_path

if __name__ == "__main__":
    setup_virtual_environment()
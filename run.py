#!/usr/bin/env python3
"""
Startup script for Video Narrator Pro
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / 'src'
sys.path.append(str(src_path))

# Check for .env file
env_path = Path(__file__).parent / '.env'
if not env_path.exists():
    print("Warning: .env file not found. Creating template...")
    with open(env_path, 'w') as f:
        f.write("OPENAI_API_KEY=your-api-key-here")
    print("Please edit .env file and add your OpenAI API key before running.")
    sys.exit(1)

try:
    from src.main import VideoNarratorApp
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("\nPlease ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

def main():
    try:
        app = VideoNarratorApp()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
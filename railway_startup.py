#!/usr/bin/env python3
"""
Railway startup script to download NLTK data and create directories
"""
import nltk
import os

def download_nltk_data():
    """Download required NLTK data"""
    try:
        # Download required NLTK data
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        print("NLTK data downloaded successfully")
    except Exception as e:
        print(f"Warning: Could not download NLTK data: {e}")

def create_directories():
    """Create necessary directories"""
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs('uploads', exist_ok=True)
        print("Directories created successfully")
    except Exception as e:
        print(f"Warning: Could not create directories: {e}")

if __name__ == "__main__":
    download_nltk_data()
    create_directories()

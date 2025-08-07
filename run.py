#!/usr/bin/env python3
"""
Candidate Recommendation Engine - Startup Script
"""

import os
import sys
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'sentence_transformers',
        'numpy',
        'sklearn',
        'openai',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        if importlib.util.find_spec(package) is None:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nTo install missing packages, run:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    print("✅ All required packages are installed")

def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠️  Warning: .env file not found")
        print("   The application will work without OpenAI API key, but AI summaries will be disabled")
        print("   To enable AI summaries, create a .env file with your OpenAI API key")
        print("   See env_example.txt for reference")
    else:
        print("✅ Environment file found")

def create_upload_folder():
    """Create uploads folder if it doesn't exist"""
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
        print("✅ Created uploads folder")
    else:
        print("✅ Uploads folder exists")

def main():
    """Main startup function"""
    print("🚀 Starting Candidate Recommendation Engine...")
    print("=" * 50)
    
    # Run checks
    check_python_version()
    check_dependencies()
    check_env_file()
    create_upload_folder()
    
    print("\n" + "=" * 50)
    print("🎯 Starting the application...")
    print("📱 Open your browser and go to: http://localhost:8080")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    # Import and run the Flask app
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 
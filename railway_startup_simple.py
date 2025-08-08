#!/usr/bin/env python3
"""
Simple Railway startup script for lightweight deployment
"""
import os
import sys

def create_directories():
    """Create necessary directories"""
    try:
        print("Creating directories...")
        # Create uploads directory if it doesn't exist
        os.makedirs('uploads', exist_ok=True)
        print("✅ Directories created successfully")
        return True
    except Exception as e:
        print(f"⚠️ Warning: Could not create directories: {e}")
        return False

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['OPENAI_API_KEY', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️ Warning: Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("✅ All required environment variables are set")
        return True

if __name__ == "__main__":
    print("🚀 Starting Railway deployment setup (Simple)...")
    
    # Check environment
    env_ok = check_environment()
    
    # Create directories
    dir_ok = create_directories()
    
    print("🎯 Railway setup completed!")
    
    # Exit with error if critical components failed
    if not dir_ok:
        print("❌ Critical error: Could not create directories")
        sys.exit(1)
    
    print("✅ Ready to start application")

#!/usr/bin/env python3
"""
Test script to verify app can start properly
"""
import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test basic imports
        import flask
        print("✅ Flask imported successfully")
        
        import numpy
        print("✅ NumPy imported successfully")
        
        import sklearn
        print("✅ Scikit-learn imported successfully")
        
        # Test app-specific imports
        from skill_extractor import skill_extractor
        print("✅ Skill extractor imported successfully")
        
        # Test app creation
        from app_simple import app
        print("✅ App created successfully")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\nTesting environment...")
    
    port = os.environ.get('PORT', '8080')
    print(f"✅ PORT: {port}")
    
    openai_key = os.environ.get('OPENAI_API_KEY')
    if openai_key:
        print(f"✅ OPENAI_API_KEY: {openai_key[:10]}...")
    else:
        print("⚠️ OPENAI_API_KEY not set")
    
    secret_key = os.environ.get('SECRET_KEY')
    if secret_key:
        print(f"✅ SECRET_KEY: {secret_key[:10]}...")
    else:
        print("⚠️ SECRET_KEY not set")

if __name__ == "__main__":
    print("🚀 Testing app startup...")
    
    test_environment()
    success = test_imports()
    
    if success:
        print("\n🎯 App is ready to start!")
        sys.exit(0)
    else:
        print("\n❌ App has issues!")
        sys.exit(1)

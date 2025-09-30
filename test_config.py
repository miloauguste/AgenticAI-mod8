#!/usr/bin/env python3
"""
Test script to verify Google API key configuration
"""

import os
from dotenv import load_dotenv

def test_api_key_loading():
    print("🔍 Testing Google API Key Configuration...")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    env_file = ".env"
    if os.path.exists(env_file):
        print(f"✅ .env file found: {env_file}")
    else:
        print(f"❌ .env file not found: {env_file}")
        return False
    
    # Try to read API key
    api_key = os.getenv('GOOGLE_API_KEY')
    mock_mode = os.getenv('MOCK_EXTERNAL_APIS', 'false').lower() == 'true'
    
    print(f"🔑 GOOGLE_API_KEY: {'***' + api_key[-4:] if api_key and len(api_key) > 4 else 'Not set or too short'}")
    print(f"🎭 MOCK_EXTERNAL_APIS: {mock_mode}")
    
    # Check configuration validity
    if not api_key or api_key == "your_google_gemini_api_key_here":
        if mock_mode:
            print("⚠️  No real API key, but MOCK mode is enabled - this is OK for testing")
            return True
        else:
            print("❌ No valid API key found and MOCK mode is disabled")
            print("   Please set your Google API key in the .env file")
            return False
    else:
        print("✅ API key appears to be configured")
        return True

def test_config_loading():
    print("\n🔧 Testing Configuration Loading...")
    print("=" * 50)
    
    try:
        from config import get_config
        config = get_config()
        
        print(f"✅ Configuration loaded successfully")
        print(f"📱 App Name: {config.APP_NAME}")
        print(f"🔢 Version: {config.APP_VERSION}")
        print(f"🔑 API Key: {'Set' if config.GOOGLE_API_KEY else 'Not set'}")
        print(f"🎭 Mock Mode: {config.MOCK_EXTERNAL_APIS}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return False

def main():
    print("🔬 MediSyn Labs - Configuration Test")
    print("=" * 50)
    
    # Test 1: API key loading
    api_test = test_api_key_loading()
    
    # Test 2: Configuration loading
    config_test = test_config_loading()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    
    if api_test and config_test:
        print("✅ All tests passed! Configuration is working correctly.")
        print("\n🚀 You can now run the application:")
        print("   python main.py --web")
    else:
        print("❌ Some tests failed. Please check the issues above.")
        print("\n🔧 Quick fixes:")
        print("   1. Make sure .env file exists")
        print("   2. Set GOOGLE_API_KEY in .env file")
        print("   3. Or set MOCK_EXTERNAL_APIS=true for testing")

if __name__ == "__main__":
    main()
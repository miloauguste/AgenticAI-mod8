#!/usr/bin/env python3
"""
Test Google AI API key with simple HTTP request
"""

import os
import requests
from dotenv import load_dotenv

def test_api_key():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("No API key found")
        return
    
    print(f"Testing API key: {api_key[:10]}...")
    
    # Test with a simple REST API call
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Available models:")
            for model in data.get('models', []):
                name = model.get('name', 'Unknown')
                print(f"- {name}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api_key()
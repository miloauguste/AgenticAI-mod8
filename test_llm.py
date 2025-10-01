#!/usr/bin/env python3
"""
Simple test script to verify Google AI API is working
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_direct_genai():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("No API key found")
        return False
    
    print(f"API key found: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        print("API configured successfully")
        
        # Try different model names - using actually available models
        model_names = ['models/gemini-2.5-flash', 'models/gemini-2.5-pro', 'models/gemini-2.0-flash']
        
        for model_name in model_names:
            try:
                print(f"Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                
                # Test with a simple prompt
                response = model.generate_content("Hello, how are you?")
                print(f"{model_name} works! Response: {response.text[:50]}...")
                return True
                
            except Exception as e:
                print(f"{model_name} failed: {e}")
                continue
        
        print("No models worked")
        return False
        
    except Exception as e:
        print(f"API configuration failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Google AI API...")
    test_direct_genai()
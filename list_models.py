#!/usr/bin/env python3
"""
List available models for Google AI API
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def list_available_models():
    load_dotenv()
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("No API key found")
        return
    
    print(f"API key found: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        print("API configured successfully")
        
        print("\nListing available models...")
        models = genai.list_models()
        
        print("Available models:")
        for model in models:
            print(f"- Name: {model.name}")
            print(f"  Display Name: {model.display_name}")
            print(f"  Supported methods: {model.supported_generation_methods}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_available_models()
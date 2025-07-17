#!/usr/bin/env python3
"""
Test Azure OpenAI with API key authentication
"""

import os
import json
import requests
from pathlib import Path
from dotenv import load_dotenv


def test_azure_api_key():
    # Load environment
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    api_base = os.getenv("OPENAI_API_BASE")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    
    if not api_base:
        print("Error: OPENAI_API_BASE not set")
        return
    
    if not api_key:
        print("Error: AZURE_OPENAI_API_KEY not set")
        print("Please run: export AZURE_OPENAI_API_KEY=\"your-key-here\"")
        return
    
    # Your deployment name
    deployment = "gpt-4.1_2025-04-14_DZ-EU"
    
    # Construct URL
    url = f"{api_base}/openai/deployments/{deployment}/chat/completions?api-version=2025-04-01-preview"
    
    # Headers for API key auth
    headers = {
        "api-key": api_key,  # Note: Azure uses "api-key" header, not "Authorization"
        "Content-Type": "application/json"
    }
    
    # Test payload
    data = {
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 10
    }
    
    print(f"Testing URL: {url}")
    print(f"API Key (first 10 chars): {api_key[:10]}...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"\nStatus: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Success! API key authentication is working")
            result = response.json()
            print(f"Response: {result['choices'][0]['message']['content']}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")


if __name__ == "__main__":
    test_azure_api_key()
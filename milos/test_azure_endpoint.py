#!/usr/bin/env python3
"""
Test Azure OpenAI endpoint directly to verify connectivity and auth
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv
from get_azure_token import get_azure_token


def test_azure_endpoint():
    """Test the Azure OpenAI endpoint directly."""
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    # Get the Azure token
    print("Obtaining Azure AD token...")
    try:
        token = get_azure_token(env_path)
        print("✓ Token obtained successfully")
    except Exception as e:
        print(f"Failed to get Azure token: {e}")
        return 1
    
    # Get API base
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("Error: OPENAI_API_BASE not found in .env")
        return 1
    
    # Test with a simple chat completion request
    url = f"{api_base}/openai/deployments/gpt-4/chat/completions?api-version=2025-04-01-preview"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messages": [{"role": "user", "content": "Say 'Hello from Azure'"}],
        "max_tokens": 10
    }
    
    print(f"\nTesting endpoint: {url}")
    print(f"Token (first 20 chars): {token[:20]}...")
    
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"\nResponse status: {response.status_code}")
        
        if response.status_code == 200:
            print("✓ Azure OpenAI is working!")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(test_azure_endpoint())
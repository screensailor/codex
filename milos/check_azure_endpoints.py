#!/usr/bin/env python3
"""
Check what kind of Azure endpoint we're dealing with
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def analyze_endpoint():
    # Load environment
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    api_base = os.getenv("OPENAI_API_BASE")
    print(f"Current endpoint: {api_base}")
    print()
    
    if "apim" in api_base or "api-management" in api_base:
        print("✓ This appears to be an API Management (APIM) endpoint")
        print("  APIM endpoints often require Bearer token authentication")
        print()
    
    if ".openai.azure.com" in api_base:
        print("✓ This appears to be a direct Azure OpenAI endpoint")
        print("  These typically support API key authentication")
        print()
    
    print("Typical Azure OpenAI endpoints look like:")
    print("  https://<resource-name>.openai.azure.com/")
    print()
    print("API Management endpoints look like:")
    print("  https://<apim-name>.azure-api.net/")
    print()
    
    print("Your options:")
    print("1. If you have a direct Azure OpenAI endpoint (not through APIM),")
    print("   update OPENAI_API_BASE in your .env file")
    print()
    print("2. Continue using Azure AD tokens with the APIM endpoint")
    print("   (but Codex CLI doesn't support this natively)")
    print()
    print("3. Check if your APIM can be configured to accept API keys")
    print("   (your IT/Azure admin would need to do this)")


if __name__ == "__main__":
    analyze_endpoint()
#!/usr/bin/env python3
"""
Setup script for using Azure OpenAI with API keys (instead of Azure AD tokens)
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv


def setup_azure_with_api_key():
    """Setup Codex to use Azure OpenAI with API key authentication."""
    
    # Load .env to get the base URL
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("Error: OPENAI_API_BASE not found in .env")
        return 1
    
    # Ensure it ends with /openai
    if not api_base.endswith("/openai"):
        api_base = f"{api_base}/openai"
    
    # Create ~/.codex directory
    codex_home = Path.home() / ".codex"
    codex_home.mkdir(exist_ok=True)
    
    # Create config.json
    config = {
        "model": "gpt-4",  # Change to your deployment name
        "provider": "azure",
        "providers": {
            "azure": {
                "name": "AzureOpenAI",
                "baseURL": api_base,
                "envKey": "AZURE_OPENAI_API_KEY"
            }
        }
    }
    
    config_path = codex_home / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Created {config_path}")
    print(f"✓ Azure endpoint: {api_base}")
    
    print("\n" + "="*50)
    print("SETUP COMPLETE!")
    print("="*50)
    
    print("\nNext steps:")
    print("1. Click 'Show Keys' in Azure Portal")
    print("2. Copy one of the keys (KEY 1 or KEY 2)")
    print("3. Run these commands:\n")
    
    print("   export AZURE_OPENAI_API_KEY=\"<paste-your-key-here>\"")
    print("   export OPENAI_API_KEY=$AZURE_OPENAI_API_KEY")
    print("   codex \"hello, what model are you using?\"\n")
    
    print("Or add to your ~/.zshrc or ~/.bashrc:")
    print("   export AZURE_OPENAI_API_KEY=\"<your-key>\"")
    print("   export OPENAI_API_KEY=$AZURE_OPENAI_API_KEY")
    
    return 0


if __name__ == "__main__":
    exit(setup_azure_with_api_key())
#!/usr/bin/env python3
"""
Setup Azure configuration for Codex CLI based on Microsoft's blog post
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv


def setup_azure_config():
    """Create ~/.codex/config.json with Azure settings."""
    # Load environment variables
    env_path = Path(__file__).parent / ".env"
    load_dotenv(env_path)
    
    # Get OPENAI_API_BASE from .env
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("Error: OPENAI_API_BASE not found in .env")
        return 1
    
    # Create config directory
    codex_home = Path.home() / ".codex"
    codex_home.mkdir(exist_ok=True)
    
    # Create config.json based on Microsoft's blog format
    config = {
        "model": "gpt-4",  # Change this to your deployment name
        "provider": "azure",
        "providers": {
            "azure": {
                "name": "AzureOpenAI",
                "baseURL": api_base,
                "envKey": "AZURE_OPENAI_API_KEY"
            }
        },
        "history": {
            "maxSize": 1000,
            "saveHistory": True,
            "sensitivePatterns": []
        }
    }
    
    # Write config file
    config_path = codex_home / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Created {config_path}")
    print("\nNow run:")
    print("  export AZURE_OPENAI_API_KEY=$(uv run get-azure-token)")
    print("  export OPENAI_API_KEY=$AZURE_OPENAI_API_KEY")
    print("  codex 'your prompt here'")
    
    return 0


if __name__ == "__main__":
    exit(setup_azure_config())
#!/usr/bin/env python3
"""
Wrapper for Node.js version of Codex with Azure AD authentication
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from get_azure_token import get_azure_token


def run_codex_nodejs(args: List[str], env_path: Optional[Path] = None) -> int:
    """Run Node.js Codex CLI with Azure AD authentication."""
    # Load environment variables
    if env_path is None:
        env_path = Path(__file__).parent / ".env"
    
    load_dotenv(env_path)
    
    # Get the Azure token
    print("Obtaining Azure AD token...", file=sys.stderr)
    try:
        token = get_azure_token(env_path)
        print("✓ Token obtained successfully", file=sys.stderr)
    except Exception as e:
        print(f"Failed to get Azure token: {e}", file=sys.stderr)
        return 1
    
    # Get OPENAI_API_BASE from .env
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("Error: OPENAI_API_BASE not found in .env", file=sys.stderr)
        return 1
    
    # Extract deployment name from arguments
    model_name = None
    filtered_args = []
    i = 0
    while i < len(args):
        if args[i] in ["--model", "-m"] and i + 1 < len(args):
            model_name = args[i + 1]
            filtered_args.extend([args[i], args[i + 1]])
            i += 2
        elif args[i].startswith("--model="):
            model_name = args[i].split("=", 1)[1]
            filtered_args.append(args[i])
            i += 1
        else:
            filtered_args.append(args[i])
            i += 1
    
    # First, create/update the config file with Azure settings
    codex_home = Path.home() / ".codex"
    codex_home.mkdir(exist_ok=True)
    
    # Read existing config if it exists
    config_path = codex_home / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {}
    
    # Update with Azure settings
    config["provider"] = "azure"
    if not config.get("providers"):
        config["providers"] = {}
    
    config["providers"]["azure"] = {
        "name": "AzureOpenAI",
        "baseURL": api_base,
        "envKey": "AZURE_OPENAI_API_KEY"
    }
    
    # Write updated config
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    # Create environment with Azure settings
    env = os.environ.copy()
    
    # IMPORTANT: According to Microsoft blog, we need BOTH environment variables
    # This is a workaround for a current Codex bug
    env["AZURE_OPENAI_API_KEY"] = token
    env["OPENAI_API_KEY"] = token  # Required workaround!
    
    # Build command
    codex_cmd = ["codex", "--provider", "azure"]
    
    # Add model if specified
    if model_name:
        if "--model" not in filtered_args and "-m" not in filtered_args:
            codex_cmd.extend(["--model", model_name])
    
    # Add remaining arguments
    codex_cmd.extend(filtered_args)
    
    # Debug output
    print(f"Running: {' '.join(codex_cmd)}", file=sys.stderr)
    print(f"With AZURE_BASE_URL: {api_base}", file=sys.stderr)
    
    # Run Codex
    try:
        result = subprocess.run(codex_cmd, env=env)
        return result.returncode
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error running Codex: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """CLI entry point."""
    return run_codex_nodejs(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
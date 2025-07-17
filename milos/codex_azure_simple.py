#!/usr/bin/env python3
"""
Simplest approach: Just use command-line flags
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from get_azure_token import get_azure_token


def run_codex_simple(args: List[str], env_path: Optional[Path] = None) -> int:
    """Run Codex CLI with Azure AD authentication using command-line flags."""
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
    
    # Set the token as an environment variable for Codex to use
    os.environ["AZURE_OPENAI_TOKEN"] = f"Bearer {token}"
    
    # Get OPENAI_API_BASE from .env
    api_base = os.getenv("OPENAI_API_BASE")
    if not api_base:
        print("Error: OPENAI_API_BASE not found in .env", file=sys.stderr)
        return 1
    
    # Extract deployment name from arguments if provided via --model
    model_name = None
    filtered_args = []
    i = 0
    while i < len(args):
        if args[i] == "--model" and i + 1 < len(args):
            model_name = args[i + 1]
            i += 2  # Skip both --model and its value
        elif args[i].startswith("--model="):
            model_name = args[i].split("=", 1)[1]
            i += 1
        elif args[i] == "-m" and i + 1 < len(args):
            model_name = args[i + 1]
            i += 2
        else:
            filtered_args.append(args[i])
            i += 1
    
    # Build Codex command using -c flags for each config
    codex_cmd = [
        "codex",
        "-c", "model_provider=azure-ad",
        "-c", f'model_providers.azure-ad.name=Azure with AD Auth',
        "-c", f'model_providers.azure-ad.base_url={api_base}',
        "-c", f'model_providers.azure-ad.env_http_headers.Authorization=AZURE_OPENAI_TOKEN',
        "-c", 'model_providers.azure-ad.query_params.api-version=2025-04-01-preview',
    ]
    
    # Add model if specified
    if model_name:
        codex_cmd.extend(["-m", model_name])
    
    # Add remaining arguments
    codex_cmd.extend(filtered_args)
    
    # If no arguments, add a space to avoid editor
    if not filtered_args:
        codex_cmd.append(" ")
    
    # Debug output
    print(f"Running: {' '.join(codex_cmd)}", file=sys.stderr)
    
    # Run Codex
    try:
        result = subprocess.run(codex_cmd)
        return result.returncode
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error running Codex: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """CLI entry point."""
    return run_codex_simple(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
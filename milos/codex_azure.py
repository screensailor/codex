#!/usr/bin/env python3
"""
Wrapper script to run Codex CLI with Azure AD authentication
Automatically obtains Azure AD token and configures Codex to use it
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from get_azure_token import get_azure_token


def run_codex_with_azure_auth(args: List[str], env_path: Optional[Path] = None) -> int:
    """Run Codex CLI with Azure AD authentication."""
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
    for i, arg in enumerate(args):
        if arg == "--model" and i + 1 < len(args):
            model_name = args[i + 1]
            break
        elif arg.startswith("--model="):
            model_name = arg.split("=", 1)[1]
            break

    # If no model specified, you might want to set a default
    if not model_name:
        model_name = "gpt-4"  # or your default deployment name

    # Build Codex command with Azure configuration
    codex_cmd = [
        "codex",
        "--config", "model_provider=azure-ad",
        "--config", f"model={model_name}",
        "--config", f'model_providers.azure-ad.name=Azure with AD Auth',
        "--config", f'model_providers.azure-ad.base_url={api_base}',
        "--config", f'model_providers.azure-ad.env_http_headers.Authorization=AZURE_OPENAI_TOKEN',
        "--config", 'model_providers.azure-ad.query_params.api-version=2024-08-01-preview',
    ]

    # Add any additional arguments passed to this script
    codex_cmd.extend(args)

    # Run Codex with the configuration
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
    return run_codex_with_azure_auth(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())

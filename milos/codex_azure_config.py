#!/usr/bin/env python3
"""
Alternative approach: Generate a config file for Codex with Azure AD settings
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from get_azure_token import get_azure_token


def run_codex_with_config_file(args: List[str], env_path: Optional[Path] = None) -> int:
    """Run Codex CLI with Azure AD authentication using a config file."""
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
        else:
            filtered_args.append(args[i])
            i += 1
    
    # If no model specified, use a default
    if not model_name:
        model_name = "gpt-4"  # or your default deployment name
    
    # Create a temporary config file
    config_content = f"""
model = "{model_name}"
model_provider = "azure-ad"

[model_providers.azure-ad]
name = "Azure with AD Auth"
base_url = "{api_base}"
env_http_headers = {{ "Authorization" = "AZURE_OPENAI_TOKEN" }}
query_params = {{ api-version = "2025-04-01-preview" }}
"""
    
    # Write to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.toml', delete=False) as tmp_config:
        tmp_config.write(config_content)
        tmp_config_path = tmp_config.name
    
    try:
        # Set CODEX_HOME to use our temporary config
        temp_codex_home = tempfile.mkdtemp()
        os.environ["CODEX_HOME"] = temp_codex_home
        
        # Copy the temp config to the expected location
        config_path = Path(temp_codex_home) / "config.toml"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text(config_content)
        
        # Create empty instructions file to avoid Vim
        instructions_path = Path(temp_codex_home) / "instructions.md"
        instructions_path.write_text("")
        
        # Build Codex command
        codex_cmd = ["codex"] + filtered_args
        
        # Run Codex
        print(f"Running: {' '.join(codex_cmd)}", file=sys.stderr)
        result = subprocess.run(codex_cmd)
        return result.returncode
        
    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error running Codex: {e}", file=sys.stderr)
        return 1
    finally:
        # Cleanup
        if 'tmp_config_path' in locals():
            try:
                os.unlink(tmp_config_path)
            except:
                pass
        if 'temp_codex_home' in locals():
            try:
                import shutil
                shutil.rmtree(temp_codex_home)
            except:
                pass


def main() -> int:
    """CLI entry point."""
    return run_codex_with_config_file(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
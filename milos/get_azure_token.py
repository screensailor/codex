#!/usr/bin/env python3
"""
Script to obtain Azure AD token for OpenAI API access
Reads configuration from milos/.env file
"""

import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv


def get_azure_token(env_path: Path | None = None) -> str:
    """Get Azure AD token using service principal credentials."""
    # Load environment variables
    if env_path is None:
        env_path = Path(__file__).parent / ".env"

    if not env_path.exists():
        raise FileNotFoundError(f"Error: {env_path} not found")

    load_dotenv(env_path)

    # Get required environment variables
    required_vars = {
        "AZURE_TENANT_ID": os.getenv("AZURE_TENANT_ID"),
        "AZURE_CLIENT_ID": os.getenv("AZURE_CLIENT_ID"),
        "AZURE_CLIENT_SECRET": os.getenv("AZURE_CLIENT_SECRET"),
        "AZURE_SCOPE": os.getenv("AZURE_SCOPE"),
    }

    # Check if all required variables are set
    missing_vars = [name for name, value in required_vars.items() if not value]
    if missing_vars:
        raise ValueError(
            f"Required environment variables are not set: {', '.join(missing_vars)}\n"
            f"Please ensure these are defined in {env_path}"
        )

    # Prepare token request
    token_url = (
        f"https://login.microsoftonline.com/{required_vars['AZURE_TENANT_ID']}/oauth2/v2.0/token"
    )
    token_data = {
        "client_id": required_vars["AZURE_CLIENT_ID"],
        "client_secret": required_vars["AZURE_CLIENT_SECRET"],
        "scope": required_vars["AZURE_SCOPE"],
        "grant_type": "client_credentials",
    }

    # Request token from Azure AD
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()

    token_response = response.json()
    access_token = token_response.get("access_token")

    if not access_token:
        raise ValueError(
            f"No access token in response\nResponse: {json.dumps(token_response, indent=2)}"
        )

    return access_token


def main() -> int:
    """CLI entry point."""
    try:
        token = get_azure_token()
        print(token)
        # Also export to environment variable
        os.environ["AZURE_OPENAI_TOKEN"] = token
        return 0
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to obtain access token: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Error details: {json.dumps(error_detail, indent=2)}", file=sys.stderr)
            except:
                print(f"Error response: {e.response.text}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

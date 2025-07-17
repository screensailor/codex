# Azure AD Authentication for Codex CLI

This directory contains scripts to use Codex CLI with Azure OpenAI using Azure AD (Service Principal) authentication.

## Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Azure credentials:
   - `AZURE_TENANT_ID`: Your Azure AD tenant ID
   - `AZURE_CLIENT_ID`: Your service principal's client ID
   - `AZURE_CLIENT_SECRET`: Your service principal's client secret
   - `AZURE_SCOPE`: Usually `https://cognitiveservices.azure.com/.default`
   - `OPENAI_API_BASE`: Your Azure OpenAI endpoint

3. Install dependencies using `uv` (recommended):
   ```bash
   # Install uv if you haven't already
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # Install dependencies
   cd milos
   uv pip install -e .
   ```

   Or with regular pip:
   ```bash
   pip install requests python-dotenv
   ```

## Usage

### Option 1: Use the wrapper script (recommended)

After installing with uv:
```bash
# From anywhere (if installed with uv pip install -e .)
codex-azure "your prompt here"

# With specific model/deployment
codex-azure --model gpt-4 "explain this code"

# Interactive mode
codex-azure
```

Or run directly:
```bash
python milos/codex_azure.py "your prompt here"

# With specific model/deployment
python milos/codex_azure.py --model gpt-4 "explain this code"

# Interactive mode
python milos/codex_azure.py
```

### Option 2: Manual token + config
```bash
# Get token (after installing with uv)
export AZURE_OPENAI_TOKEN=$(get-azure-token)

# Or run directly
export AZURE_OPENAI_TOKEN=$(python milos/get_azure_token.py)

# Run Codex with custom config
codex --config model_provider=azure-ad \
      --config model="your-deployment-name" \
      --config 'model_providers.azure-ad={name="Azure AD", base_url="'$OPENAI_API_BASE'", env_http_headers={"Authorization": "AZURE_OPENAI_TOKEN"}, query_params={api-version="2024-08-01-preview"}}'
```

### Option 3: Add to ~/.codex/config.toml
First get a token, then add to your config:

```toml
model = "your-deployment-name"
model_provider = "azure-ad"

[model_providers.azure-ad]
name = "Azure with AD Auth"
base_url = "https://your-resource.openai.azure.com/openai"
env_http_headers = { "Authorization" = "AZURE_OPENAI_TOKEN" }
query_params = { api-version = "2024-08-01-preview" }
```

## How it works

1. `get-azure-token.py`: Obtains an OAuth2 token from Azure AD using your service principal credentials
2. `codex-azure.py`: Wrapper that automatically gets a fresh token and configures Codex to use it
3. The token is passed via the `Authorization` header using Codex's `env_http_headers` feature

## Notes

- Azure AD tokens expire after ~1 hour, so you may need to re-run the wrapper script
- The wrapper script gets a fresh token each time it runs
- Make sure your service principal has the necessary permissions to access your Azure OpenAI resource
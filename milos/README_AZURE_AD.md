# Azure AD Authentication Issue with Codex CLI

## The Problem

The Codex CLI (Node.js version) expects Azure OpenAI to use API key authentication, where the key is sent as:
```
api-key: <your-key>
```

However, your Azure OpenAI instance uses Azure AD (Entra ID) authentication, which requires:
```
Authorization: Bearer <jwt-token>
```

The OpenAI SDK's `AzureOpenAI` class doesn't support Bearer token authentication directly.

## Current Status

1. ✅ We can obtain Azure AD tokens successfully
2. ✅ The tokens work when calling Azure OpenAI directly (verified with curl/Python)
3. ❌ Codex CLI can't use these tokens because it expects API keys

## Potential Solutions

### Option 1: Use API Key Authentication (Recommended)
If possible, enable API key authentication in your Azure OpenAI resource:
1. Go to Azure Portal → Your OpenAI Resource
2. Navigate to "Keys and Endpoint"
3. Copy one of the keys
4. Use that key instead of Azure AD tokens

### Option 2: Wait for PR #92
The Microsoft blog mentions PR #92 is "work in progress" for Entra ID token-based authentication.

### Option 3: Create a Local Proxy
Create a local proxy server that:
1. Accepts requests with API key auth
2. Exchanges the "API key" (actually a token) to Bearer auth
3. Forwards to Azure OpenAI

### Option 4: Fork and Modify Codex
Modify the Node.js code to support Bearer tokens directly.

## Workaround Attempts

We tried several approaches:
1. Setting both `AZURE_OPENAI_API_KEY` and `OPENAI_API_KEY` (Microsoft's workaround)
2. Creating custom config files
3. Using command-line flags

None work because the underlying issue is the authentication method mismatch.

## Next Steps

1. Check if your Azure OpenAI resource supports API key authentication
2. If not, consider waiting for the official Entra ID support (PR #92)
3. Or implement a local proxy solution
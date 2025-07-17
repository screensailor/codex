#!/usr/bin/env python3
"""
Setup Codex to use direct Azure OpenAI endpoint (not APIM)
"""

import os
import json
from pathlib import Path


def setup_direct_endpoint():
    # Direct Azure OpenAI endpoint
    direct_endpoint = "https://openai6t1p642f.openai.azure.com"
    
    # Create ~/.codex directory
    codex_home = Path.home() / ".codex"
    codex_home.mkdir(exist_ok=True)
    
    # Create/update config.json
    config = {
        "model": "gpt-4.1_2025-04-14_DZ-EU",
        "provider": "azure",
        "providers": {
            "azure": {
                "name": "AzureOpenAI",
                "baseURL": f"{direct_endpoint}/openai",
                "envKey": "AZURE_OPENAI_API_KEY"
            }
        }
    }
    
    config_path = codex_home / "config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Updated {config_path}")
    print(f"✓ Using direct endpoint: {direct_endpoint}")
    print()
    print("Now run:")
    print()
    print("  export AZURE_OPENAI_API_KEY=\"<your-api-key>\"")
    print("  export OPENAI_API_KEY=$AZURE_OPENAI_API_KEY")
    print("  codex \"hello, what model are you using?\"")
    print()
    print("This should work with your API keys from the Azure Portal!")
    
    # Also create a test script
    test_script = Path(__file__).parent / "test_direct_endpoint.py"
    test_content = f'''#!/usr/bin/env python3
import os
import requests

api_key = os.getenv("AZURE_OPENAI_API_KEY")
if not api_key:
    print("Please set AZURE_OPENAI_API_KEY")
    exit(1)

url = "{direct_endpoint}/openai/deployments/gpt-4.1_2025-04-14_DZ-EU/chat/completions?api-version=2025-04-01-preview"

headers = {{
    "api-key": api_key,
    "Content-Type": "application/json"
}}

data = {{
    "messages": [{{"role": "user", "content": "Hello"}}],
    "max_tokens": 10
}}

print(f"Testing: {{url}}")
response = requests.post(url, headers=headers, json=data)
print(f"Status: {{response.status_code}}")
if response.status_code == 200:
    print("✓ Success! Direct endpoint works with API key")
else:
    print(f"Error: {{response.text}}")
'''
    
    with open(test_script, "w") as f:
        f.write(test_content)
    
    os.chmod(test_script, 0o755)
    print(f"\nCreated test script: {test_script}")
    print("Run it with: python milos/test_direct_endpoint.py")


if __name__ == "__main__":
    setup_direct_endpoint()
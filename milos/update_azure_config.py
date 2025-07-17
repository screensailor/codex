#!/usr/bin/env python3
"""
Update Azure config with the correct model deployment name
"""

import json
from pathlib import Path


def update_config():
    config_path = Path.home() / ".codex" / "config.json"
    
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
    else:
        config = {}
    
    # Update the model to match your deployment
    config["model"] = "gpt-4.1_2025-04-14_DZ-EU"
    
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Updated {config_path}")
    print(f"Model set to: gpt-4.1_2025-04-14_DZ-EU")
    
    # Also show current config
    print("\nCurrent config:")
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    update_config()
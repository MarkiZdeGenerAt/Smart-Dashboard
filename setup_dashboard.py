#!/usr/bin/env python3
"""Add Smart Dashboard entry to Home Assistant configuration.yaml."""
import sys
from pathlib import Path
import yaml

DEFAULT_DIR = Path.home() / ".homeassistant"


def main() -> None:
    target_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    cfg_path = target_dir / "configuration.yaml"
    data = {}
    if cfg_path.exists():
        with cfg_path.open() as f:
            data = yaml.safe_load(f) or {}
    lovelace = data.setdefault("lovelace", {})
    dashboards = lovelace.setdefault("dashboards", {})
    if "smart-dashboard" in dashboards:
        print("Smart Dashboard already configured in configuration.yaml")
        return
    dashboards["smart-dashboard"] = {
        "mode": "yaml",
        "title": "Smart Dashboard",
        "icon": "mdi:monitor-dashboard",
        "show_in_sidebar": True,
        "filename": "dashboards/smart_dashboard.yaml",
    }
    cfg_path.write_text(yaml.safe_dump(data, sort_keys=False))
    print(f"Updated {cfg_path} with Smart Dashboard entry")


if __name__ == "__main__":
    main()

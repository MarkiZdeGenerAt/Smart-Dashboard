#!/usr/bin/env bash
# Simple installer for the Smart Dashboard custom integration.
set -euo pipefail

TARGET_DIR="${1:-$HOME/.homeassistant}"
COMP_DIR="$TARGET_DIR/custom_components/smart_dashboard"

echo "Installing Smart Dashboard to $COMP_DIR"
mkdir -p "$TARGET_DIR/custom_components"
cp -r custom_components/smart_dashboard "$COMP_DIR"

CONFIG_FILE="$TARGET_DIR/smart_dashboard.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
  cp custom_components/smart_dashboard/config/example_config.yaml "$CONFIG_FILE"
  echo "Created default configuration at $CONFIG_FILE"
fi

mkdir -p "$TARGET_DIR/dashboards"
python3 custom_components/smart_dashboard/dashboard.py "$CONFIG_FILE" --output "$TARGET_DIR/dashboards/smart_dashboard.yaml"
echo "Installation complete. Dashboard generated."


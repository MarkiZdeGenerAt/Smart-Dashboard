#!/usr/bin/env bash
# Simple installer for the SHI Dashboard custom integration.
set -euo pipefail

TARGET_DIR="${1:-$HOME/.homeassistant}"
COMP_DIR="$TARGET_DIR/custom_components/shi_dashboard"

echo "Installing SHI Dashboard to $COMP_DIR"
mkdir -p "$TARGET_DIR/custom_components"
cp -r custom_components/shi_dashboard "$COMP_DIR"

CONFIG_FILE="$TARGET_DIR/shi_dashboard.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
  cp custom_components/shi_dashboard/config/example_config.yaml "$CONFIG_FILE"
  echo "Created default configuration at $CONFIG_FILE"
fi

mkdir -p "$TARGET_DIR/dashboards"
python3 custom_components/shi_dashboard/dashboard.py "$CONFIG_FILE" --output "$TARGET_DIR/dashboards/shi_dashboard.yaml"
echo "Installation complete. Dashboard generated."


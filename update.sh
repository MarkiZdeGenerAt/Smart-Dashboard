#!/usr/bin/env bash
# Update script for the SHI Dashboard custom integration.
set -euo pipefail

REPO_URL="https://github.com/user/Smart-Dashboard"
ARCHIVE_URL="$REPO_URL/archive/refs/heads/main.tar.gz"

TARGET_DIR="${1:-$HOME/.homeassistant}"
COMP_DIR="$TARGET_DIR/custom_components/shi_dashboard"

echo "Downloading latest SHI Dashboard..."
TMP_DIR=$(mktemp -d)
curl -L "$ARCHIVE_URL" -o "$TMP_DIR/sd.tar.gz"
tar -xzf "$TMP_DIR/sd.tar.gz" -C "$TMP_DIR"
SRC_DIR=$(find "$TMP_DIR" -maxdepth 1 -type d -name 'Smart-Dashboard*' | head -n1)

mkdir -p "$TARGET_DIR/custom_components"
rm -rf "$COMP_DIR"
cp -r "$SRC_DIR/custom_components/shi_dashboard" "$COMP_DIR"

CONFIG_FILE="$TARGET_DIR/shi_dashboard.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
  cp "$SRC_DIR/custom_components/shi_dashboard/config/example_config.yaml" "$CONFIG_FILE"
  echo "Created default configuration at $CONFIG_FILE"
fi

mkdir -p "$TARGET_DIR/dashboards"
python3 "$COMP_DIR/dashboard.py" "$CONFIG_FILE" --output "$TARGET_DIR/dashboards/shi_dashboard.yaml"

echo "Update complete."
rm -rf "$TMP_DIR"

#!/usr/bin/env bash
# Simple installer for the SHI Dashboard custom integration.
set -euo pipefail

TARGET_DIR="${1:-$HOME/.homeassistant}"
COMP_DIR="$TARGET_DIR/custom_components/shi_dashboard"

echo "Installing SHI Dashboard to $COMP_DIR"
mkdir -p "$TARGET_DIR/custom_components"
cp -r shi_dashboard "$COMP_DIR"

echo "Installation complete. Example configuration can be found in shi_dashboard/config/example_config.yaml"


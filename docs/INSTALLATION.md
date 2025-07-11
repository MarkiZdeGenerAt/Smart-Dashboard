# Installation Guide

This guide explains how to install the SHI Dashboard custom integration into Home Assistant.

## Installing via HACS
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **SHI Dashboard** in HACS and install it.
3. Restart Home Assistant to activate the integration.

## Generating a Dashboard
1. On first start, a default `shi_dashboard.yaml` configuration and `ui-lovelace.yaml`
   dashboard will be created automatically.
2. Reload Lovelace or restart Home Assistant again to see the dashboard.
3. You can modify `shi_dashboard.yaml` and run the generator manually:
   ```bash
   python3 -m custom_components.shi_dashboard.dashboard shi_dashboard.yaml --output ui-lovelace.yaml
   ```
   Optionally, pass `--template <template.j2>` to use a custom Jinja2 template.

   If `auto_discover: true` is set in the configuration, export `HASS_URL` and `HASS_TOKEN` so the generator can query Home Assistant for devices.



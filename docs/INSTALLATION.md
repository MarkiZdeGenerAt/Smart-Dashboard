# Installation Guide

This guide explains how to install the SHI Dashboard custom integration into Home Assistant.

## Installing via HACS
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **SHI Dashboard** in HACS and install it.
3. Restart Home Assistant to activate the integration.

## Generating a Dashboard
1. Create a configuration file named `shi_dashboard.yaml` in your Home Assistant configuration directory. Use `shi_dashboard/config/example_config.yaml` as a starting point.
2. Run the helper script to generate a Lovelace dashboard file:
   ```bash
   python3 -m shi_dashboard.dashboard shi_dashboard.yaml --output ui-lovelace.yaml
   ```
   Optionally, pass `--template <template.j2>` to use a custom Jinja2 template.

   If `auto_discover: true` is set in the configuration, export `HASS_URL` and `HASS_TOKEN` so the generator can query Home Assistant for devices.

3. Restart Home Assistant or reload Lovelace to see the generated dashboard.



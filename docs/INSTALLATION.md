# Installation Guide

This guide explains how to install the SHI Dashboard custom integration into Home Assistant.

## Installing via HACS
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **SHI Dashboard** in HACS and install it.
3. In Home Assistant open **Settings → Devices & Services** and click **Add Integration**.
   Choose **SHI Dashboard** to create the configuration entry.
4. Restart Home Assistant to activate the integration.

## Generating a Dashboard
1. On first start, a default `shi_dashboard.yaml` configuration and
   `dashboards/shi_dashboard.yaml` dashboard will be created automatically.
2. Add this to your `configuration.yaml` so the dashboard appears in the sidebar:

   ```yaml
   lovelace:
     dashboards:
       shi-dashboard:
         mode: yaml
         title: SHI Dashboard
         icon: mdi:monitor-dashboard
         show_in_sidebar: true
         filename: dashboards/shi_dashboard.yaml
   ```
3. Reload Lovelace or restart Home Assistant again to see the dashboard.
3. You can modify `shi_dashboard.yaml` and run the generator manually:
   ```bash
   python3 custom_components/shi_dashboard/dashboard.py shi_dashboard.yaml \
       --output dashboards/shi_dashboard.yaml
   ```
  Optionally, pass `--template <template.j2>` to use a custom Jinja2 template.

  If `auto_discover: true` is set in the configuration and you run the generator outside of Home Assistant, export `HASS_URL` and `HASS_TOKEN` so it can query the API. When executed within Home Assistant the integration will automatically use its own credentials. Discovered entities are grouped by area to mimic Dwains Dashboard. If areas cannot be retrieved they are placed in a single "Auto Detected" room.

## Using Plugins

Place additional Python modules in `custom_components/shi_dashboard/plugins`.
Each module should define `process_config(config)` which will be called during
dashboard generation. See `header_card.py` for a simple example.



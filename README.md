# SHI Dashboard

SHI Dashboard is a customizable dashboard add-on for Home Assistant. It allows users to configure rooms and cards using simple YAML without writing code. The provided `dashboard.py` utility converts a user-defined configuration file into a Lovelace dashboard.

## Installation

The easiest way to install is through HACS:
1. Add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration" in HACS.
2. Search for **SHI Dashboard** and install it.
3. In Home Assistant open **Settings → Devices & Services** and click **Add Integration**.
   Select **SHI Dashboard** to create the configuration entry.
4. Restart Home Assistant. This generates `shi_dashboard.yaml` and `dashboards/shi_dashboard.yaml`.
   The integration files live under `custom_components/shi_dashboard` in your configuration directory.

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for more details.

## Getting Started

1. Restart Home Assistant after installing the integration.
   A default configuration will be created as `shi_dashboard.yaml` and a dashboard
   generated at `dashboards/shi_dashboard.yaml`.
2. Add the following to your `configuration.yaml` to show the dashboard
   automatically:

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
3. Reload Lovelace or restart Home Assistant again to see the new dashboard.
4. You can edit `shi_dashboard.yaml` at any time to customise the layout and run
   the generator manually if you wish.

## Requirements

If you run the dashboard generator outside of Home Assistant, install the
following Python packages first:

```bash
pip install homeassistant pyyaml jinja2 requests
```

## Auto Device Detection

`auto_discover` is enabled by default and will query your Home Assistant instance for all registered entities. When the generator runs inside Home Assistant it uses the integration's credentials automatically. If you run the generator manually outside of Home Assistant **you must set the environment variables** `HASS_URL` and `HASS_TOKEN` so it can connect to the API. Discovered entities are grouped by their assigned area when possible; if area information cannot be retrieved everything is placed in a single "Auto Detected" room.

## Plugins

Plugins placed in `custom_components/shi_dashboard/plugins` can modify the
configuration before the dashboard is generated. Each plugin should define a
`process_config(config)` function. The provided `header_card` plugin inserts a
markdown header card into every room.

The `blueprint_loader` plugin loads any YAML files found in
`custom_components/shi_dashboard/blueprints` and appends them as additional
rooms. This mimics the blueprint system in Dwains Dashboard for quickly adding
predefined layouts.

Translation files located under `custom_components/shi_dashboard/translations`
allow the dashboard to be generated in different languages. Set the `SHI_LANG`
environment variable (e.g. `en` or `fr`) to select the language. If no
translation is found English is used by default.

## Example Configuration

```yaml
auto_discover: true
layout:
  strategy: masonry
```

With auto discovery enabled the integration will query Home Assistant for all
entities and group them by their assigned area, similar to Dwains Dashboard.

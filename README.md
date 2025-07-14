# SHI Dashboard

SHI Dashboard is a customizable dashboard add-on for Home Assistant. It allows users to configure rooms and cards using simple YAML without writing code. The provided `dashboard.py` utility converts a user-defined configuration file into a Lovelace dashboard.

## Installation

Install the add-on through HACS for the simplest setup:
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **SHI Dashboard** and install it.
3. Open **Settings → Devices & Services** in Home Assistant and choose **Add Integration**.
   Select **SHI Dashboard** to complete the setup.
4. Restart Home Assistant to generate the default `shi_dashboard.yaml` and
   `dashboards/shi_dashboard.yaml`.
   The integration files are placed under `custom_components/shi_dashboard` in
   your Home Assistant configuration.

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

`auto_discover` is enabled by default and will query your Home Assistant instance for all registered entities. When the generator runs inside Home Assistant the API credentials are used automatically. If you run the generator manually outside of Home Assistant, set the environment variables `HASS_URL` and `HASS_TOKEN` so it can connect to the API. Discovered entities are grouped by their assigned area when possible, similar to Dwains Dashboard. If area information cannot be retrieved everything is placed in a single "Auto Detected" room.

## Plugins

Plugins placed in `custom_components/shi_dashboard/plugins` can modify the
configuration before the dashboard is generated. Each plugin should define a
`process_config(config)` function. The provided `header_card` plugin inserts a
markdown header card into every room.

## Example Configuration

```yaml
auto_discover: true
layout:
  strategy: masonry
```

With auto discovery enabled the integration will query Home Assistant for all
entities and group them by their assigned area, similar to Dwains Dashboard.

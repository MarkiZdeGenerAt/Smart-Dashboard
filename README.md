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

## Auto Device Detection

Setting `auto_discover: true` in `shi_dashboard.yaml` will query your Home Assistant instance for all registered entities. When the generator runs inside Home Assistant the API credentials are used automatically. If you run the generator manually outside of Home Assistant, set the environment variables `HASS_URL` and `HASS_TOKEN` so it can connect to the API. Discovered entities are grouped by their assigned area when possible, similar to Dwains Dashboard. If area information cannot be retrieved everything is placed in a single "Auto Detected" room.

## Plugins

Plugins placed in `custom_components/shi_dashboard/plugins` can modify the
configuration before the dashboard is generated. Each plugin should define a
`process_config(config)` function. The provided `header_card` plugin inserts a
markdown header card into every room.

## Example Configuration

```yaml
auto_discover: false
layout:
  strategy: masonry
rooms:
  - name: Living Room
    cards:
      - type: thermostat
        entity: climate.living_room
      - type: light
        entity: light.ceiling
  - name: Bedroom
    layout: horizontal
    cards:
      - type: light
        entity: light.bedside
```

This generates a dashboard with two rooms and demonstrates layout configuration. Set `auto_discover` to `true` to automatically include all detected devices.

# SHI Dashboard

SHI Dashboard is a customizable dashboard add-on for Home Assistant. It allows users to configure rooms and cards using simple YAML without writing code. The provided `dashboard.py` utility converts a user-defined configuration file into a Lovelace dashboard.

## Installation

Install the add-on through HACS for the simplest setup:
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **SHI Dashboard** and install it.
3. Restart Home Assistant to activate the integration. On first start the integration will
   generate a default `shi_dashboard.yaml` and `ui-lovelace.yaml` for you.

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for more details.

## Getting Started

1. Restart Home Assistant after installing the integration.
   A default configuration will be created as `shi_dashboard.yaml` and a dashboard
   generated as `ui-lovelace.yaml`.
2. Reload Lovelace or restart Home Assistant again to see the new dashboard.
3. You can edit `shi_dashboard.yaml` at any time to customise the layout and run
   the generator manually if you wish.

## Auto Device Detection

Setting `auto_discover: true` in `shi_dashboard.yaml` will query your Home Assistant instance for all available entities. The environment variables `HASS_URL` and `HASS_TOKEN` must be set so the generator can connect to the API.

Discovered devices are added to a room named "Auto Detected" using sensible card types.

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

# SHI Dashboard

SHI Dashboard is a customizable dashboard add-on for Home Assistant. It allows users to configure rooms and cards using simple YAML without writing code. The provided `dashboard.py` utility converts a user-defined configuration file into a Lovelace dashboard.

## Installation

Install the add-on through HACS for the simplest setup:
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **SHI Dashboard** and install it.
3. Restart Home Assistant to activate the integration.

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for more details.

## Getting Started

1. After installing through HACS, place your configuration file (see `shi_dashboard/config/example_config.yaml` for reference) in the Home Assistant configuration directory as `shi_dashboard.yaml`.
2. Run the generator to produce a Lovelace dashboard file:
```bash
python3 -m shi_dashboard.dashboard shi_dashboard.yaml --output ui-lovelace.yaml
```
3. You can also provide your own Jinja2 template to fully customise the output:
```bash
python3 -m shi_dashboard.dashboard shi_dashboard.yaml --template my_template.j2
```
4. Reload Lovelace or restart Home Assistant to see the new dashboard.

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

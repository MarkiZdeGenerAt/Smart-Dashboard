# SHI Dashboard

SHI Dashboard is a customizable dashboard add-on for Home Assistant. It allows users to configure rooms and cards using simple YAML without writing code. The provided `dashboard.py` utility converts a user-defined configuration file into a Lovelace dashboard.

## Installation

Run the provided `install.sh` script to copy the integration into your Home Assistant configuration directory. The script defaults to `~/.homeassistant` if no path is supplied:

```bash
./install.sh /path/to/homeassistant
```

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for a detailed guide.

## Getting Started

1. Install the custom integration using the `install.sh` script.
2. Place your configuration file (see `shi_dashboard/config/example_config.yaml` for reference) in the Home Assistant configuration directory as `shi_dashboard.yaml`.
3. Run the generator to produce a Lovelace dashboard file:

```bash
python3 -m shi_dashboard.dashboard shi_dashboard.yaml --output ui-lovelace.yaml
```

You can also provide your own Jinja2 template to fully customise the output:

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

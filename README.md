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

## Example Configuration

```yaml
rooms:
  - name: Living Room
    cards:
      - type: thermostat
        entity: climate.living_room
      - type: light
        entity: light.ceiling
```

This will generate a simple dashboard with a room view called "Living Room" containing the specified cards.

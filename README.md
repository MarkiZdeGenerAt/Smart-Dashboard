# SHI Dashboard

SHI Dashboard is a customizable dashboard add-on for Home Assistant. It allows users to configure rooms and cards using simple YAML without writing code. The provided `dashboard.py` utility converts a user-defined configuration file into a Lovelace dashboard.

## Getting Started

1. Install the custom integration by copying the `shi_dashboard` directory into your Home Assistant `custom_components` folder.
2. Place your configuration file (see `shi_dashboard/config/example_config.yaml` for reference) in the Home Assistant configuration directory as `shi_dashboard.yaml`.
3. Run the generator to produce a Lovelace dashboard file:

```bash
python3 -m shi_dashboard.dashboard shi_dashboard.yaml --output ui-lovelace.yaml
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

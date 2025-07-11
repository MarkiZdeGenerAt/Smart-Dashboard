# Installation Guide

This guide explains how to install the SHI Dashboard custom integration into Home Assistant.

1. **Clone the repository** on a machine that can access your Home Assistant configuration directory.
   ```bash
   git clone https://github.com/user/Smart-Dashboard.git
   cd Smart-Dashboard
   ```

2. **Run the installer** and provide the path to your Home Assistant configuration directory (defaults to `~/.homeassistant` if omitted).
   ```bash
   ./install.sh /path/to/homeassistant
   ```
   This copies the `shi_dashboard` component into `custom_components/shi_dashboard` inside your configuration directory.

3. **Create a configuration file** named `shi_dashboard.yaml` in the Home Assistant configuration directory. Use `shi_dashboard/config/example_config.yaml` as a starting point.

4. **Generate the dashboard** using the helper script:
   ```bash
   python3 -m shi_dashboard.dashboard shi_dashboard.yaml --output ui-lovelace.yaml
   ```
   Optionally, pass `--template <template.j2>` to use a custom Jinja2 template.

   If `auto_discover: true` is set in the configuration, export `HASS_URL` and `HASS_TOKEN` so the generator can query Home Assistant for devices.

5. **Restart Home Assistant** or reload Lovelace to see the generated dashboard.



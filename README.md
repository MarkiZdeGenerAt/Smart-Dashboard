# Smart Dashboard

Smart Dashboard is a customizable dashboard add-on for Home Assistant. It allows users to configure rooms and cards using simple YAML without writing code. The provided `dashboard.py` utility converts a user-defined configuration file into a Lovelace dashboard.

## Installation

The easiest way to install is through HACS:
1. Add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration" in HACS.
2. Search for **Smart Dashboard** and install it.
3. In Home Assistant open **Settings → Devices & Services** and click **Add Integration**.
   Select **Smart Dashboard** to create the configuration entry.
4. Restart Home Assistant. This generates `smart_dashboard.yaml` and `dashboards/smart_dashboard.yaml`.
   The integration files live under `custom_components/smart_dashboard` in your configuration directory.
5. The integration provides a `config_flow` declared in `manifest.json`, so it shows up automatically in the **Add Integration** dialog.

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for more details.

## Updating

Run `update.sh` from the repository to download and install the latest
version. You can also update through HACS by opening the Smart Dashboard
integration and clicking **Update** when a new release is available.
The `auto_update.py` helper checks for a new release automatically and
installs it into your Home Assistant configuration directory:

```bash
python3 auto_update.py /path/to/your/homeassistant
```

## Getting Started

1. Restart Home Assistant after installing the integration.
   A default configuration will be created as `smart_dashboard.yaml` and a dashboard
   generated at `dashboards/smart_dashboard.yaml`.
2. The integration adds the dashboard entry to `configuration.yaml`
   automatically on first start. If you ever need to update it manually run:

   ```bash
   python3 setup_dashboard.py /path/to/your/homeassistant
   ```

3. Reload Lovelace or restart Home Assistant again to see the new dashboard.
4. You can edit `smart_dashboard.yaml` at any time to customise the layout,
   select a theme and run the generator manually if you wish.

## Requirements

If you run the dashboard generator outside of Home Assistant, install the
following Python packages first:

```bash
pip install homeassistant pyyaml jinja2 requests
```

## Auto Device Detection

`auto_discover` is enabled by default and will query your Home Assistant instance for all registered entities. When the generator runs inside Home Assistant it uses the integration's credentials automatically. If you run the generator manually outside of Home Assistant **you must set the environment variables** `HASS_URL` and `HASS_TOKEN` so it can connect to the API. Discovered entities are grouped by their assigned area when possible; if area information cannot be retrieved everything is placed in a single "Auto Detected" room. Devices within an area are further arranged into stacks of lights, climate controls, multimedia players and sensors.

## Plugins

Plugins placed in `custom_components/smart_dashboard/plugins` can modify the
configuration before the dashboard is generated. Each plugin should define a `process_config(config)` function.
The `dwains_style` plugin creates a Dwains Dashboard inspired navigation bar. It
automatically adds each room as a sidebar shortcut, enables the clock in the
header and applies a default `dwains` theme. It also loads a small JavaScript
module that draws a live clock in the header so the dashboard feels closer to
Dwains Dashboard. The script is served from `/local/dwains_style.js` and is
added automatically to the Lovelace `resources` section.

Rooms are displayed using the Lovelace grid card with two columns. Individual
devices appear as button-card tiles that feature a subtle background and rounded
corners to better match the Dwains Dashboard style.

`lovelace_cards_loader` can import existing Lovelace views by talking to the
Home Assistant API. Enable it by setting `load_lovelace_cards: true` in your
configuration. The generator will request `/api/lovelace` using the credentials
provided via the `HASS_URL` and `HASS_TOKEN` environment variables and append
the returned views as rooms.

Translation files located under `custom_components/smart_dashboard/translations`
allow the dashboard to be generated in different languages. Set the `SHI_LANG`
environment variable (e.g. `en`, `ru`, `bg`, or `es`) to select the language. If no
translation is found English is used by default.

## Example Configuration

```yaml
auto_discover: true
header:
  title: "\u0423\u043C\u043D\u044B\u0439 \u0434\u043E\u043C"
  logo: "/local/icons/home.png"
  show_time: true
sidebar:
  - name: "\u041E\u0431\u0437\u043E\u0440"
    icon: "mdi:view-dashboard"
    view: "overview"
  - name: "\u0421\u0432\u0435\u0442"
    icon: "mdi:lightbulb"
    view: "lights"
    condition: user == "admin"
layout:
  strategy: masonry
theme: auto
load_lovelace_cards: true
```

With auto discovery enabled the integration will query Home Assistant for all
entities and group them by their assigned area, similar to Dwains Dashboard.
Rooms can specify an `order` field to control their position in the dashboard.
All options are validated using `voluptuous` to catch mistakes early.
You can embed any standard Lovelace card by listing its configuration under
`cards`. For example `type: glance` or `type: light` entries are passed through
to the generated dashboard unchanged. When a room has no entities a small
placeholder tile with an icon and "No entities" text is shown so the view is not
completely empty.

## UI Config Editor

A command line helper `ui_config_editor.py` lets you modify `smart_dashboard.yaml` without manual editing. It can rearrange cards, hide or show rooms and manage sidebar shortcuts used as quick links on the home screen.

Usage example:

```bash
python3 -m custom_components.smart_dashboard.ui_config_editor smart_dashboard.yaml move-card "Living" 0 1
```

Run the script with `--help` to see all available commands.

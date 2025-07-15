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

See [`docs/INSTALLATION.md`](docs/INSTALLATION.md) for more details.

## Updating

Run `update.sh` from the repository to download and install the latest
version. You can also update through HACS by opening the Smart Dashboard
integration and clicking **Update** when a new release is available.

## Getting Started

1. Restart Home Assistant after installing the integration.
   A default configuration will be created as `smart_dashboard.yaml` and a dashboard
   generated at `dashboards/smart_dashboard.yaml`.
2. Add the following to your `configuration.yaml` to show the dashboard
   automatically:

   ```yaml
   lovelace:
     dashboards:
       smart-dashboard:
         mode: yaml
         title: Smart Dashboard
         icon: mdi:monitor-dashboard
         show_in_sidebar: true
         filename: dashboards/smart_dashboard.yaml
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

`auto_discover` is enabled by default and will query your Home Assistant instance for all registered entities. When the generator runs inside Home Assistant it uses the integration's credentials automatically. If you run the generator manually outside of Home Assistant **you must set the environment variables** `HASS_URL` and `HASS_TOKEN` so it can connect to the API. Discovered entities are grouped by their assigned area when possible; if area information cannot be retrieved everything is placed in a single "Auto Detected" room. Devices within an area are further arranged into stacks of lights, climate controls and multimedia players.

## Plugins

Plugins placed in `custom_components/smart_dashboard/plugins` can modify the
configuration before the dashboard is generated. Each plugin should define a
`process_config(config)` function. The provided `header_card` plugin inserts a
markdown header card into every room.

The `blueprint_loader` plugin loads any YAML files found in
`custom_components/smart_dashboard/blueprints` and appends them as additional
rooms. This mimics the blueprint system in Dwains Dashboard for quickly adding
predefined layouts.

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
rooms:
  - name: \u0413\u043E\u0441\u0442\u0438\u043D\u0430\u044F
    order: 1
    cards:
      - type: light
        entity: light.living_room
      - type: glance
        entities:
          - sensor.temperature
          - binary_sensor.front_door
  - name: \u041A\u0443\u0445\u043D\u044F
    conditions:
      - state('binary_sensor.kitchen_motion') == 'on'
    cards:
      - type: light
        entity: light.kitchen
```

With auto discovery enabled the integration will query Home Assistant for all
entities and group them by their assigned area, similar to Dwains Dashboard.
Rooms can specify an `order` field to control their position in the dashboard.
All options are validated using `voluptuous` to catch mistakes early.
You can embed any standard Lovelace card by listing its configuration under
`cards`. For example `type: glance` or `type: light` entries are passed through
to the generated dashboard unchanged.

## Web Client

A small JavaScript helper is available at `custom_components/smart_dashboard/www/main.js`.
Include it as a Lovelace resource to enable live updates. The script periodically
fetches entity states from the Home Assistant REST API and fills any element with
a `data-entity-id` attribute with the current state.

Example resource declaration:

```yaml
resources:
  - url: /local/smart_dashboard/main.js
    type: module
```

Usage inside a dashboard:

```html
<span data-entity-id="sensor.outside_temperature"></span>
<script>
  const sd = new window.SmartDashboard('http://homeassistant.local:8123', 'YOUR_LONG_LIVED_TOKEN');
  sd.start();
</script>
```

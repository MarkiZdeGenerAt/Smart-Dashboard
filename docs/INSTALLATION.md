# Installation Guide

Follow these steps to install the Smart Dashboard custom integration into Home Assistant.

## Install with HACS
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **Smart Dashboard** and install it.
3. Open **Settings → Devices & Services** in Home Assistant and click **Add Integration**.
   Choose **Smart Dashboard** to create the configuration entry.
4. Restart Home Assistant to activate the integration.
   Since `manifest.json` enables a `config_flow`, Smart Dashboard appears automatically in the **Add Integration** list.
5. Install the [Button Card](https://github.com/custom-cards/button-card) custom card in HACS and add the resource entry:

   ```yaml
   url: /hacsfiles/button-card/button-card.js
   type: module
   ```

   This resource is required for the dashboard tiles to render correctly.

## Generate Your First Dashboard
1. The first start creates `smart_dashboard.yaml` and `dashboards/smart_dashboard.yaml` automatically.
2. The integration inserts the dashboard configuration into `configuration.yaml`
   automatically on first start. To apply it manually run:

   ```bash
   python3 setup_dashboard.py /path/to/your/homeassistant
   ```
3. Reload Lovelace or restart Home Assistant to see the dashboard.
4. To regenerate manually, run:

   ```bash
  python3 custom_components/smart_dashboard/dashboard.py smart_dashboard.yaml \
      --output dashboards/smart_dashboard.yaml
  ```
   Or call the `smart_dashboard.generate` service in Home Assistant to
   rebuild the dashboard without restarting.

You can also define a Lovelace theme by adding `theme: <name>` to
`smart_dashboard.yaml`.

Rooms may specify an `order` field so they appear in a custom sequence on the
dashboard.

   Pass `--template <template.j2>` to use a custom Jinja2 template if desired.

   Auto discovery is on by default. When running outside Home Assistant **be sure**
   to set `HASS_URL` and `HASS_TOKEN` so the generator can query the API. When
   executed within Home Assistant it automatically uses its own credentials.
Entities are grouped by area when possible; if no areas are available they are
placed in a single "Auto Detected" room. Within each area the devices are
organized into light, climate, multimedia and sensor sections to create a cleaner layout.
If you notice duplicate cards after customizing rooms, mark the generated "Auto Detected" room with `hidden: true` or remove domains you do not need from the configuration.

Set the `SHI_LANG` environment variable (for example `en`, `ru`, `bg`, or `es`) to
generate the dashboard in a different language.

## Plugins

Modules placed in `custom_components/smart_dashboard/plugins` can modify the configuration before generation. Each module should define `process_config(config)`.



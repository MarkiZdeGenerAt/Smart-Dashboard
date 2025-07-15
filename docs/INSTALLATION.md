# Installation Guide

Follow these steps to install the SHI Dashboard custom integration into Home Assistant.

## Install with HACS
1. In HACS, add `https://github.com/user/Smart-Dashboard` as a custom repository of type "integration".
2. Search for **SHI Dashboard** and install it.
3. Open **Settings → Devices & Services** in Home Assistant and click **Add Integration**.
   Choose **SHI Dashboard** to create the configuration entry.
4. Restart Home Assistant to activate the integration.

## Generate Your First Dashboard
1. The first start creates `shi_dashboard.yaml` and `dashboards/shi_dashboard.yaml` automatically.
2. Add this block to your `configuration.yaml` so the dashboard appears in the sidebar:

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
3. Reload Lovelace or restart Home Assistant to see the dashboard.
4. To regenerate manually, run:

   ```bash
 python3 custom_components/shi_dashboard/dashboard.py shi_dashboard.yaml \
      --output dashboards/shi_dashboard.yaml
  ```

You can also define a Lovelace theme by adding `theme: <name>` to
`shi_dashboard.yaml`.

Rooms may specify an `order` field so they appear in a custom sequence on the
dashboard.

   Pass `--template <template.j2>` to use a custom Jinja2 template if desired.

   Auto discovery is on by default. When running outside Home Assistant **be sure**
   to set `HASS_URL` and `HASS_TOKEN` so the generator can query the API. When
   executed within Home Assistant it automatically uses its own credentials.
Entities are grouped by area when possible; if no areas are available they are
placed in a single "Auto Detected" room.

Set the `SHI_LANG` environment variable (for example `en`, `ru`, or `bg`) to
generate the dashboard in a different language.

## Plugins

Modules placed in `custom_components/shi_dashboard/plugins` can modify the
configuration before generation. Each module should define
`process_config(config)`. See `header_card.py` for an example.



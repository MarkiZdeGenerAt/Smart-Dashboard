"""Utility to generate a SHI Dashboard Lovelace configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional
import argparse
import os
import asyncio
import yaml
import requests
from jinja2 import Template
import logging
import sys
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

# Allow running this file directly
if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    __package__ = "shi_dashboard"

try:
    from .plugins import load_plugins, run_plugins
except ImportError:  # pragma: no cover - running as script
    from plugins import load_plugins, run_plugins  # type: ignore


logger = logging.getLogger(__name__)


# Default Jinja2 template used when ``--template`` is not provided.
_DEFAULT_TEMPLATE = Template(
    """
views:
{% for room in rooms %}
  - title: {{ room.name }}
    cards:
{% for card in room.cards %}
      -{% for k, v in card.items() %}
        {{ k }}: {{ v }}
{% endfor %}
{% endfor %}
{% endfor %}
"""
)


def load_config(path: Path) -> Dict[str, Any]:
    """Load a YAML configuration file."""
    with path.open() as f:
        return yaml.safe_load(f) or {}


def discover_devices(hass_url: str, token: str) -> List[Dict[str, Any]]:
    """Return rooms generated from available Home Assistant devices."""

    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.get(
        f"{hass_url.rstrip('/')}/api/states",
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    states = resp.json()

    # Try to fetch area, device and entity registries to map entities to areas
    areas: Dict[str | None, str] = {}
    try:
        a_resp = requests.get(
            f"{hass_url.rstrip('/')}/api/areas",
            headers=headers,
            timeout=10,
        )
        a_resp.raise_for_status()
        for area in a_resp.json():
            area_id = area.get("area_id") or area.get("id")
            name = area.get("name") or "Area"
            areas[area_id] = name
    except Exception:  # pragma: no cover - runtime environment
        logger.info("Area lookup failed, falling back to single room")

    device_areas: Dict[str, str | None] = {}
    try:
        d_resp = requests.get(
            f"{hass_url.rstrip('/')}/api/devices",
            headers=headers,
            timeout=10,
        )
        d_resp.raise_for_status()
        for dev in d_resp.json():
            dev_id = dev.get("id") or dev.get("device_id")
            device_areas[dev_id] = dev.get("area_id")
    except Exception:  # pragma: no cover - runtime environment
        pass

    entity_devices: Dict[str, str] = {}
    try:
        e_resp = requests.get(
            f"{hass_url.rstrip('/')}/api/entities",
            headers=headers,
            timeout=10,
        )
        e_resp.raise_for_status()
        for ent in e_resp.json():
            entity_devices[ent.get("entity_id")] = ent.get("device_id")
    except Exception:  # pragma: no cover - runtime environment
        pass

    rooms: Dict[str, List[Dict[str, Any]]] = {}
    for state in states:
        entity_id = state.get("entity_id")
        if not entity_id:
            continue
        domain = entity_id.split(".")[0]
        card_type = {
            "light": "light",
            "switch": "switch",
            "climate": "thermostat",
            "sensor": "sensor",
            "cover": "cover",
            "media_player": "media-control",
            "binary_sensor": "sensor",
        }.get(domain, "entity")

        device_id = entity_devices.get(entity_id)
        area_id = device_areas.get(device_id)
        area_name = (
            areas.get(area_id, "Auto Detected") if areas else "Auto Detected"
        )
        rooms.setdefault(area_name, []).append(
            {"type": card_type, "entity": entity_id}
        )

    return [{"name": name, "cards": cards} for name, cards in rooms.items()]


async def async_discover_devices_internal(
    hass: HomeAssistant,
) -> List[Dict[str, Any]]:
    """Return rooms generated using Home Assistant's internal registries."""

    states = hass.states.async_all()

    area_reg = await ar.async_get_registry(hass)
    device_reg = await dr.async_get_registry(hass)
    entity_reg = await er.async_get_registry(hass)

    areas: Dict[str | None, str] = {
        area.id: area.name for area in area_reg.async_list_areas()
    }
    device_areas: Dict[str, str | None] = {
        device.id: device.area_id for device in device_reg.devices.values()
    }
    entity_devices: Dict[str, str] = {
        ent.entity_id: ent.device_id for ent in entity_reg.entities.values()
    }

    rooms: Dict[str, List[Dict[str, Any]]] = {}
    for state in states:
        entity_id = state.entity_id
        domain = entity_id.split(".")[0]
        card_type = {
            "light": "light",
            "switch": "switch",
            "climate": "thermostat",
            "sensor": "sensor",
            "cover": "cover",
            "media_player": "media-control",
            "binary_sensor": "sensor",
        }.get(domain, "entity")

        device_id = entity_devices.get(entity_id)
        area_id = device_areas.get(device_id)
        area_name = (
            areas.get(area_id, "Auto Detected") if areas else "Auto Detected"
        )
        rooms.setdefault(area_name, []).append(
            {"type": card_type, "entity": entity_id}
        )

    return [{"name": name, "cards": cards} for name, cards in rooms.items()]


def build_dashboard(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convert the config into a Lovelace dashboard structure."""
    views = []
    for room in config.get("rooms", []):
        cards = room.get("cards", [])
        layout = room.get("layout")
        if layout in ("horizontal", "vertical"):
            cards = [{"type": f"{layout}-stack", "cards": cards}]

        views.append({"title": room.get("name", "Room"), "cards": cards})

    dashboard = {"views": views}
    if "layout" in config:
        dashboard["layout"] = config["layout"]
    return dashboard


def load_template(path: Path | None) -> Template:
    """Return a ``Template`` either from ``path`` or the default template."""
    if path is None:
        return _DEFAULT_TEMPLATE
    with path.open() as f:
        return Template(f.read())


def generate_dashboard(
    config_path: Path,
    output_path: Path,
    template_path: Path | None = None,
    hass: Optional[HomeAssistant] = None,
) -> None:
    """Generate a dashboard file from config_path written to output_path."""

    config = load_config(config_path)

    # Load and execute any available plugins before building the dashboard
    load_plugins()
    run_plugins(config)

    if config.get("auto_discover"):
        if hass is not None:
            try:
                future = asyncio.run_coroutine_threadsafe(
                    async_discover_devices_internal(hass), hass.loop
                )
                rooms = future.result()
                config.setdefault("rooms", []).extend(rooms)
            except Exception:
                logger.exception("Device discovery failed")
        else:
            hass_url = os.environ.get(
                "HASS_URL", "http://localhost:8123"
            )
            token = os.environ.get("HASS_TOKEN")
            if token:
                try:
                    config.setdefault("rooms", []).extend(
                        discover_devices(hass_url, token)
                    )
                except Exception:
                    logger.exception("Device discovery failed")
            else:
                logger.error("auto_discover enabled but HASS_TOKEN is not set")

    if template_path is not None:
        template = load_template(template_path)
        rendered = template.render(rooms=config.get("rooms", []))
    else:
        dashboard = build_dashboard(config)
        rendered = yaml.safe_dump(dashboard, sort_keys=False)

    output_path.write_text(rendered)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Generate SHI Dashboard config"
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to shi_dashboard.yaml configuration",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("generated_dashboard.yaml"),
        help="Output path for generated Lovelace config",
    )
    parser.add_argument(
        "--template",
        type=Path,
        help="Optional Jinja2 template used to render the dashboard",
    )

    args = parser.parse_args()
    try:
        generate_dashboard(args.config, args.output, args.template)
    except Exception:
        logger.exception("Dashboard generation failed")
        sys.exit(1)
    print(f"Dashboard configuration written to {args.output}")


if __name__ == "__main__":
    main()

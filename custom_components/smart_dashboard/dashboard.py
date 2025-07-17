"""Utility to generate a Smart Dashboard Lovelace configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import argparse
import os
import asyncio
import yaml
import requests
import voluptuous as vol
from jinja2 import Template
import logging
import sys
import json
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

# Allow running this file directly
if __name__ == "__main__" and __package__ is None:
    sys.path.append(str(Path(__file__).resolve().parents[1]))
    __package__ = "smart_dashboard"

try:
    from .plugins import load_plugins, run_plugins
    from .schema import CONFIG_SCHEMA
except ImportError:  # pragma: no cover - running as script
    from plugins import load_plugins, run_plugins  # type: ignore
    from schema import CONFIG_SCHEMA  # type: ignore


logger = logging.getLogger(__name__)


# --- Translation helpers ----------------------------------------------------
_TRANSLATIONS: Dict[str, Dict[str, str]] = {}


# Translations are loaded lazily by ``load_translations`` to avoid blocking I/O
# during import when the Home Assistant event loop is already running.


async def load_translations(lang: str) -> Dict[str, str]:
    """Return translation dictionary for *lang* using a background thread."""
    if lang not in _TRANSLATIONS:
        trans_path = Path(__file__).parent / "translations" / f"{lang}.json"
        if not trans_path.exists():
            _TRANSLATIONS[lang] = {}
        else:
            def _read() -> Dict[str, str]:
                with trans_path.open() as f:
                    return json.load(f)

            try:
                _TRANSLATIONS[lang] = await asyncio.to_thread(_read)
            except Exception:  # pragma: no cover - runtime environment
                _TRANSLATIONS[lang] = {}
    return _TRANSLATIONS.get(lang, {})


async def t(key: str, lang: str, default: str) -> str:
    """Return translated string for ``key`` or ``default`` if missing."""
    translations = await load_translations(lang)
    return translations.get(key, default)


def _slugify(text: str) -> str:
    """Return *text* converted to a URL slug."""
    slug = "".join(c.lower() if c.isalnum() else "-" for c in text)
    parts = [p for p in slug.split("-") if p]
    return "-".join(parts)


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


_DEVICE_TEMPLATE_MAP = {
    "light": "light_tile",
    "climate": "climate_tile",
    "media_player": "media_tile",
    "sensor": "sensor_tile",
    "binary_sensor": "sensor_tile",
}


def _apply_tile_templates(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return cards converted to button-card tiles using templates."""
    result: List[Dict[str, Any]] = []
    for card in cards:
        entity = card.get("entity")
        domain = entity.split(".")[0] if isinstance(entity, str) else None
        template = _DEVICE_TEMPLATE_MAP.get(domain)
        if template:
            result.append(
                {
                    "type": "custom:button-card",
                    "template": template,
                    "entity": entity,
                }
            )
        else:
            result.append(card)
    return result


def _get_known_entities(hass: Optional[HomeAssistant]) -> Set[str]:
    """Return a set of known entity IDs."""
    if hass is not None:
        return {state.entity_id for state in hass.states.async_all()}

    token = os.environ.get("HASS_TOKEN")
    if not token:
        logger.warning("HASS_TOKEN not set; cannot fetch entity list")
        return set()

    url = os.environ.get("HASS_URL", "http://localhost:8123").rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        resp = requests.get(f"{url}/api/states", headers=headers, timeout=10)
        resp.raise_for_status()
        return {
            item.get("entity_id")
            for item in resp.json()
            if item.get("entity_id") is not None
        }
    except Exception:  # pragma: no cover - runtime environment
        logger.warning("Failed to fetch entity list", exc_info=True)
        return set()


def filter_existing_entities(
    config: Dict[str, Any], hass: Optional[HomeAssistant] = None
) -> None:
    """Remove cards referencing missing entities from *config*."""
    known = _get_known_entities(hass)
    if not known:
        logger.warning("Entity list empty; skipping entity filtering")
        return
    for room in config.get("rooms", []):
        cards = []
        for card in room.get("cards", []):
            if isinstance(card, dict):
                entity = card.get("entity")
                if entity and entity not in known:
                    continue
            cards.append(card)
        room["cards"] = cards


def deduplicate_cards(config: Dict[str, Any]) -> None:
    """Remove duplicate card definitions within each room."""
    for room in config.get("rooms", []):
        seen: Set[str] = set()
        unique: List[Dict[str, Any]] = []
        for card in room.get("cards", []):
            if isinstance(card, dict):
                key = json.dumps(card, sort_keys=True)
                if key in seen:
                    continue
                seen.add(key)
            unique.append(card)
        room["cards"] = unique


def _build_condition_context() -> Dict[str, Any]:
    """Return evaluation context populated with environment variables."""
    ctx: Dict[str, Any] = dict(os.environ)
    user = ctx.get("DASHBOARD_USER") or ctx.get("SD_USER") or ctx.get("USER")
    if user is not None:
        ctx.setdefault("user", user)
    return ctx


def _eval_condition(expr: str, ctx: Dict[str, Any]) -> bool:
    """Safely evaluate a condition expression using *ctx*."""
    try:
        return bool(eval(expr, {"__builtins__": {}}, ctx))
    except Exception:
        logger.error("Failed to evaluate condition '%s'", expr)
        return False


def apply_conditions(config: Dict[str, Any]) -> None:
    """Remove rooms and sidebar items whose conditions evaluate to False."""
    ctx = _build_condition_context()

    if "rooms" in config:
        filtered_rooms = []
        for room in config["rooms"]:
            conds = room.get("conditions") or []
            if all(_eval_condition(c, ctx) for c in conds):
                filtered_rooms.append(room)
        config["rooms"] = filtered_rooms

    if "sidebar" in config:
        filtered_sidebar = []
        for item in config["sidebar"]:
            cond = item.get("condition")
            if cond is None or _eval_condition(cond, ctx):
                item.pop("condition", None)
                filtered_sidebar.append(item)
        config["sidebar"] = filtered_sidebar



def load_config(path: Path) -> Dict[str, Any]:
    """Load a YAML configuration file."""
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    try:
        return CONFIG_SCHEMA(data)
    except vol.Invalid as exc:
        raise ValueError(f"Invalid configuration: {exc}") from exc


def _group_cards_by_type(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return cards grouped into stacks by device type and converted to tiles."""
    cards = _apply_tile_templates(cards)
    groups = {
        "light": [],
        "climate": [],
        "multimedia": [],
        "sensor": [],
        "other": [],
    }
    for card in cards:
        entity = card.get("entity")
        domain = entity.split(".")[0] if isinstance(entity, str) else ""
        if domain == "light":
            groups["light"].append(card)
        elif domain == "climate":
            groups["climate"].append(card)
        elif domain == "media_player":
            groups["multimedia"].append(card)
        elif domain in ("sensor", "binary_sensor"):
            groups["sensor"].append(card)
        else:
            groups["other"].append(card)

    result: List[Dict[str, Any]] = []
    if groups["light"]:
        result.append({"type": "vertical-stack", "cards": groups["light"]})
    if groups["climate"]:
        result.append({"type": "vertical-stack", "cards": groups["climate"]})
    if groups["multimedia"]:
        result.append({"type": "vertical-stack", "cards": groups["multimedia"]})
    if groups["sensor"]:
        result.append({"type": "vertical-stack", "cards": groups["sensor"]})
    result.extend(groups["other"])
    return result


def discover_devices(
    hass_url: str, token: str, lang: str
) -> List[Dict[str, Any]]:
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
    seen_entities: Set[str] = set()
    for state in states:
        entity_id = state.get("entity_id")
        if not entity_id or entity_id in seen_entities:
            continue
        seen_entities.add(entity_id)
        domain = entity_id.split(".")[0]
        card_type = {
            "light": "light",
            "switch": "entity",
            "climate": "thermostat",
            "sensor": "sensor",
            "cover": "entity",
            "media_player": "media-control",
            "binary_sensor": "sensor",
        }.get(domain, "entity")

        device_id = entity_devices.get(entity_id)
        area_id = device_areas.get(device_id)
        area_name = (
            areas.get(area_id, asyncio.run(t("auto_detected", lang, "Auto Detected")))
            if areas
            else asyncio.run(t("auto_detected", lang, "Auto Detected"))
        )
        rooms.setdefault(area_name, []).append(
            {"type": card_type, "entity": entity_id}
        )

    return [
        {"name": name, "cards": _group_cards_by_type(cards)}
        for name, cards in rooms.items()
    ]


async def async_discover_devices_internal(
    hass: HomeAssistant,
    lang: str,
) -> List[Dict[str, Any]]:
    """Return rooms generated using Home Assistant's internal registries."""

    states = hass.states.async_all()

    area_reg = ar.async_get(hass)
    device_reg = dr.async_get(hass)
    entity_reg = er.async_get(hass)

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
    seen_entities: Set[str] = set()
    for state in states:
        entity_id = state.entity_id
        if entity_id in seen_entities:
            continue
        seen_entities.add(entity_id)
        domain = entity_id.split(".")[0]
        card_type = {
            "light": "light",
            "switch": "entity",
            "climate": "thermostat",
            "sensor": "sensor",
            "cover": "entity",
            "media_player": "media-control",
            "binary_sensor": "sensor",
        }.get(domain, "entity")

        device_id = entity_devices.get(entity_id)
        area_id = device_areas.get(device_id)
        area_name = (
            areas.get(area_id, await t("auto_detected", lang, "Auto Detected"))
            if areas
            else await t("auto_detected", lang, "Auto Detected")
        )
        rooms.setdefault(area_name, []).append(
            {"type": card_type, "entity": entity_id}
        )

    return [
        {"name": name, "cards": _group_cards_by_type(cards)}
        for name, cards in rooms.items()
    ]


def build_dashboard(config: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """Convert the config into a Lovelace dashboard structure."""
    views = []
    rooms = sorted(
        config.get("rooms", []),
        key=lambda r: r.get("order", 0)
    )

    overview_cards = []
    for room in rooms:
        if room.get("hidden"):
            continue
        name = room.get("name", asyncio.run(t("room", lang, "Room")))
        path = _slugify(name)
        icon = room.get("icon", "mdi:home-outline")
        active_count = sum(
            1 for card in room.get("cards", []) if isinstance(card, dict) and card.get("entity")
        )
        tile_cards = _apply_tile_templates(room.get("cards", []))[:4]
        stack = {
            "type": "vertical-stack",
            "cards": [
                {
                    "type": "custom:button-card",
                    "icon": icon,
                    "name": name,
                    "label": asyncio.run(
                        t("device_count", lang, "{count} devices")
                    ).format(count=active_count),
                    "tap_action": {
                        "action": "navigate",
                        "navigation_path": f"/lovelace/{path}",
                    },
                }
            ],
        }
        if tile_cards:
            stack["cards"].append(
                {
                    "type": "grid",
                    "columns": 2,
                    "square": False,
                    "cards": tile_cards,
                }
            )
        overview_cards.append(stack)

    if overview_cards:
        views.append({
            "title": asyncio.run(t("overview", lang, "Overview")),
            "path": "overview",
            "cards": [
                {
                    "type": "grid",
                    "columns": 2,
                    "square": False,
                    "cards": overview_cards,
                }
            ],
        })

    # Device overview showing all cards grouped by type
    device_cards: List[Dict[str, Any]] = []
    for room in rooms:
        if room.get("hidden"):
            continue
        device_cards.extend(room.get("cards", []))
    grouped_devices = _group_cards_by_type(device_cards)
    if grouped_devices:
        views.append({
            "title": asyncio.run(t("devices", lang, "Devices")),
            "path": "devices",
            "cards": [
                {
                    "type": "grid",
                    "columns": 2,
                    "square": False,
                    "cards": grouped_devices,
                }
            ],
        })

    for room in rooms:
        if room.get("hidden"):
            continue
        cards = _apply_tile_templates(room.get("cards", []))
        if not cards:
            cards = [
                {
                    "type": "custom:button-card",
                    "icon": "mdi:help-circle-outline",
                    "name": asyncio.run(t("no_entities", lang, "No entities")),
                }
            ]
        layout = room.get("layout")
        if layout in ("horizontal", "vertical"):
            cards = [{"type": f"{layout}-stack", "cards": cards}]
        else:
            cards = [
                {
                    "type": "grid",
                    "columns": 2,
                    "square": False,
                    "cards": cards,
                }
            ]

        name = room.get("name", asyncio.run(t("room", lang, "Room")))
        views.append({
            "title": name,
            "path": _slugify(name),
            "cards": cards,
        })

    dashboard = {"views": views}
    dashboard["button_card_templates"] = {
        "device_tile": {
            "show_icon": True,
            "show_name": True,
            "show_state": True,
            "layout": "vertical",
            "styles": {
                "card": [
                    "padding: 8px",
                    "background: var(--ha-card-background, rgba(0,0,0,0.05))",
                    "border-radius: 12px",
                ]
            },
        },
        "light_tile": {"template": "device_tile", "tap_action": {"action": "toggle"}},
        "climate_tile": {"template": "device_tile"},
        "sensor_tile": {"template": "device_tile"},
        "media_tile": {"template": "device_tile"},
    }
    if "layout" in config:
        dashboard["layout"] = config["layout"]
    if "theme" in config:
        dashboard["theme"] = config["theme"]
    if "header" in config:
        dashboard["header"] = config["header"]
    if "sidebar" in config:
        dashboard["sidebar"] = config["sidebar"]
    if "resources" in config:
        dashboard["resources"] = config["resources"]
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

    lang = os.environ.get("SHI_LANG", "en")
    config = load_config(config_path)

    # Disable auto discovery if we cannot fetch entities from the API
    if config.get("auto_discover") and not _get_known_entities(hass):
        logger.warning(
            "auto_discover disabled because entity list could not be retrieved"
        )
        config["auto_discover"] = False

    if config.get("auto_discover"):
        if hass is not None:
            try:
                future = asyncio.run_coroutine_threadsafe(
                    async_discover_devices_internal(hass, lang), hass.loop
                )
                rooms = future.result()
                config.setdefault("rooms", []).extend(rooms)
                logger.info("Auto discovered %d rooms", len(rooms))
            except Exception:
                logger.exception("Device discovery failed")
        else:
            hass_url = os.environ.get(
                "HASS_URL", "http://localhost:8123"
            )
            token = os.environ.get("HASS_TOKEN")
            if token:
                try:
                    rooms = discover_devices(hass_url, token, lang)
                    config.setdefault("rooms", []).extend(rooms)
                    logger.info("Auto discovered %d rooms", len(rooms))
                except Exception:
                    logger.exception("Device discovery failed")
            else:
                logger.error("auto_discover enabled but HASS_TOKEN is not set")

    # Load and execute any available plugins after building the config
    load_plugins()
    run_plugins(config)

    apply_conditions(config)

    filter_existing_entities(config, hass)
    deduplicate_cards(config)

    if template_path is not None:
        template = load_template(template_path)
        rendered = template.render(rooms=config.get("rooms", []))
    else:
        dashboard = build_dashboard(config, lang)
        rendered = yaml.safe_dump(dashboard, sort_keys=False)

    output_path.write_text(rendered)


def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s:%(name)s:%(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Generate Smart Dashboard config"
    )
    parser.add_argument(
        "config",
        type=Path,
        help="Path to smart_dashboard.yaml configuration",
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

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml
import voluptuous as vol
from homeassistant.core import HomeAssistant

from .const import DEFAULT_OVERVIEW_LIMIT, DEFAULT_GRID_COLUMNS
from .plugins import load_plugins, run_plugins
from .schema import CONFIG_SCHEMA
from .templates import (
    apply_tile_templates,
    load_template,
    BUTTON_CARD_TEMPLATES,
)
from .translation import t
from .auto_discovery import (
    discover_devices,
    async_discover_devices_internal,
    _get_known_entities,
    _group_cards_by_type,
)

logger = logging.getLogger(__name__)


def _slugify(text: str) -> str:
    """Return *text* converted to a URL slug."""
    slug = "".join(c.lower() if c.isalnum() else "-" for c in text)
    parts = [p for p in slug.split("-") if p]
    return "-".join(parts)


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


def build_dashboard(config: Dict[str, Any], lang: str) -> Dict[str, Any]:
    """Convert the config into a Lovelace dashboard structure."""
    views = []
    rooms = sorted(
        config.get("rooms", []),
        key=lambda r: r.get("order", 0)
    )
    global_limit = int(config.get("overview_limit", DEFAULT_OVERVIEW_LIMIT))

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
        room_limit = int(room.get("overview_limit", global_limit))
        tile_cards = apply_tile_templates(room.get("cards", []))[:room_limit]
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
                    "columns": int(room.get("columns", DEFAULT_GRID_COLUMNS)),
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
        cards = apply_tile_templates(room.get("cards", []))
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
                    "columns": int(room.get("columns", DEFAULT_GRID_COLUMNS)),
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

    if not views:
        views.append({
            "title": asyncio.run(t("dashboard_title", lang, "Smart Dashboard")),
            "cards": [
                {
                    "type": "markdown",
                    "content": asyncio.run(t("no_devices_found", lang, "No devices found.")),
                }
            ],
        })

    dashboard = {"views": views}
    dashboard["button_card_templates"] = BUTTON_CARD_TEMPLATES
    if "layout" in config:
        dashboard["layout"] = config["layout"]
    if "theme" in config:
        dashboard["theme"] = config["theme"]
    if "header" in config:
        dashboard["header"] = config["header"]
    if "sidebar" in config:
        dashboard["sidebar"] = config["sidebar"]

    resources = list(config.get("resources", []))
    urls = {res.get("url") for res in resources if isinstance(res, dict)}
    if "/hacsfiles/button-card/button-card.js" not in urls:
        resources.append({"url": "/hacsfiles/button-card/button-card.js", "type": "module"})
    if resources:
        dashboard["resources"] = resources
    return dashboard


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

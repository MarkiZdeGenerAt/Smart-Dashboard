"""Utility to generate a SHI Dashboard Lovelace configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
import argparse
import os
import yaml
import requests
from jinja2 import Template
import logging
import sys


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
    """Return a list of rooms generated from available Home Assistant devices."""
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{hass_url.rstrip('/')}/api/states", headers=headers, timeout=10)
    resp.raise_for_status()
    states = resp.json()

    cards = []
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
        }.get(domain, "entity")
        cards.append({"type": card_type, "entity": entity_id})

    return [{"name": "Auto Detected", "cards": cards}]


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
) -> None:
    """Generate a dashboard file from config_path written to output_path."""

    config = load_config(config_path)

    if config.get("auto_discover"):
        hass_url = os.environ.get("HASS_URL", "http://localhost:8123")
        token = os.environ.get("HASS_TOKEN")
        if token:
            try:
                config.setdefault("rooms", []).extend(discover_devices(hass_url, token))
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
    logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
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

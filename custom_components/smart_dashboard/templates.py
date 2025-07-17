from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List
from jinja2 import Template

# Default Jinja2 template used when ``--template`` is not provided.
DEFAULT_TEMPLATE = Template(
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

DEVICE_TEMPLATE_MAP = {
    "light": "light_tile",
    "climate": "climate_tile",
    "media_player": "media_tile",
    "sensor": "sensor_tile",
    "binary_sensor": "sensor_tile",
}

BUTTON_CARD_TEMPLATES: Dict[str, Dict[str, Any]] = {
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


def load_template(path: Path | None) -> Template:
    """Return a ``Template`` either from ``path`` or the default template."""
    if path is None:
        return DEFAULT_TEMPLATE
    with path.open() as f:
        return Template(f.read())


def apply_tile_templates(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return cards converted to button-card tiles using templates."""
    result: List[Dict[str, Any]] = []
    for card in cards:
        entity = card.get("entity")
        domain = entity.split(".")[0] if isinstance(entity, str) else None
        template = DEVICE_TEMPLATE_MAP.get(domain)
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

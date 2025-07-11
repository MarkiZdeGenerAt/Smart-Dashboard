"""Utility to generate a SHI Dashboard Lovelace configuration."""

from pathlib import Path
from typing import Any
import yaml
from jinja2 import Template

_TEMPLATE = Template(
    """
views:
{% for room in rooms %}
  - title: {{ room.name }}
    cards:
{% for card in room.cards %}
      - type: {{ card.type }}
        entity: {{ card.entity }}
{% endfor %}
{% endfor %}
"""
)


def load_config(path: Path) -> dict:
    with path.open() as f:
        return yaml.safe_load(f)


def generate_dashboard(config_path: Path, output_path: Path) -> None:
    config = load_config(config_path)
    rooms = config.get("rooms", [])
    rendered = _TEMPLATE.render(rooms=rooms)
    output_path.write_text(rendered)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate SHI Dashboard config")
    parser.add_argument(
        "config", type=Path, help="Path to shi_dashboard.yaml configuration"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("generated_dashboard.yaml"),
        help="Output path for generated Lovelace config",
    )
    args = parser.parse_args()
    generate_dashboard(args.config, args.output)
    print(f"Dashboard configuration written to {args.output}")

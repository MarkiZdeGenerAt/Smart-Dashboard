"""Utility to generate a SHI Dashboard Lovelace configuration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
import argparse
import yaml
from jinja2 import Template


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


def build_dashboard(config: Dict[str, Any]) -> Dict[str, Any]:
    """Convert the config into a Lovelace dashboard structure."""
    views = []
    for room in config.get("rooms", []):
        views.append(
            {
                "title": room.get("name", "Room"),
                "cards": room.get("cards", []),
            }
        )
    return {"views": views}


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

    if template_path is not None:
        template = load_template(template_path)
        rendered = template.render(rooms=config.get("rooms", []))
    else:
        dashboard = build_dashboard(config)
        rendered = yaml.safe_dump(dashboard, sort_keys=False)

    output_path.write_text(rendered)


def main() -> None:
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
    generate_dashboard(args.config, args.output, args.template)
    print(f"Dashboard configuration written to {args.output}")


if __name__ == "__main__":
    main()

"""Plugin to emulate basic Dwains Dashboard navigation style."""

from __future__ import annotations

from typing import Any, Dict


def _slugify(text: str) -> str:
    slug = "".join(c.lower() if c.isalnum() else "-" for c in text)
    return "-".join(part for part in slug.split("-") if part)


def process_config(config: Dict[str, Any]) -> None:
    """Modify *config* to resemble Dwains Dashboard."""
    # Ensure a visible header with clock
    header = config.setdefault("header", {})
    header.setdefault("title", "Home")
    header.setdefault("show_time", True)

    # Apply Dwains theme if not specified
    config.setdefault("theme", "dwains")

    sidebar = config.setdefault("sidebar", [])
    existing = {item.get("view") for item in sidebar if isinstance(item, dict)}

    for room in config.get("rooms", []):
        name = room.get("name", "Room")
        view = _slugify(name)
        if view in existing:
            continue
        sidebar.append({"name": name, "icon": "mdi:chevron-right", "view": view})
        existing.add(view)

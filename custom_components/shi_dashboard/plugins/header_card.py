"""Example plugin that inserts a header markdown card for each room."""

from __future__ import annotations

from typing import Dict, Any


def process_config(config: Dict[str, Any]) -> None:
    for room in config.get("rooms", []):
        name = room.get("name", "Room")
        cards = room.setdefault("cards", [])
        header = {"type": "markdown", "content": f"## {name}"}
        cards.insert(0, header)

"""Load room blueprints from the blueprints directory."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import yaml


def process_config(config: Dict[str, Any]) -> None:
    blueprints_dir = Path(__file__).resolve().parent.parent / "blueprints"
    if not blueprints_dir.is_dir():
        return
    rooms = config.setdefault("rooms", [])
    for file in blueprints_dir.glob("*.yaml"):
        try:
            with file.open() as f:
                data = yaml.safe_load(f)
            if isinstance(data, dict):
                rooms.append(data)
        except Exception:  # pragma: no cover - runtime environment
            import logging
            logging.getLogger(__name__).error(
                "Failed to load blueprint %s", file
            )

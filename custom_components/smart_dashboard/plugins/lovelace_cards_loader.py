"""Load Lovelace cards from Home Assistant via its API."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

import requests

_LOGGER = logging.getLogger(__name__)


def process_config(config: Dict[str, Any]) -> None:
    """Append rooms generated from the current Lovelace config."""
    if not config.get("load_lovelace_cards"):
        return

    token = os.environ.get("HASS_TOKEN")
    if not token:
        _LOGGER.error("load_lovelace_cards enabled but HASS_TOKEN is not set")
        return

    hass_url = os.environ.get("HASS_URL", "http://localhost:8123").rstrip("/")
    headers = {"Authorization": f"Bearer {token}"}

    try:
        resp = requests.get(f"{hass_url}/api/lovelace", headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as err:  # pragma: no cover - runtime environment
        _LOGGER.error("Failed to load Lovelace config: %s", err)
        return

    views = data.get("views", data.get("data", {}).get("views", []))
    rooms = config.setdefault("rooms", [])
    for idx, view in enumerate(views, 1):
        rooms.append(
            {
                "name": view.get("title", f"View {idx}"),
                "order": idx,
                "cards": view.get("cards", []),
            }
        )


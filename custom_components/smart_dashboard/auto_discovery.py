from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, Dict, List, Optional, Set

import requests
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)

from .translation import t
from .templates import apply_tile_templates

logger = logging.getLogger(__name__)

# Mapping from entity domain to default Lovelace card type.  Used by both
# internal and external discovery to ensure consistent behavior.
DOMAIN_CARD_TYPE: Dict[str, str] = {
    "light": "light",
    "switch": "light",
    "climate": "thermostat",
    "sensor": "sensor",
    "cover": "cover",
    "media_player": "media-control",
    "binary_sensor": "sensor",
}


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
    except Exception:
        logger.warning("Failed to fetch entity list", exc_info=True)
        return set()


def _group_cards_by_type(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Return cards grouped into stacks by device type and converted to tiles."""
    cards = apply_tile_templates(cards)
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


def discover_devices(hass_url: str, token: str, lang: str) -> List[Dict[str, Any]]:
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
    except Exception:
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
    except Exception:
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
    except Exception:
        pass

    rooms: Dict[str, List[Dict[str, Any]]] = {}
    seen_entities: Set[str] = set()
    for state in states:
        entity_id = state.get("entity_id")
        if not entity_id or entity_id in seen_entities:
            continue
        seen_entities.add(entity_id)
        domain = entity_id.split(".")[0]
        card_type = DOMAIN_CARD_TYPE.get(domain, "entity")

        device_id = entity_devices.get(entity_id)
        area_id = device_areas.get(device_id)
        area_name = (
            areas.get(area_id, asyncio.run(t("auto_detected", lang, "Auto Detected")))
            if areas
            else asyncio.run(t("auto_detected", lang, "Auto Detected"))
        )
        rooms.setdefault(area_name, []).append({"type": card_type, "entity": entity_id})

    return [
        {"name": name, "cards": _group_cards_by_type(cards)}
        for name, cards in rooms.items()
    ]


async def async_discover_devices_internal(
    hass: HomeAssistant, lang: str
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
        card_type = DOMAIN_CARD_TYPE.get(domain, "entity")

        device_id = entity_devices.get(entity_id)
        area_id = device_areas.get(device_id)
        area_name = (
            areas.get(area_id, await t("auto_detected", lang, "Auto Detected"))
            if areas
            else await t("auto_detected", lang, "Auto Detected")
        )
        rooms.setdefault(area_name, []).append({"type": card_type, "entity": entity_id})

    return [
        {"name": name, "cards": _group_cards_by_type(cards)}
        for name, cards in rooms.items()
    ]


__all__ = [
    "discover_devices",
    "async_discover_devices_internal",
    "_get_known_entities",
    "_group_cards_by_type",
]

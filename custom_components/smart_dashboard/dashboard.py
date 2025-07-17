"""Compatibility wrapper importing dashboard utilities from submodules."""

import requests

from .generator import (
    generate_dashboard,
    build_dashboard,
    load_config,
    filter_existing_entities,
    deduplicate_cards,
    apply_conditions,
    main,
)
from .auto_discovery import (
    discover_devices,
    async_discover_devices_internal,
    _get_known_entities,
    _group_cards_by_type,
)
from .templates import (
    load_template,
    apply_tile_templates,
    BUTTON_CARD_TEMPLATES,
    DEVICE_TEMPLATE_MAP,
    DEFAULT_TEMPLATE,
)
from .translation import load_translations, t

__all__ = [
    "generate_dashboard",
    "build_dashboard",
    "load_config",
    "filter_existing_entities",
    "deduplicate_cards",
    "apply_conditions",
    "discover_devices",
    "async_discover_devices_internal",
    "_get_known_entities",
    "_group_cards_by_type",
    "load_template",
    "apply_tile_templates",
    "BUTTON_CARD_TEMPLATES",
    "DEVICE_TEMPLATE_MAP",
    "DEFAULT_TEMPLATE",
    "load_translations",
    "t",
    "main",
]

if __name__ == "__main__":
    main()

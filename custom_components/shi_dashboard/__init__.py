"""SHI Dashboard custom integration."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.core import HomeAssistant

from .dashboard import generate_dashboard

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Automatically generate config and dashboard on first install."""
    config_path = Path(hass.config.path("shi_dashboard.yaml"))
    if not config_path.exists():
        example = Path(__file__).parent / "config" / "example_config.yaml"
        try:
            shutil.copy(example, config_path)
            _LOGGER.info("Created default configuration at %s", config_path)
        except OSError as err:
            _LOGGER.error("Failed to copy default config: %s", err)

    output_path = Path(hass.config.path("ui-lovelace.yaml"))
    try:
        generate_dashboard(config_path, output_path)
        _LOGGER.info("Generated dashboard at %s", output_path)
    except Exception as err:  # pragma: no cover - runtime environment
        _LOGGER.error("Dashboard generation failed: %s", err)

    return True


__all__ = ["generate_dashboard", "async_setup"]

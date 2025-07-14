"""SHI Dashboard custom integration."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DASHBOARD_DIR, DASHBOARD_FILE

from .dashboard import generate_dashboard

_LOGGER = logging.getLogger(__name__)


def _create_default_config(hass: HomeAssistant) -> Path:
    """Ensure default configuration exists and return its path."""
    config_path = Path(hass.config.path("shi_dashboard.yaml"))
    if not config_path.exists():
        example = Path(__file__).parent / "config" / "example_config.yaml"
        try:
            shutil.copy(example, config_path)
            _LOGGER.info("Created default configuration at %s", config_path)
        except OSError as err:
            _LOGGER.error("Failed to copy default config: %s", err)
    return config_path


async def _generate_dashboard_files(hass: HomeAssistant) -> None:
    """Generate dashboard files from configuration."""
    config_path = _create_default_config(hass)
    output_dir = Path(hass.config.path(DASHBOARD_DIR))
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / DASHBOARD_FILE
    try:
        await hass.async_add_executor_job(
            generate_dashboard, config_path, output_path, None, hass
        )
        _LOGGER.info("Generated dashboard at %s", output_path)
    except Exception as err:  # pragma: no cover - runtime environment
        _LOGGER.error("Dashboard generation failed: %s", err)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via YAML is deprecated; create files and do nothing else."""
    await _generate_dashboard_files(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SHI Dashboard from a config entry."""
    await _generate_dashboard_files(hass)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = True
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    return True


__all__ = [
    "generate_dashboard",
    "async_setup",
    "async_setup_entry",
    "async_unload_entry",
]

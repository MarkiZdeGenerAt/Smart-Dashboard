"""Smart Dashboard custom integration."""

from __future__ import annotations

import logging
import shutil
from pathlib import Path
try:  # pragma: no cover - optional dependency for tests
    from homeassistant.util.yaml import load_yaml_dict, save_yaml
except Exception:  # pragma: no cover - environment without Home Assistant
    import yaml

    def load_yaml_dict(path: Path) -> dict:
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def save_yaml(path: str, data: dict) -> None:
        Path(path).write_text(yaml.safe_dump(data, sort_keys=False))

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN, DASHBOARD_DIR, DASHBOARD_FILE

from .dashboard import generate_dashboard

_LOGGER = logging.getLogger(__name__)


def _create_default_config(hass: HomeAssistant) -> Path:
    """Ensure default configuration exists and return its path."""
    config_path = Path(hass.config.path("smart_dashboard.yaml"))
    if not config_path.exists():
        example = Path(__file__).parent / "config" / "example_config.yaml"
        try:
            shutil.copy(example, config_path)
            _LOGGER.info("Created default configuration at %s", config_path)
        except OSError as err:
            _LOGGER.error("Failed to copy default config: %s", err)
    return config_path


def _ensure_dashboard_entry(hass: HomeAssistant) -> None:
    """Insert Smart Dashboard entry into configuration.yaml if missing."""
    cfg_path = Path(hass.config.path("configuration.yaml"))
    data: dict = {}
    if cfg_path.exists():
        try:
            data = load_yaml_dict(cfg_path)
        except Exception as err:  # pragma: no cover - runtime environment
            _LOGGER.error("Failed to read %s: %s", cfg_path, err)
            return
    lovelace = data.setdefault("lovelace", {})
    dashboards = lovelace.setdefault("dashboards", {})
    if "smart-dashboard" in dashboards:
        return
    dashboards["smart-dashboard"] = {
        "mode": "yaml",
        "title": "Smart Dashboard",
        "icon": "mdi:monitor-dashboard",
        "show_in_sidebar": True,
        "filename": "dashboards/smart_dashboard.yaml",
    }
    try:
        save_yaml(str(cfg_path), data)
        _LOGGER.info("Added Smart Dashboard to %s", cfg_path)
    except Exception as err:  # pragma: no cover - runtime environment
        _LOGGER.error("Failed to update %s: %s", cfg_path, err)


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
    await hass.async_add_executor_job(_ensure_dashboard_entry, hass)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up via YAML is deprecated; create files and do nothing else."""
    await _generate_dashboard_files(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Smart Dashboard from a config entry."""
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

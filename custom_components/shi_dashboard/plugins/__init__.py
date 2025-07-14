"""Plugin system for SHI Dashboard."""

from __future__ import annotations

from importlib import import_module, util
from pathlib import Path
from typing import Callable, Dict, Any, List

PLUGINS: List[Callable[[Dict[str, Any]], None]] = []


def load_plugins() -> None:
    """Load all plugins from the plugins directory."""
    plugins_dir = Path(__file__).parent
    for file in plugins_dir.glob("*.py"):
        if file.stem == "__init__":
            continue
        module_name = f"shi_dashboard_plugin_{file.stem}"
        spec = util.spec_from_file_location(module_name, file)
        if spec and spec.loader:
            module = util.module_from_spec(spec)
            spec.loader.exec_module(module)
        else:
            continue
        if hasattr(module, "process_config"):
            PLUGINS.append(module.process_config)


def run_plugins(config: Dict[str, Any]) -> None:
    """Run all loaded plugins on the config."""
    for plugin in PLUGINS:
        try:
            plugin(config)
        except Exception as err:  # pragma: no cover - plugin errors shouldn't crash
            import logging
            logging.getLogger(__name__).error("Plugin %s failed: %s", plugin.__name__, err)

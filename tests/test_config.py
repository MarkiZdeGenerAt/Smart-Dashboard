import yaml
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import types

dummy = types.ModuleType("dummy")
sys.modules.setdefault("homeassistant", dummy)
core_mod = types.ModuleType("core")
core_mod.HomeAssistant = object
sys.modules.setdefault("homeassistant.core", core_mod)
sys.modules.setdefault("homeassistant.helpers", types.ModuleType("helpers"))
helpers_mod = sys.modules["homeassistant.helpers"]
helpers_mod.area_registry = types.ModuleType("area_registry")
helpers_mod.device_registry = types.ModuleType("device_registry")
helpers_mod.entity_registry = types.ModuleType("entity_registry")
sys.modules.setdefault("homeassistant.helpers.area_registry", helpers_mod.area_registry)
sys.modules.setdefault("homeassistant.helpers.device_registry", helpers_mod.device_registry)
sys.modules.setdefault("homeassistant.helpers.entity_registry", helpers_mod.entity_registry)
sys.modules.setdefault("homeassistant.config_entries", types.ModuleType("config_entries"))
sys.modules["homeassistant.config_entries"].ConfigEntry = object

from custom_components.smart_dashboard.dashboard import load_config


def test_load_valid_config(tmp_path):
    cfg = {"rooms": [{"name": "Living", "cards": [{"type": "light"}]}]}
    path = tmp_path / "cfg.yaml"
    path.write_text(yaml.safe_dump(cfg))
    data = load_config(path)
    assert data["rooms"][0]["name"] == "Living"


def test_load_invalid_config(tmp_path):
    cfg = {"rooms": [{"name": 123}]}
    path = tmp_path / "cfg.yaml"
    path.write_text(yaml.safe_dump(cfg))
    with pytest.raises(ValueError):
        load_config(path)

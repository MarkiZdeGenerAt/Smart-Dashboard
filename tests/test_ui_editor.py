import sys
from pathlib import Path
import types

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

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

from custom_components.smart_dashboard.ui_config_editor import (
    move_card,
    set_room_hidden,
    add_shortcut,
)


def test_move_card():
    cfg = {"rooms": [{"name": "Room", "cards": [{"id": 1}, {"id": 2}]}]}
    move_card(cfg, "Room", 0, 1)
    assert cfg["rooms"][0]["cards"][1]["id"] == 1


def test_hide_room():
    cfg = {"rooms": [{"name": "Room", "cards": []}]}
    set_room_hidden(cfg, "Room", True)
    assert cfg["rooms"][0]["hidden"] is True


def test_add_shortcut():
    cfg = {}
    add_shortcut(cfg, "Home", "mdi:home", "overview")
    assert cfg["sidebar"][0]["name"] == "Home"


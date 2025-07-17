import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Provide dummy Home Assistant modules for import
dummy = types.ModuleType("dummy")
sys.modules.setdefault("homeassistant", dummy)
core_mod = types.ModuleType("core")
core_mod.HomeAssistant = object
sys.modules.setdefault("homeassistant.core", core_mod)
helpers_mod = types.ModuleType("helpers")
helpers_mod.area_registry = types.ModuleType("area_registry")
helpers_mod.device_registry = types.ModuleType("device_registry")
helpers_mod.entity_registry = types.ModuleType("entity_registry")
sys.modules.setdefault("homeassistant.helpers", helpers_mod)
sys.modules.setdefault("homeassistant.helpers.area_registry", helpers_mod.area_registry)
sys.modules.setdefault("homeassistant.helpers.device_registry", helpers_mod.device_registry)
sys.modules.setdefault("homeassistant.helpers.entity_registry", helpers_mod.entity_registry)
sys.modules.setdefault("homeassistant.config_entries", types.ModuleType("config_entries"))
sys.modules["homeassistant.config_entries"].ConfigEntry = object

from custom_components.smart_dashboard.dashboard import discover_devices

class FakeResp:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data


def test_unknown_types_use_entity(monkeypatch):
    states = [
        {"entity_id": "switch.a"},
        {"entity_id": "cover.b"},
    ]

    def fake_get(url, headers=None, timeout=10):
        if url.endswith('/api/states'):
            return FakeResp(states)
        elif url.endswith('/api/areas'):
            return FakeResp([])
        elif url.endswith('/api/devices'):
            return FakeResp([])
        elif url.endswith('/api/entities'):
            return FakeResp([])
        raise AssertionError('unexpected url ' + url)

    monkeypatch.setattr('custom_components.smart_dashboard.dashboard.requests.get', fake_get)
    rooms = discover_devices('http://localhost', 'abc', 'en')
    cards = rooms[0]['cards']
    assert [card['type'] for card in cards] == ['entity', 'entity']

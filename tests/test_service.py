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

from custom_components import smart_dashboard as sd
import asyncio

class DummyServices:
    def __init__(self):
        self._registry = {}
    def has_service(self, domain, service):
        return (domain, service) in self._registry
    def async_register(self, domain, service, func):
        self._registry[(domain, service)] = func
    def async_remove(self, domain, service):
        self._registry.pop((domain, service), None)

class DummyHass:
    def __init__(self):
        self.services = DummyServices()
        self.data = {}

def test_generate_service(monkeypatch):
    hass = DummyHass()
    entry = types.SimpleNamespace(entry_id="1")
    called = {"count": 0}

    async def fake_gen(h):
        called["count"] += 1

    monkeypatch.setattr(sd, "_generate_dashboard_files", fake_gen)

    asyncio.run(sd.async_setup_entry(hass, entry))
    assert hass.services.has_service(sd.DOMAIN, "generate")
    handler = hass.services._registry[(sd.DOMAIN, "generate")]
    asyncio.run(handler(None))
    assert called["count"] == 2

    asyncio.run(sd.async_unload_entry(hass, entry))
    assert not hass.services.has_service(sd.DOMAIN, "generate")

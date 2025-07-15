import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.smart_dashboard.dashboard import filter_existing_entities

class FakeResp:
    def raise_for_status(self):
        pass
    def json(self):
        return [{"entity_id": "light.x"}]

def test_filter_entities(monkeypatch):
    cfg = {"rooms": [{"name": "Room", "cards": [
        {"type": "light", "entity": "light.x"},
        {"type": "light", "entity": "light.y"}
    ]}]}

    def fake_get(url, headers=None, timeout=10):
        assert url.endswith("/api/states")
        return FakeResp()

    monkeypatch.setenv("HASS_TOKEN", "abc")
    monkeypatch.setenv("HASS_URL", "http://localhost")
    monkeypatch.setattr("custom_components.smart_dashboard.dashboard.requests.get", fake_get)

    filter_existing_entities(cfg)
    cards = cfg["rooms"][0]["cards"]
    assert len(cards) == 1
    assert cards[0]["entity"] == "light.x"

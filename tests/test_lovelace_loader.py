import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.smart_dashboard.plugins.lovelace_cards_loader import process_config


def test_loader(monkeypatch):
    data = {"views": [{"title": "API View", "cards": [{"type": "light"}]}]}

    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return data

    def fake_get(url, headers=None, timeout=10):
        assert url.endswith("/api/lovelace")
        return FakeResp()

    monkeypatch.setattr(
        "custom_components.smart_dashboard.plugins.lovelace_cards_loader.requests.get",
        fake_get,
    )
    monkeypatch.setenv("HASS_TOKEN", "abc")
    monkeypatch.setenv("HASS_URL", "http://localhost")
    cfg = {"load_lovelace_cards": True}
    process_config(cfg)
    assert cfg["rooms"][0]["name"] == "API View"
    assert cfg["rooms"][0]["cards"][0]["type"] == "light"

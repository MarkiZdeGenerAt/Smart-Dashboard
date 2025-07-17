import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.smart_dashboard.dashboard import apply_conditions


def _base_config():
    return {
        "rooms": [
            {"name": "Visible", "cards": []},
            {"name": "Hidden", "cards": [], "conditions": ["user == 'admin'"]},
        ],
        "sidebar": [
            {"name": "Home", "view": "overview"},
            {"name": "Admin", "view": "admin", "condition": "user == 'admin'"},
        ],
    }


def test_conditions_filtered(monkeypatch):
    cfg = _base_config()
    monkeypatch.setenv("DASHBOARD_USER", "guest")
    apply_conditions(cfg)
    assert [r["name"] for r in cfg["rooms"]] == ["Visible"]
    assert [s["name"] for s in cfg["sidebar"]] == ["Home"]


def test_conditions_pass(monkeypatch):
    cfg = _base_config()
    monkeypatch.setenv("DASHBOARD_USER", "admin")
    apply_conditions(cfg)
    assert {r["name"] for r in cfg["rooms"]} == {"Visible", "Hidden"}
    assert {s["name"] for s in cfg["sidebar"]} == {"Home", "Admin"}

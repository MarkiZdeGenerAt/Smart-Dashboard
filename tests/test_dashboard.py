import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.smart_dashboard.dashboard import build_dashboard


def test_overview_generation():
    cfg = {
        "rooms": [
            {"name": "Living Room", "cards": [{"type": "light", "entity": "light.l1"}]},
            {"name": "Kitchen", "cards": [{"type": "light", "entity": "light.k1"}]},
        ]
    }
    dash = build_dashboard(cfg, "en")
    assert dash["views"][0]["title"] == "Overview"
    assert dash["views"][1]["title"] == "Devices"
    grid = dash["views"][0]["cards"][0]
    assert grid["type"] == "grid"
    first = grid["cards"][0]
    assert first["tap_action"]["navigation_path"] == "/lovelace/living-room"
    assert first["type"] == "custom:button-card"
    # Device tiles use templates inside room and device views
    device_tile = dash["views"][1]["cards"][0]["cards"][0]
    assert device_tile["template"] == "light_tile"
    assert dash["views"][2]["path"] == "living-room"
    assert dash["views"][3]["path"] == "kitchen"
    assert "light_tile" in dash.get("button_card_templates", {})


def test_resources_included():
    cfg = {
        "resources": [{"url": "/local/test.js", "type": "module"}],
        "rooms": [],
    }
    dash = build_dashboard(cfg, "en")
    assert dash["resources"][0]["url"] == "/local/test.js"

def test_dwains_plugin_resources():
    from custom_components.smart_dashboard.plugins.dwains_style import process_config
    cfg = {"rooms": [{"name": "Room"}]}
    process_config(cfg)
    assert any(r.get("url") == "/local/dwains_style.js" for r in cfg.get("resources", []))


def test_empty_room_placeholder():
    cfg = {"rooms": [{"name": "Empty", "cards": []}]}
    dash = build_dashboard(cfg, "en")
    room_view = dash["views"][1]
    card = room_view["cards"][0]
    assert card["icon"] == "mdi:help-circle-outline"
    assert card["name"] == "No entities"

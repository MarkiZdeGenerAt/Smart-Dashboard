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
    stack = grid["cards"][0]
    assert stack["type"] == "vertical-stack"
    btn = stack["cards"][0]
    assert btn["tap_action"]["navigation_path"] == "/lovelace/living-room"
    assert btn["type"] == "custom:button-card"
    # Next card shows device tiles
    grid_inside = stack["cards"][1]
    assert grid_inside["type"] == "grid"
    # Devices view is a grid of stacks
    device_grid = dash["views"][1]["cards"][0]
    assert device_grid["type"] == "grid"
    device_tile = device_grid["cards"][0]["cards"][0]
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
    assert any(r.get("url") == "/hacsfiles/button-card/button-card.js" for r in dash["resources"])


def test_button_card_resource_added():
    dash = build_dashboard({"rooms": []}, "en")
    assert any(r.get("url") == "/hacsfiles/button-card/button-card.js" for r in dash.get("resources", []))

def test_dwains_plugin_resources():
    from custom_components.smart_dashboard.plugins.dwains_style import process_config
    cfg = {"rooms": [{"name": "Room"}]}
    process_config(cfg)
    assert any(r.get("url") == "/local/dwains_style.js" for r in cfg.get("resources", []))


def test_empty_room_placeholder():
    cfg = {"rooms": [{"name": "Empty", "cards": []}]}
    dash = build_dashboard(cfg, "en")
    room_view = dash["views"][1]
    card = room_view["cards"][0]["cards"][0]
    assert card["icon"] == "mdi:help-circle-outline"
    assert card["name"] == "No entities"


def test_overview_limit_global():
    cfg = {
        "overview_limit": 1,
        "rooms": [
            {
                "name": "Room",
                "cards": [
                    {"type": "light", "entity": "light.a"},
                    {"type": "light", "entity": "light.b"},
                ],
            }
        ],
    }
    dash = build_dashboard(cfg, "en")
    inner = dash["views"][0]["cards"][0]["cards"][0]["cards"][1]
    assert len(inner["cards"]) == 1


def test_overview_limit_room_override():
    cfg = {
        "overview_limit": 1,
        "rooms": [
            {
                "name": "Room",
                "overview_limit": 2,
                "cards": [
                    {"type": "light", "entity": "light.a"},
                    {"type": "light", "entity": "light.b"},
                    {"type": "light", "entity": "light.c"},
                ],
            }
        ],
    }
    dash = build_dashboard(cfg, "en")
    inner = dash["views"][0]["cards"][0]["cards"][0]["cards"][1]
    assert len(inner["cards"]) == 2


def test_fallback_view_when_empty():
    cfg = {"rooms": []}
    dash = build_dashboard(cfg, "en")
    assert dash["views"][0]["title"] == "Smart Dashboard"
    card = dash["views"][0]["cards"][0]
    assert card["type"] == "markdown"
    assert card["content"] == "No devices found."

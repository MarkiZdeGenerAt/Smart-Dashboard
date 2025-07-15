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
    assert dash["views"][0]["cards"][0]["tap_action"]["navigation_path"] == "/lovelace/living-room"
    assert dash["views"][1]["path"] == "living-room"
    assert dash["views"][2]["path"] == "kitchen"

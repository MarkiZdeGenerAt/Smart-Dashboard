import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.smart_dashboard.dashboard import deduplicate_cards


def test_remove_duplicate_cards():
    cfg = {"rooms": [{"name": "Room", "cards": [
        {"type": "light", "entity": "light.l1"},
        {"type": "light", "entity": "light.l1"},
        {"type": "light", "entity": "light.l2"},
    ]}]}
    deduplicate_cards(cfg)
    cards = cfg["rooms"][0]["cards"]
    assert len(cards) == 2
    assert {c["entity"] for c in cards} == {"light.l1", "light.l2"}

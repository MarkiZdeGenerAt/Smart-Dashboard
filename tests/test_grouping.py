import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.smart_dashboard.dashboard import _group_cards_by_type


def test_grouping():
    cards = [
        {"type": "light", "entity": "light.l1"},
        {"type": "thermostat", "entity": "climate.c1"},
        {"type": "media-control", "entity": "media_player.m1"},
        {"type": "sensor", "entity": "sensor.temp"},
    ]
    grouped = _group_cards_by_type(cards)
    assert grouped[0]["type"] == "vertical-stack"
    assert len(grouped[0]["cards"]) == 1
    assert grouped[1]["type"] == "vertical-stack"
    assert len(grouped[1]["cards"]) == 1
    assert grouped[2]["type"] == "vertical-stack"
    assert len(grouped[2]["cards"]) == 1
    assert grouped[3]["type"] == "sensor"

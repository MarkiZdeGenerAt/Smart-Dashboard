import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from custom_components.smart_dashboard.dashboard import discover_devices

class FakeResp:
    def __init__(self, data):
        self._data = data
    def raise_for_status(self):
        pass
    def json(self):
        return self._data


def test_discover_devices_deduplicates(monkeypatch):
    states = [
        {"entity_id": "light.a"},
        {"entity_id": "light.a"},  # duplicate
        {"entity_id": "light.b"},
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
    entities = set()
    for card in cards:
        if 'cards' in card:
            for c in card['cards']:
                entities.add(c['entity'])
        else:
            entities.add(card['entity'])
    assert entities == {'light.a', 'light.b'}

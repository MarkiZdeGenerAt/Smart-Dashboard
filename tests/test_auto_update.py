import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import auto_update


class FakeResp:
    def __init__(self, data=None):
        self._data = data or {}

    def raise_for_status(self):
        pass

    def json(self):
        return self._data

    @property
    def content(self):
        return b""


def test_no_update(monkeypatch, tmp_path):
    comp_dir = tmp_path / "custom_components" / "smart_dashboard"
    comp_dir.mkdir(parents=True)
    (comp_dir / "manifest.json").write_text(json.dumps({"version": "0.1.0"}))

    def fake_get(url, timeout=10):
        assert "manifest.json" in url
        return FakeResp({"version": "0.1.0"})

    monkeypatch.setattr(auto_update.requests, "get", fake_get)
    updated = auto_update.auto_update(tmp_path)
    assert updated is False


def test_update(monkeypatch, tmp_path):
    comp_dir = tmp_path / "custom_components" / "smart_dashboard"
    comp_dir.mkdir(parents=True)
    (comp_dir / "manifest.json").write_text(json.dumps({"version": "0.1.0"}))

    def fake_get(url, timeout=10):
        if "manifest.json" in url:
            return FakeResp({"version": "0.2.0"})
        return FakeResp()

    monkeypatch.setattr(auto_update.requests, "get", fake_get)
    monkeypatch.setattr(auto_update, "_download_and_extract", lambda x: Path("src"))
    called = {}

    def fake_install(src, target):
        called["ok"] = True

    monkeypatch.setattr(auto_update, "_install_from_source", fake_install)
    updated = auto_update.auto_update(tmp_path)
    assert updated is True
    assert called.get("ok")

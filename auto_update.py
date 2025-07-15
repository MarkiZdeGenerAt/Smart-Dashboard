#!/usr/bin/env python3
"""Automatic update helper for the Smart Dashboard integration."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Tuple

import requests

REPO_URL = "https://github.com/user/Smart-Dashboard"
ARCHIVE_URL = f"{REPO_URL}/archive/refs/heads/main.tar.gz"
MANIFEST_URL = (
    f"{REPO_URL}/raw/main/custom_components/smart_dashboard/manifest.json"
)

DEFAULT_DIR = Path.home() / ".homeassistant"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("auto_update")


def _parse_version(ver: str) -> Tuple[int, ...]:
    """Convert a version string like '1.2.3' into a tuple of ints."""
    return tuple(int(v) for v in ver.split("."))


def _get_local_version(target_dir: Path) -> str:
    manifest = target_dir / "custom_components" / "smart_dashboard" / "manifest.json"
    if not manifest.exists():
        return "0.0.0"
    return json.loads(manifest.read_text()).get("version", "0.0.0")


def _get_remote_version() -> str:
    resp = requests.get(MANIFEST_URL, timeout=10)
    resp.raise_for_status()
    return resp.json()["version"]


def _download_and_extract(tmp_dir: Path) -> Path:
    archive = tmp_dir / "sd.tar.gz"
    resp = requests.get(ARCHIVE_URL, timeout=20)
    resp.raise_for_status()
    archive.write_bytes(resp.content)
    with tarfile.open(archive) as tar:
        tar.extractall(tmp_dir)
    root = next(tmp_dir.glob("Smart-Dashboard*"))
    return root


def _install_from_source(src_root: Path, target_dir: Path) -> None:
    comp_src = src_root / "custom_components" / "smart_dashboard"
    comp_dst = target_dir / "custom_components" / "smart_dashboard"
    comp_dst.parent.mkdir(parents=True, exist_ok=True)
    if comp_dst.exists():
        shutil.rmtree(comp_dst)
    shutil.copytree(comp_src, comp_dst)

    config_file = target_dir / "smart_dashboard.yaml"
    if not config_file.exists():
        shutil.copy(comp_src / "config" / "example_config.yaml", config_file)
        logger.info("Created default configuration at %s", config_file)

    dashboards_dir = target_dir / "dashboards"
    dashboards_dir.mkdir(exist_ok=True)
    subprocess.check_call([
        sys.executable,
        str(comp_dst / "dashboard.py"),
        str(config_file),
        "--output",
        str(dashboards_dir / "smart_dashboard.yaml"),
    ])
    subprocess.check_call([
        sys.executable,
        str(Path(__file__).with_name("setup_dashboard.py")),
        str(target_dir),
    ])


def auto_update(target_dir: Path = DEFAULT_DIR) -> bool:
    """Check for a new version and update if necessary."""
    local_v = _get_local_version(target_dir)
    try:
        remote_v = _get_remote_version()
    except Exception as exc:  # pragma: no cover - network failures
        logger.error("Failed to fetch remote version: %s", exc)
        return False

    if _parse_version(remote_v) <= _parse_version(local_v):
        logger.info("Smart Dashboard is up to date (%s)", local_v)
        return False

    logger.info("Updating Smart Dashboard from %s to %s", local_v, remote_v)
    with tempfile.TemporaryDirectory() as tmp:
        root = _download_and_extract(Path(tmp))
        _install_from_source(root, target_dir)
    logger.info("Update complete.")
    return True


if __name__ == "__main__":
    dir_arg = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_DIR
    auto_update(dir_arg)

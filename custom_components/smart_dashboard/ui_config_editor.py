#!/usr/bin/env python3
"""Command line editor for Smart Dashboard configuration."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict
import yaml

from .schema import CONFIG_SCHEMA


def load_config(path: Path) -> Dict[str, Any]:
    with path.open() as f:
        data = yaml.safe_load(f) or {}
    return CONFIG_SCHEMA(data)


def save_config(path: Path, data: Dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, sort_keys=False))


def _find_room(config: Dict[str, Any], name: str) -> Dict[str, Any]:
    for room in config.get("rooms", []):
        if room.get("name") == name:
            return room
    raise ValueError(f"Room '{name}' not found")


def move_card(config: Dict[str, Any], room_name: str, from_idx: int, to_idx: int) -> None:
    room = _find_room(config, room_name)
    cards = room.get("cards", [])
    if not (0 <= from_idx < len(cards)):
        raise IndexError("from_idx out of range")
    if not (0 <= to_idx <= len(cards)):
        raise IndexError("to_idx out of range")
    card = cards.pop(from_idx)
    cards.insert(to_idx, card)


def set_room_hidden(config: Dict[str, Any], room_name: str, hidden: bool) -> None:
    room = _find_room(config, room_name)
    room["hidden"] = bool(hidden)


def add_shortcut(config: Dict[str, Any], name: str, icon: str | None, view: str) -> None:
    shortcut = {"name": name, "view": view}
    if icon:
        shortcut["icon"] = icon
    config.setdefault("sidebar", []).append(shortcut)


def main() -> None:
    parser = argparse.ArgumentParser(description="Edit Smart Dashboard config")
    parser.add_argument("config", type=Path, help="Path to smart_dashboard.yaml")
    sub = parser.add_subparsers(dest="cmd", required=True)

    mv = sub.add_parser("move-card", help="Move a card within a room")
    mv.add_argument("room")
    mv.add_argument("from_idx", type=int)
    mv.add_argument("to_idx", type=int)

    hide = sub.add_parser("hide-room", help="Hide a room")
    hide.add_argument("room")

    show = sub.add_parser("show-room", help="Show a room")
    show.add_argument("room")

    sc = sub.add_parser("add-shortcut", help="Add a sidebar shortcut")
    sc.add_argument("name")
    sc.add_argument("view")
    sc.add_argument("--icon")

    args = parser.parse_args()
    cfg = load_config(args.config)

    if args.cmd == "move-card":
        move_card(cfg, args.room, args.from_idx, args.to_idx)
    elif args.cmd == "hide-room":
        set_room_hidden(cfg, args.room, True)
    elif args.cmd == "show-room":
        set_room_hidden(cfg, args.room, False)
    elif args.cmd == "add-shortcut":
        add_shortcut(cfg, args.name, args.icon, args.view)

    save_config(args.config, cfg)


if __name__ == "__main__":
    main()

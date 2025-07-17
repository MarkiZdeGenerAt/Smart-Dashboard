from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger(__name__)

_TRANSLATIONS: Dict[str, Dict[str, str]] = {}


async def load_translations(lang: str) -> Dict[str, str]:
    """Return translation dictionary for *lang* using a background thread."""
    if lang not in _TRANSLATIONS:
        trans_path = Path(__file__).parent / "translations" / f"{lang}.json"
        if not trans_path.exists():
            _TRANSLATIONS[lang] = {}
        else:
            def _read() -> Dict[str, str]:
                with trans_path.open() as f:
                    return json.load(f)
            try:
                _TRANSLATIONS[lang] = await asyncio.to_thread(_read)
            except Exception:
                _TRANSLATIONS[lang] = {}
    return _TRANSLATIONS.get(lang, {})


async def t(key: str, lang: str, default: str) -> str:
    """Return translated string for ``key`` or ``default`` if missing."""
    translations = await load_translations(lang)
    return translations.get(key, default)

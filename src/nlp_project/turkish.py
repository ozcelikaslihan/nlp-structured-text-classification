"""Turkish-aware normalization used only for evaluation matching."""

from __future__ import annotations

import re
import unicodedata


def turkish_lower(text: str) -> str:
    """Lowercase Turkish dotted/dotless I correctly before str.lower()."""

    return text.replace("İ", "i").replace("I", "ı").lower()


def normalize_entity(text: str) -> str:
    """NFC-normalize, Turkish-lowercase, trim, and collapse whitespace."""

    normalized = unicodedata.normalize("NFC", text)
    return re.sub(r"\s+", " ", turkish_lower(normalized)).strip()

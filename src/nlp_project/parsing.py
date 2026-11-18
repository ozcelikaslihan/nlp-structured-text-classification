"""Raw parsing, conservative cleaning, and schema validation."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from pydantic import ValidationError

from .schema import ModelOutput

_FENCE_RE = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.IGNORECASE | re.DOTALL)


@dataclass(frozen=True)
class ParseResult:
    raw_success: bool
    clean_success: bool
    parsed: Any | None
    cleaned_text: str | None
    error: str | None


def _first_balanced_json_object(text: str) -> str | None:
    """Return the first balanced {...} region, respecting strings and escapes."""

    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return None


def clean_json_text(raw: str) -> str:
    """Remove common wrappers without silently repairing invalid JSON syntax."""

    candidate = raw.strip().lstrip("\ufeff")
    fenced = _FENCE_RE.match(candidate)
    if fenced:
        candidate = fenced.group(1).strip()
    try:
        json.loads(candidate)
        return candidate
    except (json.JSONDecodeError, TypeError):
        extracted = _first_balanced_json_object(candidate)
        return extracted if extracted is not None else candidate


def parse_raw_and_cleaned(raw: str) -> ParseResult:
    """Measure raw json.loads first, then try the documented cleaning path."""

    try:
        parsed = json.loads(raw)
        return ParseResult(True, True, parsed, raw, None)
    except (json.JSONDecodeError, TypeError) as raw_error:
        cleaned = clean_json_text(raw)
        try:
            parsed = json.loads(cleaned)
            return ParseResult(False, True, parsed, cleaned, None)
        except (json.JSONDecodeError, TypeError) as clean_error:
            return ParseResult(
                False,
                False,
                None,
                cleaned,
                f"raw={raw_error}; cleaned={clean_error}",
            )


def validate_schema(value: Any) -> tuple[bool, ModelOutput | None, str | None]:
    """Validate required fields, types, enums, and forbidden extra fields."""

    try:
        validated = ModelOutput.model_validate(value)
        return True, validated, None
    except ValidationError as error:
        return False, None, str(error)


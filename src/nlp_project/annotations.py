"""Fail-fast validation for the manually produced entity gold standard."""

from __future__ import annotations

import json
from pathlib import Path

from .schema import CATEGORIES, ENTITY_TYPES

DEFAULT_PATH = Path("outputs/reviewed_annotations_20261119.jsonl")


def load_and_validate(
    path: Path = DEFAULT_PATH, minimum: int = 100
) -> list[dict[str, object]]:
    if not path.exists():
        raise ValueError(f"Missing annotation file: {path}")
    records: list[dict[str, object]] = []
    seen_ids: set[str] = set()
    errors: list[str] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"line {line_number}: invalid JSON: {error}")
            continue
        sample_id = record.get("id")
        if not isinstance(sample_id, str) or not sample_id:
            errors.append(f"line {line_number}: missing string id")
        elif sample_id in seen_ids:
            errors.append(f"line {line_number}: duplicate id {sample_id}")
        seen_ids.add(sample_id)
        if record.get("annotation_complete") is not True:
            errors.append(f"line {line_number}: annotation_complete must be true")
        if record.get("gold_category") not in CATEGORIES:
            errors.append(f"line {line_number}: invalid gold_category")
        if not isinstance(record.get("text"), str) or not record["text"].strip():
            errors.append(f"line {line_number}: empty text")
        entities = record.get("gold_entities")
        if not isinstance(entities, list):
            errors.append(f"line {line_number}: gold_entities must be a list")
        else:
            for entity_index, entity in enumerate(entities):
                valid_keys = isinstance(entity, dict) and set(entity) == {"text", "type"}
                if not valid_keys:
                    errors.append(
                        f"line {line_number}, entity {entity_index}: keys must be text,type"
                    )
                    continue
                if not isinstance(entity["text"], str) or not entity["text"].strip():
                    errors.append(f"line {line_number}, entity {entity_index}: invalid text")
                elif entity["text"] not in record.get("text", ""):
                    errors.append(
                        f"line {line_number}, entity {entity_index}: not an exact source span"
                    )
                if entity["type"] not in ENTITY_TYPES:
                    errors.append(f"line {line_number}, entity {entity_index}: invalid type")
        records.append(record)
    if len(records) < minimum:
        errors.append(f"need at least {minimum} records, found {len(records)}")
    if errors:
        preview = "\n".join(errors[:30])
        suffix = f"\n... and {len(errors) - 30} more" if len(errors) > 30 else ""
        raise ValueError(preview + suffix)
    return records


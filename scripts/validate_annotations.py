"""Fail-fast checks for the manually produced entity gold standard."""

from __future__ import annotations

from collections import Counter

from nlp_project.annotations import load_and_validate


def main() -> None:
    try:
        records = load_and_validate()
    except ValueError as error:
        raise SystemExit(f"Annotation validation failed:\n{error}") from error
    categories = Counter(record["gold_category"] for record in records)
    entities = Counter(entity["type"] for record in records for entity in record["gold_entities"])
    print(f"Valid annotations: {len(records)}")
    print(f"Categories: {dict(categories)}")
    print(f"Entities: {dict(entities)}")


if __name__ == "__main__":
    main()

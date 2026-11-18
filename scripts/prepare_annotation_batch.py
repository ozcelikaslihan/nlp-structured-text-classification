"""Create a deterministic, stratified 105-item manual annotation batch."""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

from nlp_project.schema import CATEGORIES
from nlp_project.turkish import turkish_lower

SOURCE = Path("data/raw/TTC4900.csv")
DESTINATION = Path("data/annotations/eval_gold.jsonl")
DEV_DESTINATION = Path("data/dev/dev_classification.jsonl")
SAMPLES_PER_CATEGORY = 15
DEV_SAMPLES_PER_CATEGORY = 5
SEED = 20261109
MIN_TEXT_LENGTH = 300
MAX_TEXT_LENGTH = 2500


def canonical_category(value: str) -> str | None:
    lowered = turkish_lower(unicodedata.normalize("NFC", value)).strip()
    lowered = "".join(
        char for char in unicodedata.normalize("NFKD", lowered) if not unicodedata.combining(char)
    )
    lowered = re.sub(r"[^a-z]", "", lowered)
    aliases = {"dunya": "dunya", "ekonomi": "ekonomi", "kultur": "kultur",
               "saglik": "saglik", "siyaset": "siyaset", "spor": "spor",
               "teknoloji": "teknoloji"}
    return aliases.get(lowered)


def read_rows() -> list[list[str]]:
    for encoding in ("utf-8-sig", "utf-8", "cp1254", "latin-1"):
        try:
            sample = SOURCE.read_text(encoding=encoding)[:16384]
            break
        except UnicodeDecodeError:
            continue
    else:
        raise RuntimeError("Dataset encoding could not be detected.")
    dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    with SOURCE.open(encoding=encoding, newline="") as handle:
        return list(csv.reader(handle, dialect))


def extract_examples(rows: list[list[str]]) -> dict[str, list[tuple[int, str]]]:
    """Detect the category cell and treat the longest other cell as the text."""

    groups: dict[str, list[tuple[int, str]]] = defaultdict(list)
    for row_number, row in enumerate(rows, start=1):
        category_cells = [(index, canonical_category(cell)) for index, cell in enumerate(row)]
        category_cells = [(index, value) for index, value in category_cells if value]
        if not category_cells:
            continue
        category_index, category = category_cells[0]
        candidates = [cell.strip() for index, cell in enumerate(row) if index != category_index]
        text = max(candidates, key=len, default="")
        if MIN_TEXT_LENGTH <= len(text) <= MAX_TEXT_LENGTH:
            groups[category].append((row_number, text))
    return groups


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Replace only an untouched draft batch")
    args = parser.parse_args()
    if not SOURCE.exists():
        raise SystemExit("Run scripts/download_dataset.py first.")
    if DESTINATION.exists():
        existing = [json.loads(line) for line in DESTINATION.read_text(encoding="utf-8").splitlines()]
        untouched = all(
            item.get("annotation_complete") is False and item.get("gold_entities") == []
            for item in existing
        )
        if not args.force or not untouched:
            raise SystemExit(f"Refusing to overwrite {DESTINATION}; preserve manual annotations.")
    groups = extract_examples(read_rows())
    missing = [category for category in CATEGORIES if len(groups[category]) < SAMPLES_PER_CATEGORY]
    if missing:
        raise SystemExit(f"Insufficient samples for categories: {missing}")
    rng = random.Random(SEED)
    selected: list[dict[str, object]] = []
    dev_selected: list[dict[str, object]] = []
    for category in CATEGORIES:
        chosen = rng.sample(groups[category], SAMPLES_PER_CATEGORY + DEV_SAMPLES_PER_CATEGORY)
        for row_number, text in chosen[:SAMPLES_PER_CATEGORY]:
            selected.append(
                {
                    "id": f"ttc4900-row-{row_number}",
                    "text": text,
                    "gold_category": category,
                    "gold_entities": [],
                    "annotation_complete": False,
                }
            )
        for row_number, text in chosen[SAMPLES_PER_CATEGORY:]:
            dev_selected.append(
                {"id": f"ttc4900-row-{row_number}", "text": text, "gold_category": category}
            )
    rng.shuffle(selected)
    rng.shuffle(dev_selected)
    DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    with DESTINATION.open("w", encoding="utf-8", newline="\n") as handle:
        for record in selected:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    DEV_DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    with DEV_DESTINATION.open("w", encoding="utf-8", newline="\n") as handle:
        for record in dev_selected:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"Created {len(selected)} records at {DESTINATION}")
    print(f"Created {len(dev_selected)} disjoint development records at {DEV_DESTINATION}")
    print(f"Selection length range: {MIN_TEXT_LENGTH}-{MAX_TEXT_LENGTH} characters")
    print("Manually fill gold_entities and set annotation_complete=true for every record.")


if __name__ == "__main__":
    main()


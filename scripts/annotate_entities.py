"""Interactive, human-only entity annotation with validation and backups."""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from nlp_project.schema import ENTITY_TYPES

PATH = Path("data/annotations/eval_gold.jsonl")
BACKUP_DIR = Path("data/annotations/backups")


def save(records: list[dict[str, object]]) -> None:
    temporary = PATH.with_suffix(".jsonl.tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    temporary.replace(PATH)


def main() -> None:
    if not PATH.exists():
        raise SystemExit("Run scripts/prepare_annotation_batch.py first.")
    records = [json.loads(line) for line in PATH.read_text(encoding="utf-8").splitlines()]
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(PATH, BACKUP_DIR / f"eval_gold-{stamp}.jsonl")
    print("Enter one entity as: exact source text<TAB>TYPE")
    print("Allowed TYPE values: PERSON, ORGANIZATION, LOCATION")
    print("Blank line finishes the current record. :quit saves and exits.")

    for index, record in enumerate(records, start=1):
        if record.get("annotation_complete") is True:
            continue
        print("\n" + "=" * 96)
        print(f"Record {index}/{len(records)} | {record['id']} | category={record['gold_category']}")
        print(record["text"])
        entities: list[dict[str, str]] = []
        while True:
            answer = input("entity<TAB>TYPE (blank=done): ").strip()
            if answer == ":quit":
                save(records)
                print("Progress saved.")
                return
            if not answer:
                record["gold_entities"] = entities
                record["annotation_complete"] = True
                save(records)
                print(f"Saved record with {len(entities)} entities.")
                break
            if "\t" not in answer:
                print("Use a TAB between the exact entity span and its type.")
                continue
            text, entity_type = (part.strip() for part in answer.rsplit("\t", 1))
            if entity_type not in ENTITY_TYPES:
                print(f"Invalid type. Choose one of: {', '.join(ENTITY_TYPES)}")
                continue
            if not text or text not in record["text"]:
                print("That exact span does not occur in the source text.")
                continue
            candidate = {"text": text, "type": entity_type}
            if candidate in entities:
                print("Duplicate ignored.")
                continue
            entities.append(candidate)
            print(f"Added: {candidate}")
    print("All records are annotated. Run scripts/validate_annotations.py next.")


if __name__ == "__main__":
    main()


"""Compare candidate local models on a development set, never the final test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ollama import Client

from nlp_project.ollama_client import generate
from nlp_project.parsing import parse_raw_and_cleaned, validate_schema


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--config", type=Path, default=Path("configs/experiment.json"))
    parser.add_argument("--dev", type=Path, default=Path("data/dev/dev_classification.jsonl"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    config["model"] = args.model
    samples = [json.loads(line) for line in args.dev.read_text(encoding="utf-8").splitlines()]
    if args.limit:
        samples = samples[: args.limit]
    client = Client(host="http://127.0.0.1:11434")
    correct = valid = 0
    for index, sample in enumerate(samples, start=1):
        output = generate(
            client=client, text=sample["text"], setting="schema_constrained", config=config
        )
        parsed = parse_raw_and_cleaned(output.raw_output)
        is_valid, value, _ = validate_schema(parsed.parsed) if parsed.clean_success else (False, None, None)
        prediction = value.category if value else None
        valid += int(is_valid)
        correct += int(prediction == sample["gold_category"])
        print(f"{index:02d}/{len(samples)} gold={sample['gold_category']:<10} pred={str(prediction):<10} valid={is_valid} sec={output.elapsed_seconds:.2f}")
    print(json.dumps({
        "model": args.model,
        "n": len(samples),
        "schema_validity": valid / len(samples),
        "classification_accuracy": correct / len(samples),
    }, indent=2))


if __name__ == "__main__":
    main()

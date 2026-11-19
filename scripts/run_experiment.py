"""Run and resume the paired 105-sample Ollama experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ollama import Client

from nlp_project.evaluation import MetricAccumulator
from nlp_project.ollama_client import generate
from nlp_project.parsing import parse_raw_and_cleaned, validate_schema
from nlp_project.prompts import SYSTEM_PROMPT
from nlp_project.schema import OUTPUT_JSON_SCHEMA
from nlp_project.annotations import DEFAULT_PATH, load_and_validate

SETTINGS = ("prompt_only", "schema_constrained")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def stable_hash(value: object) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def model_metadata(client: Client, model: str) -> dict[str, Any]:
    with urllib.request.urlopen("http://127.0.0.1:11434/api/version", timeout=10) as response:
        version = json.load(response)
    shown = client.show(model)
    details = shown.details.model_dump(mode="json") if shown.details else None
    return {
        "ollama_version": version.get("version"),
        "requested_model": model,
        "model_details": details,
        "model_modified_at": str(shown.modified_at) if shown.modified_at else None,
    }


def load_existing(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    if not path.exists():
        return {}
    existing: dict[tuple[str, str], dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        existing[(record["sample_id"], record["setting"])] = record
    return existing


def append_record(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
        handle.flush()


def build_summary(
    records: list[dict[str, Any]], samples_by_id: dict[str, dict[str, Any]], rule: str
) -> dict[str, Any]:
    summaries: dict[str, Any] = {}
    for setting in SETTINGS:
        accumulator = MetricAccumulator()
        for record in records:
            if record["setting"] != setting:
                continue
            gold = samples_by_id[record["sample_id"]]
            validated = None
            if record.get("schema_valid"):
                _, validated, _ = validate_schema(record["parsed_output"])
            accumulator.add(
                gold_category=gold["gold_category"],
                gold_entities=gold["gold_entities"],
                raw_success=record["raw_json_success"],
                clean_success=record["cleaned_json_success"],
                validated=validated,
                elapsed_seconds=record["elapsed_seconds"],
                matching_rule=rule,
            )
        summaries[setting] = accumulator.summary()
    return summaries


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/experiment.json"))
    parser.add_argument("--annotations", type=Path, default=DEFAULT_PATH)
    parser.add_argument("--output-dir", type=Path, default=Path("results/main"))
    parser.add_argument("--limit", type=int, help="Smoke-test only; never use for final metrics")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = read_json(args.config)
    all_samples = load_and_validate(args.annotations, minimum=config["minimum_samples"])
    samples = all_samples[: args.limit] if args.limit else all_samples
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output_path = args.output_dir / "generations.jsonl"
    manifest_path = args.output_dir / "manifest.json"
    summary_path = args.output_dir / "summary.json"

    client = Client(host="http://127.0.0.1:11434")
    try:
        metadata = model_metadata(client, config["model"])
    except Exception as error:
        raise SystemExit(f"Cannot reach local Ollama or model is missing: {error}") from error

    method = {"system_prompt": SYSTEM_PROMPT, "json_schema": OUTPUT_JSON_SCHEMA}
    fingerprint = stable_hash(
        {"config": config, "annotation_hash": stable_hash(all_samples), "method": method}
    )
    if manifest_path.exists():
        manifest = read_json(manifest_path)
        if manifest.get("fingerprint") != fingerprint:
            raise SystemExit("Existing output has a different config/dataset. Choose another --output-dir.")
    else:
        manifest = {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "fingerprint": fingerprint,
            "config": config,
            "annotation_sha256": stable_hash(all_samples),
            "method_sha256": stable_hash(method),
            "system_prompt": SYSTEM_PROMPT,
            "json_schema": OUTPUT_JSON_SCHEMA,
            "n_full_samples": len(all_samples),
            "python_version": sys.version,
            "platform": platform.platform(),
            **metadata,
        }
        manifest_path.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    existing = load_existing(output_path)
    total_calls = len(samples) * len(SETTINGS)
    completed = sum((sample["id"], setting) in existing for sample in samples for setting in SETTINGS)
    print(f"Resuming at {completed}/{total_calls} calls")

    for sample in samples:
        for setting in SETTINGS:
            key = (sample["id"], setting)
            if key in existing:
                continue
            print(f"[{completed + 1}/{total_calls}] {sample['id']} | {setting}", flush=True)
            try:
                generation = generate(client=client, text=sample["text"], setting=setting, config=config)
                parsed = parse_raw_and_cleaned(generation.raw_output)
                schema_valid, _, schema_error = validate_schema(parsed.parsed) if parsed.clean_success else (False, None, None)
                record = {
                    "sample_id": sample["id"],
                    "setting": setting,
                    "raw_output": generation.raw_output,
                    "raw_json_success": parsed.raw_success,
                    "cleaned_json_success": parsed.clean_success,
                    "cleaned_text": parsed.cleaned_text,
                    "parsed_output": parsed.parsed,
                    "schema_valid": schema_valid,
                    "parse_error": parsed.error,
                    "schema_error": schema_error,
                    "generation_error": None,
                    "elapsed_seconds": generation.elapsed_seconds,
                    "prompt_eval_count": generation.prompt_eval_count,
                    "eval_count": generation.eval_count,
                    "prompt_eval_duration_ns": generation.prompt_eval_duration,
                    "eval_duration_ns": generation.eval_duration,
                    "done_reason": generation.done_reason,
                }
            except Exception as error:
                record = {
                    "sample_id": sample["id"], "setting": setting, "raw_output": "",
                    "raw_json_success": False, "cleaned_json_success": False,
                    "cleaned_text": None, "parsed_output": None, "schema_valid": False,
                    "parse_error": None, "schema_error": None,
                    "generation_error": f"{type(error).__name__}: {error}",
                    "elapsed_seconds": 0.0, "prompt_eval_count": None, "eval_count": None,
                    "prompt_eval_duration_ns": None, "eval_duration_ns": None, "done_reason": None,
                }
            append_record(output_path, record)
            existing[key] = record
            completed += 1

    target_records = [
        existing[(sample["id"], setting)] for sample in samples for setting in SETTINGS
    ]
    samples_by_id = {sample["id"]: sample for sample in samples}
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "is_final_run": args.limit is None,
        "matching_rule": config["entity_matching"],
        "settings": build_summary(target_records, samples_by_id, config["entity_matching"]),
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


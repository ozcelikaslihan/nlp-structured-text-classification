"""Uncut video demo: paired settings, two temperatures, and five new texts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ollama import Client

from nlp_project.ollama_client import generate
from nlp_project.parsing import parse_raw_and_cleaned, validate_schema

NEW_SAMPLES = [
    "Türkiye Cumhuriyet Merkez Bankası Ankara'da yaptığı açıklamada politika faizini sabit tuttu.",
    "Fenerbahçe teknik direktörü José Mourinho, İstanbul'daki maç öncesinde basın toplantısı düzenledi.",
    "Sağlık Bakanlığı, grip vakalarına karşı vatandaşlara aşı çağrısı yaptı.",
    "Apple, yeni işlemcisini Kaliforniya'daki etkinlikte tanıttı ve cihazların gelecek ay satılacağını duyurdu.",
    # Deliberately ambiguous: politics and economy are both plausible.
    "Mecliste kabul edilen bütçe düzenlemesi vergi gelirlerini artırmayı hedefliyor.",
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=Path, default=Path("configs/experiment.json"))
    parser.add_argument("--dataset-samples", type=Path, default=Path("outputs/reviewed_annotations_20261119.jsonl"))
    parser.add_argument("--log", type=Path, default=Path("outputs/live_rehearsal.jsonl"))
    args = parser.parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    dataset_records = [json.loads(line) for line in args.dataset_samples.read_text(encoding="utf-8").splitlines()]
    # The same two fixed dataset samples are used in every displayed condition.
    display_samples = [(f"DATASET: {item['id']}", item["text"]) for item in dataset_records[:2]]
    display_samples += [(f"NEW-{index}", text) for index, text in enumerate(NEW_SAMPLES, start=1)]
    client = Client(host="http://127.0.0.1:11434")

    for temperature in (0.0, 1.0):
        local_config = {**config, "temperature": temperature}
        for label, text in display_samples:
            print("\n" + "=" * 88)
            print(f"{label} | temperature={temperature}")
            print(text)
            for setting in ("prompt_only", "schema_constrained"):
                try:
                    output = generate(client=client, text=text, setting=setting, config=local_config)
                    parsed = parse_raw_and_cleaned(output.raw_output)
                    valid, value, error = validate_schema(parsed.parsed) if parsed.clean_success else (False, None, parsed.error)
                    print(f"\n[{setting}] raw={parsed.raw_success}, cleaned={parsed.clean_success}, schema={valid}")
                    print(output.raw_output)
                    args.log.parent.mkdir(parents=True, exist_ok=True)
                    with args.log.open('a', encoding='utf-8') as handle:
                        handle.write(json.dumps({'label': label, 'text': text, 'temperature': temperature,
                            'setting': setting, 'raw_output': output.raw_output,
                            'raw_success': parsed.raw_success, 'clean_success': parsed.clean_success,
                            'schema_valid': valid, 'seconds': output.elapsed_seconds}, ensure_ascii=False)+'\n')
                    if error:
                        print(f"ERROR: {error}")
                    if value:
                        print("PARSED:", json.dumps(value.model_dump(), ensure_ascii=False))
                except Exception as error:
                    print(f"\n[{setting}] CALL FAILED: {type(error).__name__}: {error}")


if __name__ == "__main__":
    main()


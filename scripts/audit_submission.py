"""Check the frozen gold and independently rebuild metrics from raw saved text.

No model call is made and no saved evaluation files are modified.
Run from the repository root after installing the project.
"""
import hashlib
import json
from pathlib import Path

from nlp_project.annotations import load_and_validate
from nlp_project.evaluation import MetricAccumulator
from nlp_project.parsing import parse_raw_and_cleaned, validate_schema


def stable_hash(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def main():
    samples = load_and_validate()
    gold = {sample['id']: sample for sample in samples}
    assert len(samples) == 105
    print(f'Gold validated: {len(samples)} articles, {sum(len(s["gold_entities"]) for s in samples)} entities')
    for folder in ('main_reviewed', 'temperature1_reviewed'):
        root = Path('outputs') / folder
        manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
        saved = json.loads((root / 'summary.json').read_text(encoding='utf-8'))['settings']
        assert stable_hash(samples) == manifest['annotation_sha256'], 'Gold changed since inference'
        records = [json.loads(line) for line in (root / 'generations.jsonl').read_text(encoding='utf-8').splitlines()]
        expected = {(sample_id, setting) for sample_id in gold for setting in saved}
        actual = {(r['sample_id'], r['setting']) for r in records}
        assert len(records) == len(actual) == 210 and actual == expected, 'Missing/duplicate calls'
        for setting, summary in saved.items():
            accumulator = MetricAccumulator()
            for r in records:
                if r['setting'] != setting:
                    continue
                parsed = parse_raw_and_cleaned(r['raw_output'])
                valid, value, _ = validate_schema(parsed.parsed) if parsed.clean_success else (False, None, None)
                assert (parsed.raw_success, parsed.clean_success, valid) == (
                    r['raw_json_success'], r['cleaned_json_success'], r['schema_valid'])
                sample = gold[r['sample_id']]
                accumulator.add(gold_category=sample['gold_category'], gold_entities=sample['gold_entities'],
                    raw_success=parsed.raw_success, clean_success=parsed.clean_success, validated=value,
                    elapsed_seconds=r['elapsed_seconds'], matching_rule=manifest['config']['entity_matching'])
            rebuilt = accumulator.summary()
            assert rebuilt == summary, f'Metric mismatch: {folder}/{setting}'
        print(f'{folder}: 210 unique calls, gold hash and all recomputed metrics match')
    print('PASS: saved experiment evidence is internally consistent; video/submission are separate checks.')


if __name__ == '__main__':
    main()

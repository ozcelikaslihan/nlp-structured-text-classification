# NLP Project I: Local structured output evaluation

Python and local Ollama inference classify Turkish news into seven categories
and extract PERSON, ORGANIZATION and LOCATION names. No cloud LLM API is used.

## Current status (19 November 2026)

- 105 manually reviewed articles, 949 gold entity annotations.
- Completed paired runs at temperatures 0 and 1: 420 saved model outputs.
- Three-page English technical report: [PDF](outputs/technical_report.pdf).
- Video recording and upload, public viewing links and submission remain.
- Model eligibility needs clarification: Qwen2.5-3B uses the Qwen Research
  License, not Apache-2.0. Do not describe this as confirmed compliance with a
  strict open-source license requirement.
  [Official license](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct/blob/main/LICENSE)

## Reproduce the saved evaluation

Run from this repository's root. The measured environment was Python 3.13.17,
Ollama 0.40.16, ollama Python package 0.6.1 and Pydantic 2.12.4.
Python >=3.11 is declared supported; other versions were not used for the report.

~~~powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
python scripts/validate_annotations.py
python scripts/audit_submission.py
~~~

The audit recomputes metrics from saved raw model outputs without calling Ollama.
The authoritative frozen gold file is
`outputs/reviewed_annotations_20261119.jsonl`, used by default in validation,
experiments and the live demo. `data/annotations/eval_gold.jsonl` is the old
working annotation file, not the gold used for the report. Do not rerun
annotation preparation over the frozen file.

To generate new predictions, start local Ollama and obtain `qwen2.5:3b`.
Check `ollama show qwen2.5:3b` for Q4_K_M; the measured local ID was
357c53fb659c (3.1B parameters). A tag can change upstream, so compare metadata.
Hardware used: RTX 3050 Laptop, 4 GB VRAM.

~~~powershell
ollama pull qwen2.5:3b
ollama show qwen2.5:3b
python scripts/run_experiment.py --limit 2 --output-dir results/new_smoke
python scripts/run_experiment.py --output-dir results/new_main
python scripts/run_experiment.py --config configs/temperature1.json --output-dir results/new_temperature1
~~~

New runs go to separate directories so the reported evidence remains intact.
Resume with the same command, config and annotations. Main parameters:
temperature=0, seed=42, top_k=40, top_p=0.9, num_ctx=4096, num_predict=512,
keep_alive=10m, stream=false. The secondary config changes only temperature to 1.
Unspecified options use Ollama defaults.

## Data and methodology

TTC-4900 supplies class labels; entity labels were selected manually from scratch
by one annotator using the browser interface. Sampling seed 20261109 selects
15 articles per class (105 evaluation articles) and 5 per class (35 development
articles), restricted to 300–2500 characters. This is a length filter, not a
guarantee that all prompts and responses fit the token budget.

Follow [annotation rules](data/README.md). Entity scoring is typed exact matching
after NFC, whitespace normalization and Turkish-aware casing (İ→i, I→ı before
lowercasing). Invalid schema outputs count as wrong classes and empty entity
predictions. Repeated predicted entities are penalized.

Both conditions have identical messages and generation parameters; only the
schema-constrained condition receives the Ollama `format` key. The report
separates direct raw JSON parsing, parsing after cleaning, schema validity,
classification accuracy and micro entity F1. Cleaning does not repair truncated
JSON. Development choices and limitations are in [the decision log](docs/decision_log.md).
One preliminary test article was inspected before freezing the split.

## Reported results

| Temperature | Setting | Raw JSON | Clean JSON | Schema | Accuracy | Entity F1 |
|---|---|---|---|---|---|---|
| 0 | Prompt-only | 98.10% | 98.10% | 92.38% | 49.52% | 30.05% |
| 0 | Schema | 99.05% | 99.05% | 99.05% | 54.29% | 29.63% |
| 1 | Prompt-only | 98.10% | 98.10% | 96.19% | 52.38% | 27.46% |
| 1 | Schema | 99.05% | 99.05% | 99.05% | 55.24% | 27.90% |

Evidence: `outputs/main_reviewed/` and `outputs/temperature1_reviewed/` each
contain a manifest, 210 raw generation records and a summary. Gold labels and
these evidence folders are explicitly included by Git ignore rules.

## Video and report

Use [the video plan](docs/video_plan.md) and
[Turkish preparation notes](outputs/video_hazirlik.md) as cues, not a script.
A1 removes a single return statement from an isolated in-memory copy of the
actual extraction function; the source files and evaluation results are unchanged.

~~~powershell
python scripts/live_demo.py
python scripts/defense_ablation.py
ollama show qwen2.5:3b
~~~

The live demo runs two dataset articles and five new fictional samples in both
settings at both temperatures (28 calls). Record the run without cuts.
For rebuilding the report only, additionally install ReportLab and run
`python scripts/build_report.py`. ReportLab is not needed for model evaluation.

## Remaining submission steps

- Resolve whether the instructor accepts the model's research license.
- Record English video, <=30 minutes: walkthrough; uncut live tests; A1–A4 plus
  B1, C1, D1, E1, F6, G1. Include a demonstrated experiment and explain actual
  outputs. Face visible at the beginning, screen and voice throughout.
- Upload to YouTube as Unlisted; use actual chapter timestamps.
- Share code, annotations, results and report via GitHub or Drive with view access.
- Submit both links and live/defense start times once through the supplied form
  by 22 November 2026, 23:59 Europe/Istanbul.
- Do not change submitted code/report after the deadline; retain video availability.

## Sources and assistance

- [TTC-4900 dataset](https://github.com/savasy/TurkishTextClassification)
- [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [Ollama Python client](https://github.com/ollama/ollama-python)
- [Annotation interface reference](https://github.com/emrehann17/structured-text-project):
  used as a workflow/UI reference, not as this project's gold labels.
- An AI coding assistant helped implement and review code and draft documentation.
  The student manually selected the entity labels and must explain the work
  and results in their own words.


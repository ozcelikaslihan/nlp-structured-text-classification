# Local LLM Structured Output Evaluation (Project I)

This repository evaluates a **fully local Ollama model** on two simultaneous
Turkish NLP tasks:

1. classify TTC-4900 news into `dunya`, `ekonomi`, `kultur`, `saglik`,
   `siyaset`, `spor`, or `teknoloji`;
2. extract `PERSON`, `ORGANIZATION`, and `LOCATION` entities.

The paired experiment compares prompt-only JSON generation with JSON-schema
constrained generation. The prompt, model, sample order, seed, and generation
options are identical; the constrained condition alone receives Ollama's
`format` parameter. No cloud LLM API is used.

> Project status (18 November 2026): Python 3.13.17, dependencies, Ollama
> 0.40.16, `qwen2.5:3b` Q4_K_M, TTC-4900, the disjoint development set, and the
> 105-item annotation batch are ready; all tests pass. **Manual gold entity
> annotation**, final runs, error analysis, the report PDF, and video recording
> still have to be completed.

## Requirements covered by design

- 105 fixed evaluation documents (15 from each of 7 classes), exceeding the
  required 100. Texts are deterministically sampled from the 300–2500 character
  range so the complete input fits the declared local context budget.
- Manually annotated entity gold labels with written rules and fail-fast
  validation.
- Strict JSON schema shared by prompt, Ollama `format`, and Pydantic validation.
- Separate raw `json.loads` rate and post-cleaning parse rate.
- Schema validity, classification accuracy, and typed micro entity P/R/F1.
- Turkish-aware `İ/i` and `I/ı` normalization and a stated exact-match rule.
- Exceptions are saved as failed records so a long run continues; runs resume
  without repeating completed calls.
- Manifest captures exact model details, quantization, Ollama version, Python,
  platform, config, and annotation hash.
- A repeatable live demo uses both settings, temperatures 0 and 1.0, the same
  dataset examples, and five new examples including an ambiguous expected error.

## 1. Install (Windows PowerShell)

Python 3.11 or 3.12 and Ollama are required. From this repository:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
python -m pytest
```

Start Ollama, then download the exact configured model:

```powershell
ollama serve
ollama pull qwen2.5:3b
ollama show qwen2.5:3b
ollama ps
```

The installed tag is suitable for a 4 GB RTX 3050 laptop GPU. `ollama show`
must confirm that its quantization is `Q4_K_M`; the report should state the
actual tag (`qwen2.5:3b`) and quantization as separate reproducibility fields.
Do not replace the real local tag with a longer library alias in the report.

## 2. Prepare the data and gold annotations

```powershell
python scripts/download_dataset.py
python scripts/inspect_dataset.py
python scripts/prepare_annotation_batch.py
```

Manually edit `data/annotations/eval_gold.jsonl`. For every line, fill
`gold_entities` and set `annotation_complete` to `true`. Follow every rule in
[data/README.md](data/README.md). Then run:

```powershell
python scripts/annotate_entities.py
python scripts/validate_annotations.py
```

The annotation tool is human-only: it never calls a model, requires exact source
spans, saves after every record, and creates a local backup when it starts.

The validator checks at least 100 records, allowed labels/types, unique IDs,
exact source spans, JSON syntax, and completion flags. Commit the completed gold
file; it is part of the reproducible evaluation artifact.

## 3. Verify a smoke test, then run the full paired experiment

Keep the final parameters in [configs/experiment.json](configs/experiment.json).
For a code-path smoke test only:

```powershell
python scripts/run_experiment.py --limit 2 --output-dir results/smoke
```

For the final 210-call run:

```powershell
python scripts/run_experiment.py --output-dir results/main
```

The script is resumable. Do not change the config or annotations inside one
output directory. Final metrics are written to `results/main/summary.json`; all
raw outputs and failure details are in `results/main/generations.jsonl`, and
exact reproducibility metadata is in `results/main/manifest.json`.

For fair reporting, parsing/schema failures count as incorrect classifications
and as predicting no entities (therefore all gold entities for that item become
false negatives). This avoids calculating task accuracy only on successfully
parsed outputs.

## 4. Video demo and report

Rehearse, then record this command **without cuts**:

```powershell
python scripts/live_demo.py
```

Use [docs/video_plan.md](docs/video_plan.md) for the required English walkthrough,
live test, ten defense answers, timing, and upload checklist. Use
[docs/report_outline.md](docs/report_outline.md) to write the maximum four-page
technical report from actual saved results.

## Main experimental parameters

The source of truth is `configs/experiment.json`:

- model tag: `qwen2.5:3b`
- quantization: `Q4_K_M` (captured from `ollama show` in the manifest)
- seed: `42`
- temperature: `0.0`
- top-k: `40`
- top-p: `0.9`
- context length: `4096`
- maximum output tokens: `512`
- dataset sampling seed: `20261109`
- entity matching: typed normalized exact match

Any parameter changed before the final run must also be updated in the report
and used in the video. The temperature-1.0 video experiment is a named secondary
experiment, not the main result.

## Submission checklist (deadline: 22 November 2026, 23:59 Europe/Istanbul)

- [ ] At least 100 fully manual, validated entity annotations.
- [ ] Tests pass; smoke run inspected; final paired run has 105 × 2 records.
- [ ] Report is PDF, no more than 4 pages, and contains actual tables/discussion.
- [ ] Exact tag, quantization, Ollama version, seed, context and all generation
      parameters match the manifest, code, report, and recorded video.
- [ ] D1 is answered by showing the real `Q4_K_M` value from `ollama show`.
- [ ] Video is English, ≤30 minutes, screen + voice throughout, face at start.
- [ ] Live test is uncut; both settings, two temperatures, and five new samples
      are visible.
- [ ] YouTube account verified; video uploaded as **Unlisted**, not Private/Public.
- [ ] Real timestamps are in the description and live/defense starts in the form.
- [ ] GitHub repository or Drive folder is viewable by anyone with the link.
- [ ] YouTube link and repository/Drive link submitted once through the form.
- [ ] Code/report are not changed after the deadline; video remains available
      until final grades are announced.

## Sources

- [TTC-4900 repository](https://github.com/savasy/TurkishTextClassification)
- [Ollama structured outputs](https://docs.ollama.com/capabilities/structured-outputs)
- [Official Ollama Python client](https://github.com/ollama/ollama-python)

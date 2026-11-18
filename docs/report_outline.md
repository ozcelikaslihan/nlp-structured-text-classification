# Technical report outline (maximum 4 pages)

## 1. Task, data, and reproducibility

- Task: seven-way TTC-4900 Turkish news classification plus PERSON,
  ORGANIZATION, LOCATION extraction.
- Evaluation split: deterministic stratified sample, 15 per class, 105 total,
  restricted to 300–2500 characters so every full text fits the local inference
  budget; dataset seed 20261109. Explain that entities were manually annotated and
  summarize the rules from `data/README.md`.
- State exact model name/tag, `ollama show` quantization, Ollama version,
  hardware, Python/package versions, seed, temperature, top-k, top-p, context
  length, and max generated tokens. Copy these from the run manifest rather
  than memory.

## 2. Methodology

- Show the output schema and the seven allowed category values.
- Prompt-only: prompt requests JSON; **no `format` argument**.
- Schema-constrained: identical messages and generation options, plus
  `format=OUTPUT_JSON_SCHEMA`.
- Describe direct raw parsing, conservative cleaning, second parse attempt,
  Pydantic schema validation, and graceful failure records.
- Entity rule: typed normalized exact match; NFC, whitespace normalization,
  Turkish-aware case conversion (`İ→i`, `I→ı`, then `lower()`).

## 3. Results

Include one compact table with both settings as rows and these columns:

- raw JSON parse success
- cleaned JSON parse success
- schema validity
- classification accuracy
- entity micro precision, recall, F1
- mean response time (optional but useful)

Add the temperature 0 vs 1.0 live-test result as a small secondary table if it
fits. Never invent numbers; copy from `results/main/summary.json`.

## 4. Discussion, errors, limitations

- Directly answer whether constrained decoding changed semantic accuracy, not
  only format validity. Use observed classification and entity F1 differences.
- Inspect at least 5 classification errors and 5 entity errors. Discuss category
  ambiguity, missed long organizations, hallucinated entities, Turkish suffixes,
  and quantization/model-size limitations only where supported by examples.
- Limitations: only 105 manually annotated items, single dataset/model/seed for
  main comparison, possible annotation subjectivity, exact matching strictness.
- State that the model and inference were fully local through Ollama and no
  cloud LLM API was used.

## References / links

- TTC-4900 source repository
- Ollama structured outputs documentation
- Exact base model/tokenizer page used for the tokenization defense experiment


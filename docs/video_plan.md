# Video plan (English, maximum 30 minutes)

Do not read this verbatim. Use it as a checklist and explain the choices in your
own words.

## 00:00–09:00 — Code walkthrough

1. Brief face-visible introduction, task, local-only constraint, model/hardware.
2. Dataset download and deterministic 105-sample selection.
3. Manual gold entity rules and one annotated example.
4. `schema.py`, `prompts.py`, and the identical-message experimental control.
5. `ollama_client.py`: point out that only schema-constrained mode gets
   `format`; show all generation parameters.
6. `parsing.py`: raw `json.loads`, cleaner, try/except, validation.
7. `evaluation.py`: classification accuracy and micro entity F1.
8. `run_experiment.py`: resumable paired loop and saved manifest/results.

## 09:00–16:00 — Uncut live tests

- Run `python scripts/live_demo.py` without cuts from command to output.
- Show the same fixed examples in prompt-only and constrained settings.
- Show the same examples at temperature 0 and 1.0.
- Show all five new samples; explicitly identify NEW-5 as deliberately
  ambiguous and say whether the expected error happened.
- Comment on format, category, entities, and latency—not only whether it ran.

## 16:00–29:00 — Ten defense answers

Answer all four A questions, then one chosen question from each B–G:

- A1: show `return text[start : index + 1]` in `_first_balanced_json_object`.
  Run `python scripts/defense_ablation.py` to compare the original function with
  an isolated copy in which that one return is removed (`pass` keeps valid syntax).
  Explain that the fixture is synthetic, not a test metric.
- A2: discuss the added category tie-break rules that were rejected after
  development accuracy fell from 60.0% to 57.1%. Explain this decision in your
  own words; do not claim you personally made decisions you did not review.
- A3: use the actually most surprising measured result.
- A4: compare both rows of the final result table.
- B1: contrast an n-gram's local count/probability table with a Transformer's
  context-dependent hidden state and softmax distribution over next-token logits.
- C1 **experiment answer**: use the displayed temperature 0 vs 1.0 results and
  count raw parse/schema/accuracy changes.
- D1: state `Q4_K_M` and show how `ollama show qwen2.5:3b` verifies it.
- E1: explain that a tokenizer trained on a distribution dominated by other
  languages often represents Turkish agglutinative forms with more subword pieces.
- F6: explain development-set prompt selection using accuracy and format
  validity. No combined metric was predeclared in this project. Acknowledge the
  initial exploratory test inspection before the final split was frozen.
- G1: TF-IDF logistic regression may beat a small zero-shot LLM when abundant
  in-domain labeled data and stable lexical cues exist, but it does not perform
  entity extraction without a separate model.

## Before upload

- Replace timestamps with actual starts in the YouTube description so chapters
  work.
- Video is Unlisted, account is verified, face appears at start, voice/screen
  remain recorded, live section is uncut.
- Submit the live-test and defense start times in the form.

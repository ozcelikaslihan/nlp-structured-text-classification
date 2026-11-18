# Data and manual annotation

The source corpus is **TTC-4900**, a seven-class Turkish news classification
dataset. It is downloaded from the public repository by
`scripts/download_dataset.py`; the large raw file is not committed.

## Gold entity annotation rules

Annotate every selected evaluation text manually. Do not use an LLM to create
the gold labels.

- `PERSON`: a specifically named real or fictional person. Include the full
  surface name, but not titles such as *Cumhurbaşkanı* unless the title is part
  of the name.
- `ORGANIZATION`: named companies, institutions, political parties, agencies,
  sports clubs, universities, and similar bodies.
- `LOCATION`: named countries, cities, districts, regions, and geographic
  features.
- Copy the exact contiguous span from the source text, including Turkish
  characters. Do not include a Turkish case suffix after an apostrophe in the
  entity span. If the dataset omits the apostrophe, consistently annotate the
  shortest span that identifies the proper name.
- Annotate each distinct surface mention once per document. Repeated mentions
  of the same surface form are not duplicated in `gold_entities`.
- Nested entities are not used. Choose the longest span that represents the
  intended entity, e.g. `Türkiye Cumhuriyet Merkez Bankası` as one
  `ORGANIZATION`, not an additional `Türkiye` location inside it.
- Common nouns, unnamed roles, dates, money amounts, products, events, and
  nationalities are outside the entity inventory.
- If there is no qualifying entity, use an empty list and still set
  `annotation_complete` to `true`.

Example record:

```json
{"id":"ttc4900-row-123","text":"...","gold_category":"spor","gold_entities":[{"text":"Fenerbahçe","type":"ORGANIZATION"}],"annotation_complete":true}
```

## Matching rule

The reported entity metric uses **typed, normalized exact matching**. Both the
entity text and entity type must match. Text is Unicode NFC-normalized,
whitespace is collapsed, and Turkish-aware lowercasing is applied. Crucially,
the code replaces `İ` with `i` and `I` with `ı` before Python `str.lower()`.
No substring/partial match is used.


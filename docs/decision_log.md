# Experimental decision log

This file records choices made on the development set so the final test set is
not used for tuning.

## Model and hardware

- GPU: NVIDIA GeForce RTX 3050 Laptop GPU, 4 GB VRAM.
- `qwen2.5:3b`: 3.1B parameters, Q4_K_M, 1.9 GB, 32K model context.
- `qwen2.5:latest`: 7.6B parameters, Q4_K_M, 4.7 GB, 32K model context.
- The 7.6B candidate took about 60 seconds for its first development sample on
  this computer and was stopped because it would make the paired 210-call run
  and live video impractical. The 3B model was retained.

## Output schema iteration

On the disjoint 35-document development set:

- Array-of-objects entity schema (`[{text,type}, ...]`): schema validity 34.3%,
  classification accuracy 25.7%. The 3B model frequently repeated objects until
  the output-token limit and produced truncated JSON.
- Typed-list schema (`entities.persons`, `.organizations`, `.locations`): schema
  validity 97.1%, classification accuracy 60.0%. It preserves entity types while
  being much easier for the small model to complete.

## Prompt iteration

Adding explicit foreign-politics and company tie-break rules produced 100%
schema validity but reduced development classification accuracy to 57.1%.
That change was rejected and the previous, better-scoring prompt was restored.

These figures are development results, not the final test results, and must not
be presented as the required two-setting evaluation table.

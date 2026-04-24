# Paper wording (recommended)

## Variant A — only canonical rows

Use this if GPT-5.x remains unresolved.

The canonical real-LLM experiment uses `gpt-4.1-mini` and `gpt-4.1`, each evaluated on the full 25-case suite with three runs per case. Both models achieve 75/75 expected outcomes. This is a ceiling result on a controlled typed-output realization check, rather than evidence that the models have identical general security behavior.

## Variant B — clean GPT-5.x structured rerun

Use this only if GPT-5.x reruns are clean.

We additionally run a structured-output robustness pass on `gpt-5.4` and `gpt-5.4-pro`. These runs preserve raw outputs, parsed objects, validator decisions, and per-trial failure labels. Aggregate pass counts match per-trial recomputation in all rows, eliminating the aggregate-labeling ambiguity observed in earlier exploratory runs.

## Variant C — stress-suite result

Use if the new stress suite is clean.

The stress suite separates model realization from validator correctness. Failures are reported by origin: model sanitization, parse/schema failure, API transport, scoring, or validator disagreement. Across all parsed unsafe typed steps, validator decisions match expected labels, while realization failures occur before the firewall receives the intended boundary object.

# AGENTS

Use this repository as a file-first community intelligence engine.

## Rules

- Do not mutate raw source files.
- All source data must be normalized into `.garden/bronze/events/*.jsonl`.
- Deterministic metrics belong in `.garden/silver/metrics/`.
- LLM-facing context belongs in `.garden/gold/llm_packs/`.
- Human-facing reports belong in `.garden/gold/reports/`.
- Findings must include evidence ids when possible.
- Do not label people with medical or psychiatric terms. Use behavioral risk patterns.
- Removal recommendations must require repeated evidence, confidence, and alternatives.

## Typical workflow

```bash
cg import telegram-export result.json --project .
cg analyze --project . --period last-week
cg skill run all --project . --period last-week
cg report weekly --project . --period last-week
```

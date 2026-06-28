# Community Garden Core

File-first Python library for community intelligence.

It turns raw community messages into:

- **Bronze data**: normalized events.
- **Silver data**: metrics, graphs, findings, role/tribe/risk artifacts.
- **Gold data**: Markdown reports, recommendations, LLM packs, charts.

Telegram is only the first adapter. The core works with a universal `CommunityEvent` model and can later accept Slack, Discord, WhatsApp, Discourse, GitHub Discussions, Reddit, CSV/JSON exports, or custom sources.

## Install

```bash
uv sync
uv run cg --help
```

Or as a package:

```bash
uv pip install -e .
```

## Fast path

```bash
uv run cg init ./demo-garden --community-id demo --name "Demo Community"
uv run cg import telegram-export ./sample_data/telegram_result.json --project ./demo-garden
uv run cg analyze --project ./demo-garden --period 2026-W26
uv run cg report weekly --project ./demo-garden --period 2026-W26
uv run cg llm-pack weekly --project ./demo-garden --period 2026-W26
uv run cg chart radar --project ./demo-garden --period 2026-W26
```

Outputs:

```text
.garden/
  raw/
  bronze/
  silver/
  gold/
  memory/
  skills/
```

## Data layers

### Raw
Original source files, untouched.

### Bronze
Normalized `CommunityEvent` JSONL files.

### Silver
Metrics, graphs, role candidates, tribe candidates, risk findings, admin mirror findings.

### Gold
Human-facing reports, recommendations, LLM packs, charts.

## Current implementation status

This repository is a complete MVP scaffold with working MVP-0 core and functional paths for MVP-1..MVP-4:

- MVP-0: Telegram Desktop export → bronze events → metrics → graph → weekly report.
- MVP-1: skill runner, semantic registry, role/risk/admin/tribe templates.
- MVP-2: week-to-week trend comparison and radar chart data/artifact.
- MVP-3: Telegram bot and Telethon local adapters are included as optional wrappers with graceful dependency checks.
- MVP-4: CLI, MCP wrapper, FastAPI wrapper, scheduler primitives.

The LLM layer is provider-agnostic by design. The core writes compact `llm_pack.md` files for Claude Code, OpenAI API, Anthropic API, local models, or manual review.

## Philosophy

```text
Adapters collect.
Core structures.
Metrics measure.
Graphs reveal.
Skills interpret.
LLM explains.
Reports recommend.
```

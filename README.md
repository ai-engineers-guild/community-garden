# Community Garden Core

# Community Garden Core

**Community Garden** — это социологический ИИ-движок для глубокой аналитики сообществ. В отличие от стандартных ботов-статистиков, которые просто считают количество сообщений и активных юзеров, этот проект применяет социологические концепты (например, теорию "Садовника и Сорняков" Э. Юдковского), выявляя реальные поведенческие риски (выгорание экспертов, токсичность, перегруз) и формируя конкретный Action Plan для комьюнити-менеджера.

## 🛠 Два режима работы:

1. **Agent Skill (Offline/CLI)**: Локальный file-first пайплайн. Парсит сырые архивы (Telegram JSON) в унифицированные события. Автономные AI-агенты (например, в IDE или через CLI) читают подготовленные `llm_packs` и запускают свои аналитические "скиллы" (`role_analysis`, `tribe_analysis`, `risk_analysis`, `admin_mirror`) для генерации Markdown-отчетов. Никаких серверов, всё хранится локально в репозитории как "ухоженный сад данных" (`.garden/`).
2. **SaaS / Telegram Bot (Runtime Wrapper - In Roadmap)**: Полноценный микросервис на FastAPI. Любой админ может добавить бота к себе в группу, "скормить" ему свой LLM API токен (BYOK), и бот начнет в реальном времени следить за здоровьем комьюнити, отправлять On-Demand репорты прямо в личку, консультировать админа по статистике в режиме чата и трекать историю того, как исправляются риски (Week-over-Week).

---

## Что под капотом?

Движок превращает "сырые" события чатов в иерархию данных:
- **Bronze data**: нормализованные json-события (парсинг сервисных сообщений, банов, инвайтов).
- **Silver data**: детерминированные метрики графов и выводы LLM-скиллов (кто в каком трайбе, какие риски найдены).
- **Gold data**: финальные WOW-отчеты в Markdown/HTML форматах и графики.

Архитектура позволяет легко добавлять адаптеры (Slack, Discord, Discourse) — ядро работает с универсальным `CommunityEvent`.

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

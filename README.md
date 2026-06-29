# Community Garden Core

*[🇷🇺 Русский язык (Russian)](README.ru.md)*

**Community Garden** is a sociological AI engine for deep community analytics. Unlike standard stat-bots that merely count messages and active users, this project applies sociological concepts (e.g., Eliezer Yudkowsky's "Well-Kept Gardens Die by Pacifism" theory) to identify real behavioral risks (expert burnout, toxicity, information overload) and generate concrete Action Plans for community managers.

## 🛠 Two Modes of Operation

1. **Agent Skill (Offline/CLI)**: A local file-first pipeline. It parses raw archives (Telegram JSON) into unified events. Autonomous AI agents (e.g., in an IDE or via CLI) read the prepared `llm_packs` and run their analytical "skills" (`role_analysis`, `tribe_analysis`, `risk_analysis`, `admin_mirror`) to generate Markdown reports. No servers required; everything is stored locally in the repository as a "well-kept garden of data" (`.garden/`).
2. **SaaS / Telegram Bot (Runtime Wrapper - [See Roadmap](ROADMAP.md))**: A fully-fledged FastAPI microservice. Any admin can add the bot to their group, provide their LLM API token (BYOK - Bring Your Own Key), and the bot will monitor community health in real-time. It sends On-Demand reports via DMs, acts as a statistical consultant in chat, and tracks risk resolution over time (Week-over-Week).

---

## What's under the hood?

The engine transforms "raw" chat events into a data hierarchy:

- **Bronze data**: normalized json-events (parsing service messages, bans, invites).
- **Silver data**: deterministic graph metrics and LLM-skill findings (who is in which tribe, what risks were found).
- **Gold data**: final Week-over-Week reports in Markdown/HTML formats and charts.

The architecture easily accommodates new adapters (Slack, Discord, Discourse) — the core operates on a universal `CommunityEvent` model.

## 🚀 Quick Start

1. **Install**

   ```bash
   uv sync
   uv run cg --help
   ```

2. **Initialize & Import**

   ```bash
   uv run cg init ./demo-garden --community-id demo --name "Demo Community"
   uv run cg import telegram-export ./sample_data/telegram_result.json --project ./demo-garden
   ```

3. **Analyze & Generate LLM Packs**

   ```bash
   uv run cg analyze --project ./demo-garden --period 2026-W26
   uv run cg llm-pack weekly --project ./demo-garden --period 2026-W26
   ```

4. **Run AI Agents (Offline Skill)**
   Use your favorite AI agent (Gemini, Claude, Cursor) with this repository and ask it to run the `community-garden` orchestration skill to generate the final WOW report.

## 🗺 Roadmap

Check out our [ROADMAP.md](ROADMAP.md) to see the upcoming features, including the Telegram Bot SaaS implementation, real-time tracking, and multi-tenant capabilities.

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

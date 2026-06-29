# AGENTS (Community Garden)

**Community Garden** — это не просто бот для сбора метрик. Это *социологический ИИ-движок*, который анализирует поведение участников, выявляет токсичность, находит скрытых лидеров и оценивает здоровье сообщества, опираясь на фундаментальные социологические концепции (например, теорию Элиезера Юдковского "Ухоженный сад").

## 🛠 Режимы работы
Проект может работать в двух ипостасях:
1. **Offline AI Skill (текущий)**: ИИ-агент (оркестратор) запускается локально в консоли/IDE. Он использует репозиторий как file-first базу данных (`.garden/`), читает выгруженные логи (JSON) и генерирует отчеты.
2. **Runtime Bot Wrapper (Roadmap)**: Полноценный SaaS Telegram-бот, который сидит в чатах, общается с админами в личке (Chat with Data), рисует графики по запросу, следит за выполнением установленных правил (Community Guidelines) и генерирует публичные анонимные отчеты.

## Rules

- **Source of truth:** All source data must be normalized into `.garden/bronze/events/*.jsonl`.
- **Deterministic metrics:** Belong in `.garden/silver/metrics/` and `.garden/silver/graphs/`.
- **LLM-facing context:** Belong in `.garden/gold/llm_packs/`.
- **Findings & Insights:** Belong in `.garden/silver/findings/` and `.garden/silver/risks/`.
- **Human-facing reports:** Belong in `.garden/gold/reports/`.
- **Tone & Ethics:** Act as a cynical, objective sociologist. Name specific users (names/nicknames, no abstract IDs) for both praise and risks. Do not invent facts. Use behavioral terms, not medical diagnoses.
- **Evidence:** Every finding must include evidence (quotes or message IDs).

## Typical workflow

1. **Import data:**
```bash
cg import telegram-export result.json --project .
```
2. **Calculate deterministic stats and prepare LLM packs:**
```bash
cg analyze --project . --period last-week
```
3. **Run AI Agent Orchestrator:**
Ask the AI Agent (e.g., Serena/Gemini) to execute the `community-garden` orchestration skill. The agent will read the LLM packs and automatically run the semantic analysis skills (`role_analysis`, `tribe_analysis`, `risk_analysis`, `admin_mirror`, `semantic_metrics`, `recommendations`) and generate the final report via `report_generator`.

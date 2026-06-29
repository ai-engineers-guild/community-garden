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

## 🚀 Быстрый старт (Quick Start)

1. **Установка**
   ```bash
   uv sync
   uv run cg --help
   ```

2. **Инициализация и импорт**
   ```bash
   uv run cg init ./demo-garden --community-id demo --name "Demo Community"
   uv run cg import telegram-export ./sample_data/telegram_result.json --project ./demo-garden
   ```

3. **Анализ и подготовка LLM-паков**
   ```bash
   uv run cg analyze --project ./demo-garden --period 2026-W26
   uv run cg llm-pack weekly --project ./demo-garden --period 2026-W26
   ```

4. **Запуск ИИ-Агентов (Offline Skill)**
   Используйте любого ИИ-агента (Gemini, Claude, Cursor) в этом репозитории и попросите его выполнить скилл-оркестратор `community-garden`, чтобы сгенерировать финальный WOW-отчет.

## 🗺 Roadmap (План развития)

Загляните в наш [ROADMAP.md](ROADMAP.md), чтобы увидеть будущие фичи, включая SaaS Telegram-бота, отслеживание в реальном времени и Multi-Tenant возможности.

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

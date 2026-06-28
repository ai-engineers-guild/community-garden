from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from community_garden.adapters.telegram_export import TelegramExportAdapter
from community_garden.core.pipeline import analyze_project
from community_garden.periods import normalize_period
from community_garden.project import GardenProject
from community_garden.reports.weekly import render_weekly
from community_garden.utils import write_text

app = typer.Typer(help="Community Garden Core CLI")
import_app = typer.Typer(help="Import source data")
report_app = typer.Typer(help="Generate reports")
llm_app = typer.Typer(help="Generate LLM-friendly packs")
chart_app = typer.Typer(help="Generate chart artifacts")
skill_app = typer.Typer(help="Run deterministic skill scaffolds")
telegram_app = typer.Typer(help="Telegram helpers")
app.add_typer(import_app, name="import")
app.add_typer(report_app, name="report")
app.add_typer(llm_app, name="llm-pack")
app.add_typer(chart_app, name="chart")
app.add_typer(skill_app, name="skill")
app.add_typer(telegram_app, name="telegram")
console = Console()


def run(coro):
    return asyncio.run(coro)


@app.command()
def init(
    path: Path = typer.Argument(..., help="Project root directory"),
    community_id: str = typer.Option("community"),
    name: str = typer.Option("Community"),
    timezone: str = typer.Option("UTC"),
):
    project = GardenProject.init(path, community_id=community_id, name=name, timezone=timezone)
    console.print(f"[green]Initialized[/green] {project.garden_dir}")


@import_app.command("telegram-export")
def import_telegram_export(
    input_path: Path = typer.Argument(..., help="Telegram Desktop result.json"),
    project: Path = typer.Option(Path("."), help="Project root"),
    community_id: Optional[str] = typer.Option(None),
):
    gp = GardenProject(project)
    cfg = gp.config
    adapter = TelegramExportAdapter(input_path, community_id=community_id or cfg.community_id)

    async def _go():
        events = [e async for e in adapter.iter_events()]
        count = gp.write_events(events)
        return count

    count = run(_go())
    console.print(f"[green]Imported[/green] {count} events into {gp.garden_dir / 'bronze/events'}")


@app.command()
def analyze(
    project: Path = typer.Option(Path("."), help="Project root"),
    period: str = typer.Option("last-week", help="YYYY-Www, YYYY-MM, YYYY-MM-DD, last-week, current-week"),
):
    gp = GardenProject(project)
    result = run(analyze_project(gp, normalize_period(period)))
    console.print(f"[green]Analyzed[/green] period={result['period']} events={result['events']}")
    console.print(f"Garden Health: {result['garden_health']['garden_health_score']}/100")


@report_app.command("weekly")
def report_weekly(
    project: Path = typer.Option(Path("."), help="Project root"),
    period: str = typer.Option("last-week"),
):
    gp = GardenProject(project)
    path = render_weekly(gp.lake, normalize_period(period))
    console.print(f"[green]Wrote[/green] {path}")


@llm_app.command("weekly")
def llm_weekly(
    project: Path = typer.Option(Path("."), help="Project root"),
    period: str = typer.Option("last-week"),
):
    gp = GardenProject(project)
    period = normalize_period(period)
    path = gp.lake.gold_path("llm_packs", f"weekly_{period}.md")
    if not path.exists():
        run(analyze_project(gp, period))
    console.print(f"[green]LLM pack[/green] {path}")


@chart_app.command("radar")
def chart_radar(
    project: Path = typer.Option(Path("."), help="Project root"),
    period: str = typer.Option("last-week"),
):
    from community_garden.charts.radar import write_radar_chart

    gp = GardenProject(project)
    period = normalize_period(period)
    doc = gp.lake.read_silver_yaml(f"metrics/{period}.yml", default={}) or {}
    if not doc:
        run(analyze_project(gp, period))
        doc = gp.lake.read_silver_yaml(f"metrics/{period}.yml", default={}) or {}
    out = gp.lake.gold_path("charts", f"garden_health_radar_{period}.png")
    write_radar_chart(doc.get("garden_health", {}), out)
    console.print(f"[green]Wrote[/green] {out}")


@skill_app.command("run")
def skill_run(
    name: str = typer.Argument("all"),
    project: Path = typer.Option(Path("."), help="Project root"),
    period: str = typer.Option("last-week"),
):
    from community_garden.skills.runner import SkillRunner

    gp = GardenProject(project)
    period = normalize_period(period)
    doc = gp.lake.read_silver_yaml(f"metrics/{period}.yml", default={}) or {}
    if not doc:
        run(analyze_project(gp, period))
        doc = gp.lake.read_silver_yaml(f"metrics/{period}.yml", default={}) or {}
    metrics = doc.get("metrics", {})
    runner = SkillRunner(gp.garden_dir)
    if name == "all":
        result = runner.run_all(period, metrics)
    elif name == "semantic_metrics":
        result = runner.run_semantic_metric_placeholders(period, metrics)
    elif name == "risk_analysis":
        result = runner.run_rule_based_risk_scan(period, metrics)
    else:
        raise typer.BadParameter(f"Unknown deterministic skill scaffold: {name}")
    console.print(f"[green]Ran skill[/green] {name}: {result.keys() if isinstance(result, dict) else 'ok'}")


@telegram_app.command("collect")
def telegram_collect(
    token: str = typer.Option(..., envvar="TELEGRAM_BOT_TOKEN"),
    project: Path = typer.Option(Path("."), help="Project root"),
):
    from community_garden.adapters.telegram_bot import collect_long_polling

    gp = GardenProject(project)
    out = gp.lake.raw_path("telegram_bot", "updates.jsonl")
    console.print("[yellow]Starting Telegram long-polling collector. Bot sees only future updates.[/yellow]")
    run(collect_long_polling(token=token, community_id=gp.config.community_id, out_jsonl=str(out)))


@app.command("serve")
def serve(
    project: Path = typer.Option(Path("."), help="Project root"),
    host: str = typer.Option("127.0.0.1"),
    port: int = typer.Option(8000),
):
    try:
        import uvicorn
    except ImportError as exc:
        raise RuntimeError("Install FastAPI extra: uv sync --extra fastapi") from exc
    import os
    os.environ["COMMUNITY_GARDEN_PROJECT"] = str(project.resolve())
    uvicorn.run("community_garden.interfaces.fastapi_app:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    app()

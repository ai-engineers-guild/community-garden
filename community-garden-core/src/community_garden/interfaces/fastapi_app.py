from __future__ import annotations

import os
from pathlib import Path

from community_garden.core.pipeline import analyze_project
from community_garden.periods import normalize_period
from community_garden.project import GardenProject
from community_garden.reports.weekly import render_weekly

try:
    from fastapi import FastAPI
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install FastAPI extra: uv sync --extra fastapi") from exc

app = FastAPI(title="Community Garden Core", version="0.1.0")


def get_project() -> GardenProject:
    return GardenProject(Path(os.environ.get("COMMUNITY_GARDEN_PROJECT", ".")))


@app.get("/health")
def health() -> dict:
    return {"ok": True}


@app.post("/analyze/{period}")
async def analyze(period: str) -> dict:
    gp = get_project()
    return await analyze_project(gp, normalize_period(period))


@app.post("/reports/weekly/{period}")
def weekly_report(period: str) -> dict:
    gp = get_project()
    path = render_weekly(gp.lake, normalize_period(period))
    return {"path": str(path)}


@app.get("/reports/weekly/{period}")
def get_weekly_report(period: str) -> dict:
    gp = get_project()
    period = normalize_period(period)
    path = gp.lake.gold_path("reports", "weekly", f"{period}.md")
    return {"period": period, "exists": path.exists(), "content": path.read_text(encoding="utf-8") if path.exists() else None}


@app.get("/metrics/{period}")
def get_metrics(period: str) -> dict:
    gp = get_project()
    period = normalize_period(period)
    return gp.lake.read_silver_yaml(f"metrics/{period}.yml", default={}) or {}

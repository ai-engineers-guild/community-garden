from __future__ import annotations

from community_garden.core.pipeline import analyze_project
from community_garden.periods import normalize_period
from community_garden.project import GardenProject
from community_garden.reports.weekly import render_weekly


async def run_weekly_job(project_path: str, period: str = "last-week") -> str:
    project = GardenProject(project_path)
    period = normalize_period(period)
    await analyze_project(project, period)
    path = render_weekly(project.lake, period)
    return str(path)

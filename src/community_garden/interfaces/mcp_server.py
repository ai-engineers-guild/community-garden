from __future__ import annotations

import os
from pathlib import Path

from community_garden.core.pipeline import analyze_project
from community_garden.periods import normalize_period
from community_garden.project import GardenProject
from community_garden.reports.weekly import render_weekly


def get_project() -> GardenProject:
    return GardenProject(Path(os.environ.get("COMMUNITY_GARDEN_PROJECT", ".")))


def main() -> None:
    """Minimal MCP server wrapper.

    Requires optional dependency: `uv sync --extra mcp`.
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("Install MCP extra: uv sync --extra mcp") from exc

    mcp = FastMCP("community-garden")

    @mcp.tool()
    async def garden_analyze(period: str = "last-week") -> dict:
        return await analyze_project(get_project(), normalize_period(period))

    @mcp.tool()
    def garden_weekly_report(period: str = "last-week") -> str:
        path = render_weekly(get_project().lake, normalize_period(period))
        return path.read_text(encoding="utf-8")

    @mcp.resource("garden://reports/weekly/latest")
    def latest_weekly_report() -> str:
        gp = get_project()
        reports = sorted(gp.lake.gold_path("reports", "weekly").glob("*.md"))
        return reports[-1].read_text(encoding="utf-8") if reports else "No reports yet."

    mcp.run()


if __name__ == "__main__":
    main()

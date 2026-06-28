from __future__ import annotations

import asyncio
from pathlib import Path

from community_garden.adapters.telegram_export import TelegramExportAdapter
from community_garden.core.pipeline import analyze_project
from community_garden.project import GardenProject


def test_telegram_export_pipeline(tmp_path: Path):
    src = Path(__file__).parents[1] / "sample_data" / "telegram_result.json"
    project = GardenProject.init(tmp_path / "garden", community_id="demo", name="Demo")

    async def go():
        adapter = TelegramExportAdapter(src, community_id="demo")
        events = [e async for e in adapter.iter_events()]
        project.write_events(events)
        return await analyze_project(project, "2026-W26")

    result = asyncio.run(go())
    assert result["events"] == 6
    assert result["metrics"]["activity"]["messages_total"] == 6
    assert result["metrics"]["response"]["question_candidates"] >= 2

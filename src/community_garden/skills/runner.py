from __future__ import annotations

from pathlib import Path
from typing import Any


class SkillRunner:
    """Deterministic skill scaffold.

    This runner focuses on computing discrete metrics and basic aggregations.
    Complex rule-based risks and semantic evaluations are now handled by dedicated agent skills
    (see .agents/skills/risk_analysis and .agents/skills/semantic_metrics).
    """

    def __init__(self, garden_dir: Path):
        self.garden_dir = garden_dir

    def run_all(self, period: str, metrics: dict) -> dict[str, Any]:
        # Basic statistical aggregations can be added here.
        # Semantic metrics and risks are now handled by specialized LLM skills.
        return {"status": "success", "message": "Run skills manually or via agent orchestration"}

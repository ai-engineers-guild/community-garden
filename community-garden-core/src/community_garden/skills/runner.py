from __future__ import annotations

from pathlib import Path
from typing import Any

from community_garden.utils import read_yaml, write_yaml, stable_id


class SkillRunner:
    """Deterministic skill scaffold.

    This runner intentionally does not call any LLM by default. It creates structured inputs/outputs
    and placeholder findings that an external LLM or agent can fill, validate, and commit.
    """

    def __init__(self, garden_dir: Path):
        self.garden_dir = garden_dir

    def run_semantic_metric_placeholders(self, period: str, metrics: dict) -> dict[str, Any]:
        registry = read_yaml(self.garden_dir / "skills" / "semantic_metrics" / "registry.yml", default={}) or {}
        result = {"period": period, "semantic_metrics": {}}
        for key, cfg in (registry.get("metrics") or {}).items():
            result["semantic_metrics"][key] = {
                "score": None,
                "source": "semantic_skill_required",
                "confidence": None,
                "definition": cfg.get("title", key),
                "required_evidence": cfg.get("required_evidence", []),
            }
        out = self.garden_dir / "silver" / "findings" / f"semantic_metrics_{period}.yml"
        write_yaml(out, result)
        return result

    def run_rule_based_risk_scan(self, period: str, metrics: dict) -> dict[str, Any]:
        risks = []
        response = metrics.get("response", {})
        breadth = metrics.get("breadth", {})
        admin = metrics.get("admin", {})
        readability = metrics.get("readability", {})
        if (response.get("unanswered_question_rate") or 0) >= 0.35:
            risks.append({
                "id": stable_id(period, "newcomer_or_question_response_risk"),
                "risk": "newcomer_churn_risk",
                "severity": "high",
                "summary": "High share of question-like messages has no direct replies.",
                "evidence": ["metrics.response.unanswered_question_rate"],
            })
        if (breadth.get("top_5_message_share") or 0) >= 0.55:
            risks.append({
                "id": stable_id(period, "tribal_capture_or_concentration"),
                "risk": "tribal_capture_risk",
                "severity": "medium",
                "summary": "Top-5 authors produce more than half of all messages.",
                "evidence": ["metrics.breadth.top_5_message_share"],
            })
        if (readability.get("messages_per_active_day") or 0) >= 250:
            risks.append({
                "id": stable_id(period, "overload_risk"),
                "risk": "overload_risk",
                "severity": "medium",
                "summary": "Daily message volume may make chat hard to read.",
                "evidence": ["metrics.readability.messages_per_active_day"],
            })
        if (admin.get("admin_message_share") or 0) >= 0.35:
            risks.append({
                "id": stable_id(period, "admin_dependency"),
                "risk": "admin_dependency_risk",
                "severity": "medium",
                "summary": "Large share of messages comes from admins; check founder dependency.",
                "evidence": ["metrics.admin.admin_message_share"],
            })
        result = {"period": period, "risks": risks}
        write_yaml(self.garden_dir / "silver" / "risks" / f"risks_{period}.yml", result)
        return result

    def run_all(self, period: str, metrics: dict) -> dict[str, Any]:
        semantic = self.run_semantic_metric_placeholders(period, metrics)
        risks = self.run_rule_based_risk_scan(period, metrics)
        return {"semantic": semantic, "risks": risks}

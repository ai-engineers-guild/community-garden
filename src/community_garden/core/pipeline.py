from __future__ import annotations

from community_garden.graph.analysis import build_interaction_graph, export_graphml, graph_metrics
from community_garden.llm.packs import build_weekly_llm_pack
from community_garden.metrics.basic import calculate_basic_metrics, garden_health_from_metrics
from community_garden.periods import normalize_period
from community_garden.project import GardenProject
from community_garden.skills.runner import SkillRunner


async def analyze_project(project: GardenProject, period: str | None = None) -> dict:
    period = normalize_period(period)
    cfg = project.config
    events = project.load_events(period=period)
    metrics = calculate_basic_metrics(events, member_count_snapshot=cfg.member_count_snapshot)
    health = garden_health_from_metrics(metrics)
    graph = build_interaction_graph(events)
    gmetrics = graph_metrics(graph)
    project.lake.write_silver_yaml(
        f"metrics/{period}.yml", {"period": period, "metrics": metrics, "garden_health": health}
    )
    project.lake.write_silver_yaml(f"graphs/{period}.yml", {"period": period, "graph": gmetrics})
    export_graphml(graph, project.lake.silver_path("graphs", f"reply_graph_{period}.graphml"))
    SkillRunner(project.garden_dir).run_all(period, metrics)
    llm_pack = build_weekly_llm_pack(events, metrics, gmetrics, period)
    project.lake.write_gold_text(f"llm_packs/weekly_{period}.md", llm_pack)
    return {
        "period": period,
        "events": len(events),
        "metrics": metrics,
        "garden_health": health,
        "graph": gmetrics,
    }

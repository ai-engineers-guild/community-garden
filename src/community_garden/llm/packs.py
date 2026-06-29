from __future__ import annotations

from collections import Counter, defaultdict

from community_garden.models import CommunityEvent


def _name(event: CommunityEvent) -> str:
    if event.actor:
        return event.actor.display_name or event.actor.username or event.actor.id
    return "unknown"


def build_weekly_llm_pack(
    events: list[CommunityEvent],
    metrics: dict,
    graph_metrics: dict,
    period: str,
    max_messages: int = 1200,
) -> str:
    by_author = Counter(e.actor.id if e.actor else "unknown" for e in events)
    by_day = defaultdict(list)
    for e in events:
        by_day[e.timestamp.date().isoformat()].append(e)
    lines: list[str] = []
    lines.append(f"# LLM Pack: {period}")
    lines.append("")
    lines.append(
        "This pack is generated for external LLM analysis. It preserves chronological flow, reply context, metrics, graph hints, and evidence ids."
    )
    lines.append("")
    lines.append("## Deterministic metrics")
    lines.append("```yaml")
    import yaml

    lines.append(yaml.safe_dump(metrics, allow_unicode=True, sort_keys=False))
    lines.append("```")
    lines.append("")
    lines.append("## Graph metrics")
    lines.append("```yaml")
    lines.append(yaml.safe_dump(graph_metrics, allow_unicode=True, sort_keys=False))
    lines.append("```")
    lines.append("")
    lines.append("## Top authors")
    for actor, count in by_author.most_common(20):
        lines.append(f"- `{actor}`: {count} messages")
    lines.append("")
    lines.append("## Chronological message sample")
    selected = events[-max_messages:] if len(events) > max_messages else events
    for day in sorted({e.timestamp.date().isoformat() for e in selected}):
        lines.append(f"\n### {day}")
        for e in [x for x in selected if x.timestamp.date().isoformat() == day]:
            text = (e.content.clean_text or e.content.text or "").replace("\n", " ").strip()
            if not text and e.event_type.value != "admin_action":
                continue
            reply = (
                f" reply_to={e.relation.reply_to_event_id}" if e.relation.reply_to_event_id else ""
            )
            lines.append(
                f"- [{e.timestamp.strftime('%H:%M')}] `{e.event_id}` {_name(e)}{reply}: {text[:1200]}"
            )
    lines.append("")
    lines.append("## Analysis instruction")
    lines.append(
        "Use this pack to produce evidence-based community intelligence. Do not invent facts. Every strong claim must point to event ids or metric blocks."
    )
    return "\n".join(lines).strip() + "\n"

from __future__ import annotations

from pathlib import Path

from jinja2 import Template

from community_garden.lake import GardenLake
from community_garden.periods import normalize_period
from community_garden.utils import read_yaml

TEMPLATE = Template(r'''
# Weekly Garden Report — {{ period }}

## 1. Data limitations

- This report is generated from available normalized events in `.garden/bronze/events`.
- Silent readers are only estimated if `member_count_snapshot` is provided in `.garden/community.yml`.
- Semantic metrics with `semantic_skill_required` require external LLM or manual analysis.
- Role, tribe, risk, and admin conclusions should be treated as hypotheses unless supported by evidence ids.

## 2. Executive summary

Garden Health Score: **{{ garden_health.garden_health_score }}/100**

Core deterministic signal:

- Messages: **{{ metrics.activity.messages_total }}**
- Unique speakers: **{{ metrics.activity.unique_speakers }}**
- Top-5 message share: **{{ '%.1f'|format(metrics.breadth.top_5_message_share * 100) }}%**
- Question-like messages: **{{ metrics.response.question_candidates }}**
- Unanswered question candidates: **{{ metrics.response.unanswered_question_candidates }}**
- Participation Gini: **{{ metrics.breadth.participation_gini }}**

## 3. Garden Health Radar

| Dimension | Score | Source |
|---|---:|---|
{% for key, item in garden_health.radar.items() -%}
| {{ key }} | {{ item.score if item.score is not none else 'TBD' }} | {{ item.source }} |
{% endfor %}

## 4. Activity

| Metric | Value |
|---|---:|
| Messages total | {{ metrics.activity.messages_total }} |
| Text messages | {{ metrics.activity.text_messages_total }} |
| Unique speakers | {{ metrics.activity.unique_speakers }} |
| Avg messages per active day | {{ metrics.activity.avg_messages_per_active_day }} |

### Messages by day

{% for day, count in metrics.activity.messages_by_day.items() -%}
- {{ day }}: {{ count }}
{% endfor %}

## 5. Breadth / participation concentration

| Metric | Value |
|---|---:|
| Top-5 message share | {{ '%.1f'|format(metrics.breadth.top_5_message_share * 100) }}% |
| Participation Gini | {{ metrics.breadth.participation_gini }} |
| One-shot authors | {{ metrics.breadth.one_shot_authors_count }} |
| Returning authors | {{ metrics.breadth.returning_authors_count }} |
| Active speaker ratio | {{ metrics.breadth.active_speaker_ratio if metrics.breadth.active_speaker_ratio is not none else 'unknown' }} |
| Silent reader estimate | {{ metrics.breadth.silent_reader_estimate if metrics.breadth.silent_reader_estimate is not none else 'unknown' }} |

### Top authors

{% for actor, count in metrics.breadth.top_authors -%}
- `{{ actor }}`: {{ count }} messages
{% endfor %}

## 6. Response / care metrics

| Metric | Value |
|---|---:|
| Replies | {{ metrics.response.reply_count }} |
| Question candidates | {{ metrics.response.question_candidates }} |
| Unanswered question candidates | {{ metrics.response.unanswered_question_candidates }} |
| Unanswered question rate | {{ '%.1f'|format(metrics.response.unanswered_question_rate * 100) }}% |
| Median first response minutes | {{ metrics.response.median_first_response_minutes if metrics.response.median_first_response_minutes is not none else 'unknown' }} |

## 7. Network graph

| Metric | Value |
|---|---:|
| Nodes | {{ graph.nodes }} |
| Edges | {{ graph.edges }} |
| Density | {{ graph.density }} |

### Candidate leaders by weighted degree

{% for actor, score in graph.leaders -%}
- `{{ actor }}`: {{ score }}
{% endfor %}

### Candidate bridges by betweenness

{% for actor, score in graph.bridges -%}
- `{{ actor }}`: {{ score }}
{% endfor %}

### Candidate graph communities

{% for community in graph.communities -%}
- {{ community }}
{% endfor %}

## 8. Risks

{% if risks.risks -%}
{% for risk in risks.risks -%}
### {{ risk.risk }} — {{ risk.severity }}

{{ risk.summary }}

Evidence: {{ risk.evidence }}

{% endfor -%}
{% else -%}
No deterministic risk findings generated. Run semantic/risk skills for deeper analysis.
{% endif %}

## 9. Admin Mirror

Deterministic admin signals:

- Admin message count: **{{ metrics.admin.admin_message_count }}**
- Admin message share: **{{ '%.1f'|format(metrics.admin.admin_message_share * 100) }}%**
- Self-sustained reply targets: **{{ metrics.admin.self_sustained_reply_targets }}**

Semantic Admin Mirror still needs external LLM review using `gold/llm_packs/weekly_{{ period }}.md`.

## 10. Recommendations

Initial deterministic recommendations:

{% if metrics.response.unanswered_question_rate >= 0.35 -%}
1. Reduce unanswered questions: assign a weekly steward to scan unanswered questions and route them to experts.
{% endif -%}
{% if metrics.breadth.top_5_message_share >= 0.55 -%}
2. Reduce agenda capture risk: invite quieter valuable members into discussions and split hot topics into focused threads.
{% endif -%}
{% if metrics.readability.messages_per_active_day >= 250 -%}
3. Improve readability: create a daily digest or summarize overloaded threads.
{% endif -%}
4. Run semantic skills for tribe analysis, role drift, Admin Mirror, and recommendation refinement.

## 11. Next analysis step

Use:

```bash
cg llm-pack weekly --period {{ period }}
```

Then run an external LLM over the pack with the project skills in `.garden/skills`.
''')


def render_weekly(lake: GardenLake, period: str | None = None) -> Path:
    period = normalize_period(period)
    metrics_doc = lake.read_silver_yaml(f"metrics/{period}.yml", default={}) or {}
    graph_doc = lake.read_silver_yaml(f"graphs/{period}.yml", default={}) or {}
    risks_doc = read_yaml(lake.root / "silver" / "risks" / f"risks_{period}.yml", default={"risks": []}) or {"risks": []}
    text = TEMPLATE.render(
        period=period,
        metrics=metrics_doc.get("metrics", {}),
        garden_health=metrics_doc.get("garden_health", {}),
        graph=graph_doc.get("graph", {}),
        risks=risks_doc,
    )
    return lake.write_gold_text(f"reports/weekly/{period}.md", text)

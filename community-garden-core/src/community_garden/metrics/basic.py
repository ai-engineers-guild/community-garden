from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime
from math import fsum
from statistics import median

from community_garden.models import CommunityEvent, EventType
from community_garden.periods import event_day


def actor_id(event: CommunityEvent) -> str:
    return event.actor.id if event.actor else "unknown"


def has_text(event: CommunityEvent) -> bool:
    return bool((event.content.clean_text or event.content.text or "").strip())


def is_question_like(event: CommunityEvent) -> bool:
    text = (event.content.clean_text or event.content.text or "").lower()
    if not text:
        return False
    markers = ["?", "как ", "почему", "что ", "где ", "кто ", "можно ли", "зачем", "какой", "какая", "which", "how ", "why ", "what "]
    return any(m in text for m in markers)


def gini(values: list[int | float]) -> float:
    values = [v for v in values if v >= 0]
    if not values:
        return 0.0
    values.sort()
    n = len(values)
    total = fsum(values)
    if total == 0:
        return 0.0
    cum = fsum((i + 1) * v for i, v in enumerate(values))
    return (2 * cum) / (n * total) - (n + 1) / n


def calculate_basic_metrics(events: list[CommunityEvent], member_count_snapshot: int | None = None) -> dict:
    messages = [e for e in events if e.event_type in {EventType.MESSAGE_CREATED, EventType.MESSAGE_EDITED}]
    text_messages = [e for e in messages if has_text(e)]
    actors = [actor_id(e) for e in messages]
    unique_actors = sorted(set(actors))
    by_actor = Counter(actors)
    by_day = Counter(event_day(e.timestamp) for e in messages)
    by_hour = Counter(e.timestamp.hour for e in messages)
    admin_messages = [e for e in messages if e.actor and e.actor.is_admin]
    replies = [e for e in messages if e.relation.reply_to_event_id or e.relation.reply_to_message_id]
    questions = [e for e in text_messages if is_question_like(e)]
    response_times: list[float] = []
    by_msg_id = {e.event_id: e for e in messages}
    by_reply_to_raw = defaultdict(list)
    for e in replies:
        if e.relation.reply_to_event_id:
            by_reply_to_raw[e.relation.reply_to_event_id].append(e)
    for q in questions:
        replies_to_q = by_reply_to_raw.get(q.event_id, [])
        if replies_to_q:
            first = min(replies_to_q, key=lambda e: e.timestamp)
            response_times.append((first.timestamp - q.timestamp).total_seconds() / 60)
    unanswered = [q for q in questions if not by_reply_to_raw.get(q.event_id)]
    top_counts = by_actor.most_common(10)
    total_messages = len(messages)
    top5_share = sum(c for _, c in by_actor.most_common(5)) / total_messages if total_messages else 0
    active_speaker_ratio = len(unique_actors) / member_count_snapshot if member_count_snapshot else None
    one_shot_authors = [a for a, c in by_actor.items() if c == 1]
    returning_authors = [a for a, c in by_actor.items() if c >= 2]
    self_sustained_threads = sum(1 for target, reps in by_reply_to_raw.items() if reps and all(not (e.actor and e.actor.is_admin) for e in reps))
    days = sorted(by_day)
    return {
        "activity": {
            "messages_total": total_messages,
            "text_messages_total": len(text_messages),
            "unique_speakers": len(unique_actors),
            "messages_by_day": dict(sorted(by_day.items())),
            "messages_by_hour": dict(sorted(by_hour.items())),
            "avg_messages_per_active_day": round(total_messages / len(days), 2) if days else 0,
            "peak_day": max(by_day.items(), key=lambda x: x[1]) if by_day else None,
        },
        "breadth": {
            "top_5_message_share": round(top5_share, 4),
            "participation_gini": round(gini(list(by_actor.values())), 4),
            "top_authors": top_counts,
            "one_shot_authors_count": len(one_shot_authors),
            "returning_authors_count": len(returning_authors),
            "active_speaker_ratio": round(active_speaker_ratio, 4) if active_speaker_ratio is not None else None,
            "silent_reader_estimate": member_count_snapshot - len(unique_actors) if member_count_snapshot else None,
        },
        "response": {
            "reply_count": len(replies),
            "question_candidates": len(questions),
            "unanswered_question_candidates": len(unanswered),
            "unanswered_question_rate": round(len(unanswered) / len(questions), 4) if questions else 0,
            "median_first_response_minutes": round(median(response_times), 2) if response_times else None,
        },
        "admin": {
            "admin_message_count": len(admin_messages),
            "admin_message_share": round(len(admin_messages) / total_messages, 4) if total_messages else 0,
            "self_sustained_reply_targets": self_sustained_threads,
        },
        "readability": {
            "messages_per_active_day": round(total_messages / len(days), 2) if days else 0,
            "long_text_messages": sum(1 for e in text_messages if len(e.content.clean_text or "") > 800),
            "link_messages": sum(1 for e in messages if e.content.has_link),
            "media_messages": sum(1 for e in messages if e.content.has_media),
        },
    }


def garden_health_from_metrics(metrics: dict) -> dict:
    activity = metrics.get("activity", {})
    breadth = metrics.get("breadth", {})
    response = metrics.get("response", {})
    admin = metrics.get("admin", {})
    readability = metrics.get("readability", {})

    msg_total = activity.get("messages_total", 0) or 0
    speakers = activity.get("unique_speakers", 0) or 0
    top5 = breadth.get("top_5_message_share", 0) or 0
    unanswered = response.get("unanswered_question_rate", 0) or 0
    admin_share = admin.get("admin_message_share", 0) or 0
    per_day = readability.get("messages_per_active_day", 0) or 0

    vitality = min(100, int((msg_total ** 0.5) * 6 + speakers * 2))
    diversity = max(0, min(100, int(100 * (1 - top5))))
    responsiveness = max(0, min(100, int(100 * (1 - unanswered))))
    self_sustainability = max(0, min(100, int(100 * (1 - min(admin_share, 1)))))
    readability_score = max(0, min(100, int(100 - max(0, per_day - 150) * 0.4)))
    usefulness = int((responsiveness * 0.5 + diversity * 0.25 + vitality * 0.25))
    score = int((vitality + diversity + responsiveness + self_sustainability + readability_score + usefulness) / 6)
    return {
        "garden_health_score": score,
        "radar": {
            "vitality": {"score": vitality, "source": "deterministic"},
            "usefulness": {"score": usefulness, "source": "mixed_proxy"},
            "diversity": {"score": diversity, "source": "deterministic"},
            "safety": {"score": None, "source": "semantic_skill_required"},
            "belonging": {"score": None, "source": "semantic_skill_required"},
            "readability": {"score": readability_score, "source": "deterministic"},
            "self_sustainability": {"score": self_sustainability, "source": "deterministic"},
            "cultural_coherence": {"score": None, "source": "semantic_skill_required"},
            "leadership_depth": {"score": None, "source": "semantic_skill_required"},
            "outcome_production": {"score": None, "source": "semantic_skill_required"},
            "rule_alignment": {"score": None, "source": "semantic_skill_required"},
        },
    }

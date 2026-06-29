from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from community_garden.models import CommunityEvent
from community_garden.periods import event_day, event_in_period
from community_garden.utils import (
    append_jsonl,
    iter_jsonl,
    read_yaml,
    write_json,
    write_text,
    write_yaml,
)


class GardenLake:
    def __init__(self, root: Path):
        self.root = root

    def ensure_dirs(self) -> None:
        for rel in [
            "raw",
            "bronze/events",
            "bronze/actors",
            "bronze/snapshots",
            "silver/metrics",
            "silver/graphs",
            "silver/findings",
            "silver/roles",
            "silver/tribes",
            "silver/risks",
            "silver/history",
            "gold/reports/weekly",
            "gold/reports/comparative",
            "gold/reports/monthly",
            "gold/llm_packs",
            "gold/charts",
            "gold/recommendations",
            "memory",
            "skills",
            "state",
        ]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)

    def raw_path(self, *parts: str) -> Path:
        return self.root / "raw" / Path(*parts)

    def bronze_path(self, *parts: str) -> Path:
        return self.root / "bronze" / Path(*parts)

    def silver_path(self, *parts: str) -> Path:
        return self.root / "silver" / Path(*parts)

    def gold_path(self, *parts: str) -> Path:
        return self.root / "gold" / Path(*parts)

    def write_bronze_events(self, events: Iterable[CommunityEvent]) -> int:
        buckets: dict[str, list[CommunityEvent]] = defaultdict(list)
        for event in events:
            buckets[event_day(event.timestamp)].append(event)
        written = 0
        for day, rows in buckets.items():
            path = self.bronze_path("events", f"{day}.jsonl")
            existing_ids = {row.get("event_id") for row in iter_jsonl(path)}
            new_rows: list[CommunityEvent] = []
            seen_ids = set(existing_ids)
            for row in rows:
                if row.event_id in seen_ids:
                    continue
                seen_ids.add(row.event_id)
                new_rows.append(row)
            written += append_jsonl(path, new_rows)
        return written

    def load_bronze_events(self, period: str | None = None) -> list[CommunityEvent]:
        events: list[CommunityEvent] = []
        for path in sorted(self.bronze_path("events").glob("*.jsonl")):
            for row in iter_jsonl(path):
                event = CommunityEvent.model_validate(row)
                if period is None or event_in_period(event.timestamp, period):
                    events.append(event)
        events.sort(key=lambda e: e.timestamp)
        return events

    def write_silver_yaml(self, rel: str, data: Any) -> Path:
        path = self.silver_path(*Path(rel).parts)
        write_yaml(path, data)
        return path

    def read_silver_yaml(self, rel: str, default: Any = None) -> Any:
        return read_yaml(self.silver_path(*Path(rel).parts), default=default)

    def write_gold_text(self, rel: str, text: str) -> Path:
        path = self.gold_path(*Path(rel).parts)
        write_text(path, text)
        return path

    def write_gold_json(self, rel: str, data: Any) -> Path:
        path = self.gold_path(*Path(rel).parts)
        write_json(path, data)
        return path

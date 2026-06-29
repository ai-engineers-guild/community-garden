from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from community_garden.lake import GardenLake
from community_garden.models import CommunityConfig, CommunityEvent
from community_garden.periods import normalize_period
from community_garden.utils import read_yaml, utc_now_iso, write_text, write_yaml


class GardenProject:
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.garden_dir = self.root / ".garden"
        self.lake = GardenLake(self.garden_dir)

    @classmethod
    def init(
        cls,
        root: str | Path,
        community_id: str = "community",
        name: str = "Community",
        timezone: str = "UTC",
    ) -> GardenProject:
        project = cls(root)
        project.root.mkdir(parents=True, exist_ok=True)
        project.garden_dir.mkdir(parents=True, exist_ok=True)
        cfg = CommunityConfig(
            community_id=community_id,
            name=name,
            timezone=timezone,
            created_at=utc_now_iso(),
        )
        write_yaml(project.garden_dir / "community.yml", cfg.model_dump())
        for rel, content in {
            "memory/community_rules.md": "# Community Rules\n\nAdd explicit and implicit rules here.\n",
            "memory/cultural_memory.md": "# Cultural Memory\n\nImportant events, rituals, memes, and decisions.\n",
            "memory/known_roles.md": "# Known Roles\n\nKnown admins, moderators, experts, and context.\n",
            "memory/glossary.md": "# Glossary\n\nCommunity-specific terms and memes.\n",
            "memory/previous_findings.md": "# Previous Findings\n\nAccumulated findings.\n",
            "interventions/queue.md": "# Intervention Queue\n\n",
            "interventions/done.md": "# Done Interventions\n\n",
            "interventions/history.yml": "entries: []\n",
        }.items():
            write_text(project.garden_dir / rel, content)
        project.lake.ensure_dirs()
        project.copy_builtin_skills()
        return project

    def copy_builtin_skills(self) -> None:
        # Lightweight templates copied into project for user-editability.
        skills_dir = self.garden_dir / "skills"
        skills_dir.mkdir(parents=True, exist_ok=True)
        from community_garden.skills.templates import BUILTIN_SKILLS

        for rel, content in BUILTIN_SKILLS.items():
            path = skills_dir / rel
            if not path.exists():
                write_text(path, content)

    @property
    def config(self) -> CommunityConfig:
        data = read_yaml(self.garden_dir / "community.yml", default={}) or {}
        return CommunityConfig.model_validate(data)

    def write_events(self, events: Iterable[CommunityEvent]) -> int:
        return self.lake.write_bronze_events(events)

    def load_events(self, period: str | None = None) -> list[CommunityEvent]:
        period = normalize_period(period) if period else None
        return self.lake.load_bronze_events(period=period)

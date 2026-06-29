from __future__ import annotations

from collections.abc import AsyncIterator

from community_garden.adapters.base import SourceAdapter
from community_garden.models import CommunityEvent


class DiscordAdapter(SourceAdapter):
    source_name = "discord"

    async def iter_events(self) -> AsyncIterator[CommunityEvent]:
        raise NotImplementedError(
            "DiscordAdapter is a future adapter. Implement source-specific normalization only; core stays unchanged."
        )
        yield  # pragma: no cover

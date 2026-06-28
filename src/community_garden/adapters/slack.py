from __future__ import annotations

from typing import AsyncIterator

from community_garden.adapters.base import SourceAdapter
from community_garden.models import CommunityEvent


class SlackAdapter(SourceAdapter):
    source_name = "slack"

    async def iter_events(self) -> AsyncIterator[CommunityEvent]:
        raise NotImplementedError("SlackAdapter is a future adapter. Implement source-specific normalization only; core stays unchanged.")
        yield  # pragma: no cover

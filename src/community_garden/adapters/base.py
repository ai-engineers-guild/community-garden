from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from community_garden.models import CommunityEvent


class SourceAdapter(ABC):
    source_name: str

    @abstractmethod
    async def iter_events(self) -> AsyncIterator[CommunityEvent]:
        yield  # pragma: no cover

from __future__ import annotations

from collections.abc import AsyncIterator

from community_garden.adapters.base import SourceAdapter
from community_garden.models import CommunityEvent


class WhatsAppAdapter(SourceAdapter):
    source_name = "whatsapp"

    async def iter_events(self) -> AsyncIterator[CommunityEvent]:
        raise NotImplementedError(
            "WhatsAppAdapter is a future adapter. Implement source-specific normalization only; core stays unchanged."
        )
        yield  # pragma: no cover

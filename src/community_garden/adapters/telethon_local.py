from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import datetime

from community_garden.adapters.base import SourceAdapter
from community_garden.models import Actor, CommunityEvent, Content, EventType, Relation, Space


class TelethonLocalAdapter(SourceAdapter):
    """Optional local user-session importer.

    Use only locally. Do not send `.session` files to remote servers.
    """

    source_name = "telethon_local"

    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session: str,
        chat: str,
        community_id: str,
        since: datetime | None = None,
    ):
        self.api_id = api_id
        self.api_hash = api_hash
        self.session = session
        self.chat = chat
        self.community_id = community_id
        self.since = since

    async def iter_events(self) -> AsyncIterator[CommunityEvent]:
        try:
            from telethon import TelegramClient
        except ImportError as exc:
            raise RuntimeError("Install telethon extra: uv sync --extra telethon") from exc

        async with TelegramClient(self.session, self.api_id, self.api_hash) as client:
            entity = await client.get_entity(self.chat)
            async for msg in client.iter_messages(entity, offset_date=None, reverse=True):
                if self.since and msg.date and msg.date < self.since:
                    continue
                if not msg.id:
                    continue
                actor_id = str(getattr(msg.sender, "id", "unknown")) if msg.sender else "unknown"
                text = msg.message or ""
                yield CommunityEvent(
                    event_id=f"telegram:{getattr(entity, 'id', self.chat)}:{msg.id}",
                    source=self.source_name,
                    community_id=self.community_id,
                    event_type=EventType.MESSAGE_CREATED,
                    timestamp=msg.date,
                    actor=Actor(
                        id=f"telegram:{actor_id}",
                        display_name=getattr(msg.sender, "username", None) if msg.sender else None,
                    ),
                    space=Space(
                        platform="telegram",
                        chat_id=str(getattr(entity, "id", self.chat)),
                        chat_title=getattr(entity, "title", None),
                    ),
                    relation=Relation(
                        reply_to_message_id=msg.reply_to_msg_id,
                        reply_to_event_id=f"telegram:{getattr(entity, 'id', self.chat)}:{msg.reply_to_msg_id}"
                        if msg.reply_to_msg_id
                        else None,
                    ),
                    content=Content(
                        text=text,
                        clean_text=" ".join(text.split()),
                        has_link="http://" in text or "https://" in text,
                        has_media=bool(msg.media),
                    ),
                )

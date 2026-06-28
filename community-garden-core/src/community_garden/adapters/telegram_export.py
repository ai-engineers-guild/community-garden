from __future__ import annotations

import asyncio
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncIterator

from community_garden.adapters.base import SourceAdapter
from community_garden.models import Actor, CommunityEvent, Content, EventType, RawRef, Relation, Space
from community_garden.utils import read_json, stable_id

_LINK_RE = re.compile(r"https?://|t\.me/|www\.", re.I)
_MENTION_RE = re.compile(r"(?<!\w)@([a-zA-Z0-9_]{4,})")


def _text_from_tg(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                parts.append(str(item.get("text") or ""))
        return "".join(parts)
    return str(value)


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    normalized = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        dt = datetime.strptime(value[:19], "%Y-%m-%dT%H:%M:%S")
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class TelegramExportAdapter(SourceAdapter):
    """Adapter for Telegram Desktop JSON export `result.json`."""

    source_name = "telegram_export"

    def __init__(self, path: str | Path, community_id: str, chat_id: str | None = None):
        self.path = Path(path)
        self.community_id = community_id
        self.chat_id = chat_id

    async def iter_events(self) -> AsyncIterator[CommunityEvent]:
        data = await asyncio.to_thread(read_json, self.path)
        chat_title = data.get("name") or data.get("title") or self.path.parent.name
        chat_id = str(self.chat_id or data.get("id") or data.get("personal_information", {}).get("user_id") or "telegram_export")
        messages = data.get("messages") or []
        for msg in messages:
            event = self._message_to_event(msg, chat_id=chat_id, chat_title=chat_title)
            if event:
                yield event

    def _message_to_event(self, msg: dict[str, Any], chat_id: str, chat_title: str) -> CommunityEvent | None:
        msg_id = msg.get("id")
        if msg_id is None:
            return None
        msg_type = msg.get("type") or "message"
        dt = _parse_dt(msg.get("date"))
        text = _text_from_tg(msg.get("text"))
        clean_text = " ".join(text.split()) if text else ""
        from_id = str(msg.get("from_id") or msg.get("actor_id") or msg.get("from") or msg.get("actor") or "unknown")
        display_name = str(msg.get("from") or msg.get("actor") or from_id)
        event_type = EventType.MESSAGE_CREATED
        if msg_type == "service" or msg.get("action"):
            event_type = EventType.ADMIN_ACTION
        if msg.get("edited"):
            # Telegram export keeps edited message as a message with edited field; store as created with metadata.
            event_type = EventType.MESSAGE_CREATED
        mentions = [m.group(1) for m in _MENTION_RE.finditer(text or "")]
        media_type = msg.get("media_type") or msg.get("file") or msg.get("mime_type")
        event_id = f"telegram:{chat_id}:{msg_id}"
        reply_to = msg.get("reply_to_message_id")
        return CommunityEvent(
            event_id=event_id,
            source=self.source_name,
            community_id=self.community_id,
            event_type=event_type,
            timestamp=dt,
            actor=Actor(id=f"telegram:{from_id}", display_name=display_name, username=None, raw={"from_id": from_id}),
            space=Space(platform="telegram", chat_id=chat_id, chat_title=chat_title, topic_id=str(msg.get("topic_id")) if msg.get("topic_id") else None),
            relation=Relation(
                reply_to_event_id=f"telegram:{chat_id}:{reply_to}" if reply_to else None,
                reply_to_message_id=reply_to,
                mentions=[f"telegram:{m}" for m in mentions],
                forwarded_from=str(msg.get("forwarded_from")) if msg.get("forwarded_from") else None,
            ),
            content=Content(
                text=text,
                clean_text=clean_text,
                has_link=bool(_LINK_RE.search(text or "")),
                has_media=bool(media_type),
                media_type=str(media_type) if media_type else None,
                entities=msg.get("text_entities") or [],
            ),
            raw_ref=RawRef(file=str(self.path), message_id=msg_id, source_record={
                "type": msg_type,
                "action": msg.get("action"),
                "edited": msg.get("edited"),
            }),
        )

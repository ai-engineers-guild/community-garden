from __future__ import annotations

from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

from community_garden.adapters.base import SourceAdapter
from community_garden.models import Actor, CommunityEvent, Content, EventType, Relation, Space


class TelegramBotAdapter(SourceAdapter):
    """Optional live Telegram Bot API collector.

    This is intentionally a thin adapter. It maps future Bot API updates into CommunityEvent.
    It does not fetch history.
    """

    source_name = "telegram_bot"

    def __init__(self, token: str, community_id: str, chat_id: str):
        self.token = token
        self.community_id = community_id
        self.chat_id = chat_id

    async def iter_events(self) -> AsyncIterator[CommunityEvent]:
        raise RuntimeError(
            "Live Bot API collection is not a finite iterator. Use `collect_long_polling` from CLI/service."
        )
        yield  # pragma: no cover

    @staticmethod
    def update_to_event(update: dict[str, Any], community_id: str) -> CommunityEvent | None:
        msg = update.get("message") or update.get("edited_message")
        if not msg:
            return None
        chat = msg.get("chat") or {}
        user = msg.get("from") or {}
        chat_id = str(chat.get("id") or "unknown")
        msg_id = msg.get("message_id")
        if msg_id is None:
            return None
        ts = datetime.fromtimestamp(msg.get("date", 0), tz=UTC)
        text = msg.get("text") or msg.get("caption") or ""
        return CommunityEvent(
            event_id=f"telegram:{chat_id}:{msg_id}",
            source="telegram_bot",
            community_id=community_id,
            event_type=EventType.MESSAGE_EDITED
            if update.get("edited_message")
            else EventType.MESSAGE_CREATED,
            timestamp=ts,
            actor=Actor(
                id=f"telegram:{user.get('id', 'unknown')}",
                display_name=" ".join(
                    [str(user.get("first_name") or ""), str(user.get("last_name") or "")]
                ).strip()
                or user.get("username"),
                username=user.get("username"),
                is_bot=bool(user.get("is_bot")),
            ),
            space=Space(platform="telegram", chat_id=chat_id, chat_title=chat.get("title")),
            relation=Relation(
                reply_to_event_id=f"telegram:{chat_id}:{msg.get('reply_to_message', {}).get('message_id')}"
                if msg.get("reply_to_message")
                else None,
                reply_to_message_id=msg.get("reply_to_message", {}).get("message_id")
                if msg.get("reply_to_message")
                else None,
            ),
            content=Content(
                text=text,
                clean_text=" ".join(text.split()),
                has_link="http://" in text or "https://" in text,
            ),
        )


async def collect_long_polling(token: str, community_id: str, out_jsonl: str) -> None:
    """Minimal aiogram-based collector.

    Kept as optional because aiogram is an extra dependency.
    """
    try:
        from aiogram import Bot, Dispatcher, types
    except ImportError as exc:
        raise RuntimeError("Install bot extra: uv sync --extra bot") from exc

    from pathlib import Path

    from community_garden.utils import append_jsonl

    bot = Bot(token=token)
    dp = Dispatcher()

    @dp.message()
    async def on_message(message: types.Message) -> None:
        update = {"message": message.model_dump(mode="json")}
        event = TelegramBotAdapter.update_to_event(update, community_id)
        if event:
            append_jsonl(Path(out_jsonl), [event])

    await dp.start_polling(
        bot,
        allowed_updates=[
            "message",
            "edited_message",
            "chat_member",
            "message_reaction",
            "message_reaction_count",
        ],
    )

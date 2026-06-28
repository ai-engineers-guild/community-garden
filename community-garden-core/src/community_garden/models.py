from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class EventType(StrEnum):
    MESSAGE_CREATED = "message_created"
    MESSAGE_EDITED = "message_edited"
    REACTION_ADDED = "reaction_added"
    REACTION_REMOVED = "reaction_removed"
    MEMBER_JOINED = "member_joined"
    MEMBER_LEFT = "member_left"
    ADMIN_ACTION = "admin_action"
    TOPIC_CREATED = "topic_created"
    MESSAGE_DELETED = "message_deleted"
    RULE_CHANGED = "rule_changed"
    UNKNOWN = "unknown"


class Actor(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: str
    display_name: str | None = None
    username: str | None = None
    is_admin: bool = False
    is_bot: bool = False
    raw: dict[str, Any] = Field(default_factory=dict)


class Space(BaseModel):
    model_config = ConfigDict(extra="allow")

    platform: str
    chat_id: str | None = None
    chat_title: str | None = None
    topic_id: str | None = None
    topic_name: str | None = None


class Relation(BaseModel):
    model_config = ConfigDict(extra="allow")

    reply_to_event_id: str | None = None
    reply_to_message_id: str | int | None = None
    mentions: list[str] = Field(default_factory=list)
    forwarded_from: str | None = None


class Content(BaseModel):
    model_config = ConfigDict(extra="allow")

    text: str | None = None
    clean_text: str | None = None
    language: str | None = None
    has_link: bool = False
    has_media: bool = False
    media_type: str | None = None
    entities: list[dict[str, Any]] = Field(default_factory=list)


class Engagement(BaseModel):
    model_config = ConfigDict(extra="allow")

    reactions: list[dict[str, Any]] = Field(default_factory=list)
    reply_count: int | None = None


class RawRef(BaseModel):
    model_config = ConfigDict(extra="allow")

    file: str | None = None
    message_id: str | int | None = None
    source_record: dict[str, Any] = Field(default_factory=dict)


class CommunityEvent(BaseModel):
    model_config = ConfigDict(extra="allow")

    event_id: str
    source: str
    community_id: str
    event_type: EventType = EventType.UNKNOWN
    timestamp: datetime
    actor: Actor | None = None
    space: Space
    relation: Relation = Field(default_factory=Relation)
    content: Content = Field(default_factory=Content)
    engagement: Engagement = Field(default_factory=Engagement)
    raw_ref: RawRef = Field(default_factory=RawRef)


class CommunityConfig(BaseModel):
    community_id: str
    name: str
    timezone: str = "UTC"
    platform: str | None = None
    member_count_snapshot: int | None = None
    admins: list[str] = Field(default_factory=list)
    created_at: str | None = None


class Period(str):
    pass


class MetricValue(BaseModel):
    value: float | int | str | None
    source: Literal["deterministic", "semantic", "mixed", "manual"] = "deterministic"
    confidence: float | None = None
    description: str | None = None


class EvidenceRef(BaseModel):
    id: str
    kind: str = "event"
    note: str | None = None


class Finding(BaseModel):
    id: str
    title: str
    severity: Literal["info", "low", "medium", "high", "critical"] = "info"
    confidence: float = 0.5
    summary: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class Recommendation(BaseModel):
    id: str
    priority: Literal["low", "medium", "high", "critical"] = "medium"
    action: str
    reason: str
    expected_effect: str | None = None
    success_metric: str | None = None
    risk: str | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)

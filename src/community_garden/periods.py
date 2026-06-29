from __future__ import annotations

from datetime import UTC, datetime, timedelta


def iso_week_period(dt: datetime) -> str:
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"


def month_period(dt: datetime) -> str:
    return f"{dt.year}-{dt.month:02d}"


def event_day(dt: datetime) -> str:
    return dt.date().isoformat()


def normalize_period(period: str | None, now: datetime | None = None) -> str:
    now = now or datetime.now(UTC)
    if not period or period in {"current-week", "this-week"}:
        return iso_week_period(now)
    if period == "last-week":
        return iso_week_period(now - timedelta(days=7))
    if period in {"current-month", "this-month"}:
        return month_period(now)
    if period == "last-month":
        first = now.replace(day=1)
        return month_period(first - timedelta(days=1))
    return period


def event_in_period(dt: datetime, period: str) -> bool:
    if "-W" in period:
        return iso_week_period(dt) == period
    if len(period) == 7:
        return month_period(dt) == period
    if len(period) == 10:
        return event_day(dt) == period
    return True

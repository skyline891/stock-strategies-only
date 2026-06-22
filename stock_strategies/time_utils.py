"""Time helpers for Taiwan-market reports."""
from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo


TAIWAN_TZ = ZoneInfo("Asia/Taipei")


def taiwan_now(now: datetime | None = None) -> datetime:
    """Return an aware datetime in Asia/Taipei."""
    if now is None:
        return datetime.now(TAIWAN_TZ)
    if now.tzinfo is None:
        return now.replace(tzinfo=TAIWAN_TZ)
    return now.astimezone(TAIWAN_TZ)


def taiwan_date_str(now: datetime | None = None) -> str:
    return taiwan_now(now).strftime("%Y-%m-%d")


def taiwan_iso(now: datetime | None = None) -> str:
    return taiwan_now(now).isoformat(timespec="seconds")

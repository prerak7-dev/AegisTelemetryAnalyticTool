from __future__ import annotations

from datetime import datetime, timezone

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def parse_time(value: str) -> datetime:
    if value.endswith("Z"):
        value = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)

def floor_window(dt: datetime, window_seconds: int) -> datetime:
    ts = int(dt.timestamp())
    floored = ts - (ts % window_seconds)
    return datetime.fromtimestamp(floored, tz=timezone.utc)

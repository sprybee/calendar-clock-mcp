"""Read-only calendar tools; no network, credentials or persistent state."""

import math
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("calendar-clock-mcp", stateless_http=True, port=9000)


def _zone(name: str) -> ZoneInfo:
    if not name or len(name) > 100:
        raise ValueError("timezone must be a nonempty IANA name, e.g. Asia/Shanghai")
    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise ValueError(f"Unknown IANA timezone: {name}") from None


def _day(value: str) -> date:
    if len(value) != 10:
        raise ValueError("Dates must use YYYY-MM-DD")
    return date.fromisoformat(value)


@mcp.tool()
def convert_timezone(iso_datetime: str, target_timezone: str) -> dict:
    """Convert an ISO 8601 datetime with an explicit UTC offset to an IANA timezone.

    Rejects naive datetimes to avoid ambiguous or nonexistent local times at DST
    transitions. Example: 2026-01-01T00:00:00+00:00, Asia/Shanghai. Read-only.
    """
    value = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Datetime must include an explicit offset or Z")
    result = value.astimezone(_zone(target_timezone))
    return {"datetime": result.isoformat(), "timezone": target_timezone,
            "utc_offset_seconds": int(result.utcoffset().total_seconds()),
            "fold": result.fold}


@mcp.tool()
def date_difference(start_date: str, end_date: str) -> dict:
    """Return signed calendar-day difference between YYYY-MM-DD dates (end minus start).

    Same date is zero; reversing dates makes the result negative. Read-only.
    """
    days = (_day(end_date) - _day(start_date)).days
    return {"days": days, "absolute_days": abs(days)}


@mcp.tool()
def count_business_days(start_date: str, end_date: str, holidays: list[str] | None = None) -> dict:
    """Count Monday-Friday days in [start_date, end_date), excluding explicit holidays.

    Dates use YYYY-MM-DD. Start must not exceed end; maximum span is 36600 days
    and maximum holiday entries is 1000. Does not infer national holiday calendars
    or compensatory weekend workdays. Duplicate holidays are counted once. Read-only.
    """
    start, end = _day(start_date), _day(end_date)
    days = (end - start).days
    if not 0 <= days <= 36600:
        raise ValueError("Range must be nonnegative and no longer than 36600 days")
    if holidays is not None and len(holidays) > 1000:
        raise ValueError("At most 1000 holiday entries are allowed")
    excluded = {_day(value) for value in holidays or []}
    weeks, remainder = divmod(days, 7)
    count = weeks * 5 + sum((start.weekday() + i) % 7 < 5 for i in range(remainder))
    removed = sum(start <= holiday < end and holiday.weekday() < 5 for holiday in excluded)
    return {"business_days": count - removed, "excluded_weekday_holidays": removed,
            "calendar_days": days, "interval": "[start_date, end_date)"}


@mcp.tool()
def unix_timestamp_to_datetime(timestamp: float, target_timezone: str = "UTC") -> dict:
    """Convert Unix seconds (not milliseconds) to an ISO datetime in an IANA timezone.

    Supports fractional seconds and negative values within Python's datetime range.
    Read-only; does not consult the current clock.
    """
    if not math.isfinite(timestamp):
        raise ValueError("Timestamp must be finite Unix seconds")
    try:
        value = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=timestamp)
        result = value.astimezone(_zone(target_timezone))
    except (OverflowError, OSError):
        raise ValueError("Timestamp is outside the supported datetime range") from None
    return {"datetime": result.isoformat(), "timezone": target_timezone, "unix_seconds": timestamp}


@mcp.tool()
def date_to_unix_timestamp(iso_datetime: str) -> dict:
    """Convert an ISO 8601 datetime with explicit UTC offset or Z to Unix seconds.

    Naive datetimes are rejected, so results do not depend on server timezone. Read-only.
    """
    value = datetime.fromisoformat(iso_datetime.replace("Z", "+00:00"))
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("Datetime must include an explicit offset or Z")
    return {"unix_seconds": value.timestamp(),
            "utc_datetime": value.astimezone(timezone.utc).isoformat()}

from calendar_clock_mcp.server import (
    count_business_days,
    date_difference,
    date_to_unix_timestamp,
    unix_timestamp_to_datetime,
)


def test_date_difference():
    assert date_difference("2026-01-01", "2026-01-10") == {"days": 9, "absolute_days": 9}


def test_business_days_exclude_holiday():
    result = count_business_days("2026-01-05", "2026-01-12", ["2026-01-07"])
    assert result["business_days"] == 4
    assert result["excluded_weekday_holidays"] == 1


def test_timestamp_round_trip():
    result = unix_timestamp_to_datetime(0, "UTC")
    assert result["datetime"].startswith("1970-01-01T00:00:00")
    assert date_to_unix_timestamp("1970-01-01T00:00:00Z")["unix_seconds"] == 0

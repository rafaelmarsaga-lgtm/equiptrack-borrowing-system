from datetime import date, datetime, timezone

from app.timeutil import now_ph, today_ph, utcnow


def test_today_ph_is_next_day_after_1600_utc():
    # 17:00 UTC on Oct 1 is already 01:00 on Oct 2 in the Philippines (UTC+8)
    fake_now = datetime(2026, 10, 1, 17, 0, tzinfo=timezone.utc)
    assert today_ph(fake_now) == date(2026, 10, 2)


def test_today_ph_same_day_before_1600_utc():
    fake_now = datetime(2026, 10, 1, 15, 59, tzinfo=timezone.utc)
    assert today_ph(fake_now) == date(2026, 10, 1)


def test_now_ph_has_plus_8_offset():
    assert now_ph().utcoffset().total_seconds() == 8 * 3600


def test_utcnow_is_timezone_aware_utc():
    assert utcnow().utcoffset().total_seconds() == 0

from datetime import date, datetime, timedelta, timezone

# Philippine time is a fixed UTC+8 (no daylight saving), so a fixed offset is
# safe and avoids depending on timezone data being installed on the host.
PH_TZ = timezone(timedelta(hours=8))


def utcnow() -> datetime:
    """Timezone-aware UTC now (replaces the deprecated datetime.utcnow)."""
    return datetime.now(timezone.utc)


def now_ph(now: datetime | None = None) -> datetime:
    """Current Philippine time. `now` can be injected so tests control the clock."""
    return (now or utcnow()).astimezone(PH_TZ)


def today_ph(now: datetime | None = None) -> date:
    """'Today' for every business rule: due-date window, return date, Overdue."""
    return now_ph(now).date()

"""Business-hours arithmetic for the support SLA."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from .jalali import jalali_to_gregorian

TEHRAN_TZ = ZoneInfo("Asia/Tehran")
BUSINESS_START = time(9, 0)
BUSINESS_END = time(17, 0)
# Saturday (5), Sunday (6), Monday (0), Tuesday (1), Wednesday (2)
BUSINESS_WEEKDAYS = frozenset({5, 6, 0, 1, 2})

_JALALI_HOLIDAYS_1405: tuple[tuple[int, int, int], ...] = (
    (1405, 1, 1),
    (1405, 1, 2),
    (1405, 1, 3),
    (1405, 1, 4),
    (1405, 1, 12),
    (1405, 1, 13),
    (1405, 1, 25),
    (1405, 3, 7),
    (1405, 3, 14),
    (1405, 3, 15),
    (1405, 4, 5),
    (1405, 4, 6),
    (1405, 5, 15),
    (1405, 5, 23),
    (1405, 5, 25),
    (1405, 6, 1),
    (1405, 6, 10),
    (1405, 8, 24),
    (1405, 10, 3),
    (1405, 10, 17),
    (1405, 11, 5),
    (1405, 11, 22),
    (1405, 12, 10),
    (1405, 12, 20),
    (1405, 12, 21),
    (1405, 12, 29),
)

PUBLIC_HOLIDAYS: frozenset[date] = frozenset(
    jalali_to_gregorian(y, m, d) for y, m, d in _JALALI_HOLIDAYS_1405
)


def is_business_day(day: date | datetime) -> bool:
    d = day.date() if isinstance(day, datetime) else day
    return d.weekday() in BUSINESS_WEEKDAYS and d not in PUBLIC_HOLIDAYS


def business_hours_between(start: datetime, end: datetime) -> float:
    """Number of business hours in the half-open interval ``[start, end)``."""
    if end <= start:
        return 0.0

    start_tehran = start.astimezone(TEHRAN_TZ)
    end_tehran = end.astimezone(TEHRAN_TZ)

    total = timedelta(0)
    current_date = start_tehran.date()
    end_date = end_tehran.date()
    while current_date <= end_date:
        if is_business_day(current_date):
            opens = datetime.combine(current_date, BUSINESS_START, tzinfo=TEHRAN_TZ)
            closes = datetime.combine(current_date, BUSINESS_END, tzinfo=TEHRAN_TZ)
            lo = max(opens, start_tehran)
            hi = min(closes, end_tehran)
            if hi > lo:
                total += hi - lo
        current_date += timedelta(days=1)

    return total.total_seconds() / 3600.0

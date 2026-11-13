from __future__ import annotations

from datetime import datetime, timezone

from app.sla import TEHRAN_TZ, business_hours_between


def _utc(*args: int) -> datetime:
    return datetime(*args, tzinfo=timezone.utc)


def _tehran(*args: int) -> datetime:
    return datetime(*args, tzinfo=TEHRAN_TZ)


def test_business_hours_within_one_day() -> None:
    # Monday 2026-10-26, 10:00 -> 13:30 Tehran
    assert business_hours_between(_tehran(2026, 10, 26, 10, 0), _tehran(2026, 10, 26, 13, 30)) == 3.5


def test_business_hours_skip_iranian_weekend() -> None:
    # Wednesday 2026-10-21 16:00 Tehran -> Saturday 2026-10-24 10:00 Tehran
    # Thu (Oct 22) and Fri (Oct 23) are off: 1h on Wed + 1h on Sat = 2.0h
    start = _tehran(2026, 10, 21, 16, 0)
    end = _tehran(2026, 10, 24, 10, 0)
    assert business_hours_between(start, end) == 2.0


def test_business_hours_skip_public_holiday() -> None:
    # 1405/01/25 = 2026-04-14 (Tuesday) is a public holiday.
    # Mon 2026-04-13 16:00 Tehran -> Wed 2026-04-15 10:00 Tehran = 2.0h
    start = _tehran(2026, 4, 13, 16, 0)
    end = _tehran(2026, 4, 15, 10, 0)
    assert business_hours_between(start, end) == 2.0


def test_business_hours_empty_interval() -> None:
    t = _utc(2026, 10, 26, 10, 0)
    assert business_hours_between(t, t) == 0.0

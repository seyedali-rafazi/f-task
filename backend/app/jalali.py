"""Jalali (Persian) calendar conversion and Persian/Arabic digit normalization."""
from __future__ import annotations

from datetime import date

_DIGIT_TRANS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_digits(text: str) -> str:
    """Convert Persian and Arabic-Indic digits to ASCII digits."""
    return text.translate(_DIGIT_TRANS)


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> date:
    """Convert a Jalali (Solar Hijri) date to a Gregorian ``datetime.date``."""
    jy += 1595
    days = (
        -355668
        + (365 * jy)
        + ((jy // 33) * 8)
        + (((jy % 33) + 3) // 4)
        + jd
        + ((jm - 1) * 31 if jm < 7 else ((jm - 7) * 30) + 186)
    )
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    sal_a = [
        0,
        31,
        29 if (gy % 4 == 0 and gy % 100 != 0) or (gy % 400 == 0) else 28,
        31,
        30,
        31,
        30,
        31,
        31,
        30,
        31,
        30,
        31,
    ]
    gm = 0
    while gm < 13 and gd > sal_a[gm]:
        gd -= sal_a[gm]
        gm += 1
    return date(gy, gm, gd)

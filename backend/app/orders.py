"""Order reference extraction."""
from __future__ import annotations

import re

from .jalali import normalize_digits

ORDER_REF_PATTERN = re.compile(r"BZ-([0-9]+)", re.IGNORECASE)


def find_order_ref(text: str | None) -> str | None:
    """Return the first ``BZ-<digits>`` reference in ``text`` (upper-cased prefix, Latin digits)."""
    if not text:
        return None
    normalized = normalize_digits(text)
    match = ORDER_REF_PATTERN.search(normalized)
    if match is None:
        return None
    return f"BZ-{match.group(1)}"


def extract_order_ref(order_ref: str | None, body: str | None) -> str | None:
    """Prefer the explicit ``order_ref`` field; fall back to scanning the body."""
    return find_order_ref(order_ref) or find_order_ref(body)

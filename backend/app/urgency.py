"""Urgency rule for the support dashboard."""
from __future__ import annotations

from datetime import datetime

import pandas as pd

from .sla import business_hours_between


def is_urgent(
    severity: str,
    received_at: datetime,
    answered_at: datetime | None,
    now: datetime,
    sla_hours: float,
) -> bool:
    """A message is urgent when it is high severity, still unanswered at
    ``now``, and has waited at least ``sla_hours`` business hours.
    """
    if (severity or "").lower() != "high":
        return False
    if answered_at is not None and not pd.isna(answered_at) and answered_at <= now:
        return False
    return business_hours_between(received_at, now) >= sla_hours

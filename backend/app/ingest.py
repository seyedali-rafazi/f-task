"""Loading the support-system CSV export into a DataFrame."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from typing import IO

import pandas as pd

from .jalali import jalali_to_gregorian, normalize_digits
from .sla import TEHRAN_TZ

COLUMNS: list[str] = [
    "message_id",
    "customer_id",
    "channel",
    "received_at",
    "answered_at",
    "subject",
    "body",
    "order_ref",
    "severity_hint",
]

_JALALI_TS_RE = re.compile(
    r"^\s*(1[34]\d{2})[/\-](\d{1,2})[/\-](\d{1,2})(?:[T\s]+(\d{1,2}):(\d{2})(?::(\d{2}))?)?\s*$"
)


def _parse_single_timestamp(raw: str) -> pd.Timestamp:
    val = (raw or "").strip()
    if not val:
        return pd.NaT

    norm = normalize_digits(val)
    match = _JALALI_TS_RE.match(norm)
    if match:
        jy, jm, jd = int(match.group(1)), int(match.group(2)), int(match.group(3))
        hh = int(match.group(4) or 0)
        mm = int(match.group(5) or 0)
        ss = int(match.group(6) or 0)
        try:
            g_date = jalali_to_gregorian(jy, jm, jd)
            dt_tehran = datetime(g_date.year, g_date.month, g_date.day, hh, mm, ss, tzinfo=TEHRAN_TZ)
            return pd.Timestamp(dt_tehran.astimezone(timezone.utc))
        except ValueError:
            return pd.NaT

    try:
        ts = pd.to_datetime(norm, errors="coerce", utc=True, format="ISO8601")
    except Exception:
        return pd.NaT
    if pd.isna(ts):
        ts = pd.to_datetime(norm, errors="coerce", utc=True)
    return ts


def parse_timestamps(values: pd.Series) -> pd.Series:
    """Parse export timestamps (ISO-8601 UTC or Jalali Tehran time) into tz-aware UTC values."""
    parsed = [_parse_single_timestamp(v) for v in values]
    return pd.to_datetime(parsed, errors="coerce", utc=True)


def load_messages(source: str | Path | IO[bytes] | IO[str]) -> pd.DataFrame:
    """Read a support export and return one row per message, in file order."""
    df = pd.read_csv(source, dtype=str, keep_default_na=False)

    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"export is missing columns: {', '.join(missing)}")

    df = df[COLUMNS].fillna("")
    for col in ("message_id", "customer_id", "channel", "order_ref", "severity_hint"):
        df[col] = df[col].str.strip()
    df["severity_hint"] = df["severity_hint"].str.lower()

    df = df[df["message_id"] != ""]

    df["received_at"] = parse_timestamps(df["received_at"])
    df["answered_at"] = parse_timestamps(df["answered_at"])

    # discard malformed rows
    df = df.dropna(subset=["received_at"])

    return df.reset_index(drop=True)

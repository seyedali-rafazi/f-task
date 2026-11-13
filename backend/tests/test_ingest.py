from __future__ import annotations

from pathlib import Path

import pandas as pd

from app.ingest import load_messages


def test_loads_all_clean_rows(sample_csv: Path) -> None:
    df = load_messages(sample_csv)
    assert list(df["message_id"]) == ["M001", "M002", "M003", "M004"]
    assert "does not work" in df.loc[3, "body"]


def test_iso_timestamps_are_utc(sample_csv: Path) -> None:
    df = load_messages(sample_csv)
    assert df.loc[0, "received_at"] == pd.Timestamp("2026-10-26T08:00:00Z")
    assert str(df["received_at"].dt.tz) == "UTC"
    assert pd.isna(df.loc[1, "answered_at"])


def test_jalali_timestamps_parsed_as_tehran_to_utc(tmp_path: Path) -> None:
    csv_file = tmp_path / "jalali.csv"
    csv_file.write_text(
        "message_id,customer_id,channel,received_at,answered_at,subject,body,order_ref,severity_hint\n"
        "M1,C1,app,1405/06/01 23:20,۱۴۰۵/۰۵/۲۳ ۱۱:۵۲,sub,body,,low\n",
        encoding="utf-8",
    )
    df = load_messages(csv_file)
    assert len(df) == 1
    # 1405/06/01 = 2026-08-23; 23:20 Tehran (UTC+03:30) = 19:50 UTC
    assert df.loc[0, "received_at"] == pd.Timestamp("2026-08-23T19:50:00Z")
    # 1405/05/23 = 2026-08-14; 11:52 Tehran (UTC+03:30) = 08:22 UTC
    assert df.loc[0, "answered_at"] == pd.Timestamp("2026-08-14T08:22:00Z")

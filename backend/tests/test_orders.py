from __future__ import annotations

from app.orders import extract_order_ref


def test_order_ref_from_field() -> None:
    assert extract_order_ref("BZ-48219", "") == "BZ-48219"


def test_order_ref_from_body_when_field_empty() -> None:
    assert extract_order_ref("", "my order bz-77310 is late") == "BZ-77310"
    assert extract_order_ref("", "no order mentioned") is None


def test_order_ref_persian_and_arabic_digits() -> None:
    assert extract_order_ref("BZ-۴۱۸۱۹۱", "") == "BZ-418191"
    assert extract_order_ref("", "سفارش BZ-٢٧٩٥٥٥ نرسیده") == "BZ-279555"

from __future__ import annotations

from fastapi.testclient import TestClient

from app.api import app
from app.classify import classify_keywords, classify_severity_keywords
from app.drafts import detect_language, validate_draft

client = TestClient(app)


def test_severity_keywords_catch_real_high_issues() -> None:
    assert classify_severity_keywords("Double charge", "1,250,000 toman was deducted twice") == "high"
    assert classify_severity_keywords("Wallet", "Wallet balance gone after login I did not make") == "high"
    assert classify_severity_keywords("peyk", "status shode delivered ama man tahvil nagereftam") == "high"
    assert classify_severity_keywords("خطر", "دستگاه جرقه زد و دود می‌دهد") == "high"
    assert classify_severity_keywords("خیلی ناراضیم!!!", "پیک سلام نکرد و بی‌ادب بود!!!") != "high"
    assert classify_severity_keywords("کارت هدیه", "چطور کارت هدیه را وارد کنم؟") != "high"


def test_keywords_normalize_arabic_chars() -> None:
    assert classify_keywords("كارت هديه", "چطور پرداخت كنم") == "payment"


def test_detect_language() -> None:
    assert detect_language("سلام", "سفارش من نرسیده") == "fa"
    assert detect_language("", "salam, pool sefaresh BZ-644379 do bar az hesabam kam shode") == "fa"
    assert detect_language("Double charge", "1,250,000 toman was deducted twice") == "en"
    assert detect_language("Where is my order", "It has not arrived") == "en"


def test_validate_draft_blocks_unsafe_promises() -> None:
    assert validate_draft("We are checking your order and will update you soon.") == []
    assert validate_draft("We will refund your money tomorrow.") != []
    assert validate_draft("مبلغ 50000 تومان تا فردا واریز خواهد شد.") != []
    assert validate_draft("BLOCKED") != []


def test_draft_endpoint_returns_200_blocked_when_llm_unavailable() -> None:
    resp = client.post(
        "/api/draft",
        json={
            "message_id": "M_TEST_1",
            "customer_id": "C1",
            "subject": "Double charge",
            "body": "Charged twice",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["message_id"] == "M_TEST_1"
    assert data["blocked"] is True
    assert data["draft"] == ""
    assert data["language"] == "en"
    assert len(data["warnings"]) > 0

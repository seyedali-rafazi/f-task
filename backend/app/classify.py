"""Category and severity classification: LLM when configured, keyword rules otherwise."""
from __future__ import annotations

import re

import pandas as pd

from .config import Settings
from .llm import LLMClient, MessageToClassify

_ARABIC_CHARS = str.maketrans("كيى", "کیی")


def _norm(text: str) -> str:
    return text.translate(_ARABIC_CHARS).lower()


KEYWORDS: dict[str, tuple[str, ...]] = {
    "refund": (
        "refund", "money back", "bargasht", "pas bedid", "pas begiram",
        "مرجوع", "بازگشت وجه", "برگشت پول", "پول برنگشته", "استرداد", "عودت", "پولم رو پس",
    ),
    "payment": (
        "payment", "paid", "charged", "double charge", "deducted", "card", "wallet",
        "invoice", "factor", "pardakht", "sharj", "pool", "pul",
        "پرداخت", "برداشت", "کارت", "کیف پول", "فاکتور", "تراکنش", "درگاه", "کم شده", "دوبار",
    ),
    "delivery": (
        "delivery", "deliver", "arrive", "arrived", "shipping", "courier", "tracking",
        "package", "parcel", "tahvil", "ersal", "post", "peyk", "nayomad",
        "ارسال", "تحویل", "مرسوله", "پیک", "بسته", "پست", "کد رهگیری", "نرسیده",
    ),
    "product_quality": (
        "broken", "damaged", "defective", "quality", "fake", "not working", "wrong item",
        "different item", "manual", "install", "colour", "color", "kharab", "rang", "taviz",
        "spark", "smoke", "shock", "burn", "danger", "hazard", "leak", "fire",
        "خراب", "شکسته", "کیفیت", "معیوب", "تقلبی", "کار نمی", "رنگ", "لک", "راهنما",
        "نصب", "مشخصات", "تعویض", "بو ", "جرقه", "دود", "آتش", "برق گرفت", "خطرناک", "سوخت",
    ),
    "account": (
        "account", "password", "login", "log in", "sign in", "otp", "hesab", "ramz",
        "hack", "unknown access", "unauthorized",
        "حساب", "رمز", "ورود", "پسورد", "کد تایید", "شماره موبایل", "شخص دیگری", "هک",
    ),
}

CATEGORY_ORDER: tuple[str, ...] = ("refund", "payment", "account", "product_quality", "delivery")

_HIGH_SEVERITY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(p, re.IGNORECASE)
    for p in (
        # Double charge / money taken twice / wallet balance stolen/gone
        r"(charged\s+twice|double\s+charge|deducted\s+twice|taken\s+twice|dobar\s+.*kam|do\s+bar\s+.*kam|دوبار\s+.*کم|دو\s*بار\s+.*کم|دو\s*بار\s+برداشت|دوبار\s+برداشت)",
        r"(wallet\s+balance\s+gone|money\s+disappeared|موجودی.*خالی|موجودی.*پاک|پول.*ناپدید)",
        # Unauthorized account access / takeover
        r"(unknown\s+access|someone\s+else.*account|login\s+i\s+did\s+not\s+make|hacked|account\s+takeover|شخص\s+دیگری.*حساب|بدون\s+اطلاع\s+من\s+عوض|ورود\s+غیرمجاز|کنترل\s+حساب|هک\s+شد)",
        # Parcel marked delivered but never arrived
        r"((marked|status|وضعیت|زده|ثبت\s+شده).{0,40}(delivered|تحویل\s+(شده|داده\s+شده)).{0,60}(never|not|نرسید|تحویل\s+نگرفت|نیومد|nayomad|naresid|tahvil\s+nagereft)|(nayomad|نرسید|تحویل\s+نگرفت).{0,60}(delivered|تحویل\s+(شده|داده\s+شده)))",
        # Dangerous / hazardous product
        r"(spark|smoke|electric\s*shock|caught\s+fire|burn(ed|ing)?|explode|toxic|poison|hazardous|dangerous|جرقه|دود\s+می|آتش\s+گرفت|برق\s*گرفت|خطرناک|مسموم|سوختگی|انفجار|نشت\s+گاز|نشتی\s+سمی)",
    )
)


def classify_keywords(subject: str, body: str) -> str:
    text = _norm(f"{subject} {body}")
    for category in CATEGORY_ORDER:
        if any(word in text for word in KEYWORDS[category]):
            return category
    return "other"


def classify_severity_keywords(subject: str, body: str) -> str:
    text = _norm(f"{subject} {body}")
    if any(pat.search(text) for pat in _HIGH_SEVERITY_PATTERNS):
        return "high"
    return "medium"


def classify_messages(df: pd.DataFrame, settings: Settings) -> tuple[pd.Series, pd.Series]:
    """Return ``(categories, severities)`` Series aligned to ``df``."""
    kw_cats = [classify_keywords(s, b) for s, b in zip(df["subject"], df["body"])]
    kw_sevs = [classify_severity_keywords(s, b) for s, b in zip(df["subject"], df["body"])]

    if not settings.llm_base_url:
        return (
            pd.Series(kw_cats, index=df.index, dtype=object),
            pd.Series(kw_sevs, index=df.index, dtype=object),
        )

    client = LLMClient(settings)
    batch = [
        MessageToClassify(message_id=m, subject=s, body=b)
        for m, s, b in zip(df["message_id"], df["subject"], df["body"])
    ]
    results = client.classify(batch)

    cats = [
        results[m].category if m in results else fb
        for m, fb in zip(df["message_id"], kw_cats)
    ]
    sevs = [
        results[m].severity if m in results else fb
        for m, fb in zip(df["message_id"], kw_sevs)
    ]
    return (
        pd.Series(cats, index=df.index, dtype=object),
        pd.Series(sevs, index=df.index, dtype=object),
    )

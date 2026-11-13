"""Runtime configuration, read from environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

CATEGORIES: tuple[str, ...] = (
    "delivery",
    "payment",
    "refund",
    "product_quality",
    "account",
    "other",
)


@dataclass(frozen=True)
class Settings:
    urgent_sla_business_hours: float
    llm_base_url: str | None
    llm_api_key: str | None
    llm_model: str
    llm_timeout_seconds: float


def _optional(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def _load_dotenv_if_needed() -> None:
    if "PYTEST_CURRENT_TEST" in os.environ:
        return
    for candidate in (Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"):
        if candidate.is_file():
            for line in candidate.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and k not in os.environ:
                    os.environ[k] = v
            break


def get_settings() -> Settings:
    _load_dotenv_if_needed()
    return Settings(
        urgent_sla_business_hours=float(os.environ.get("URGENT_SLA_BUSINESS_HOURS", "2")),
        llm_base_url=_optional("LLM_BASE_URL"),
        llm_api_key=_optional("LLM_API_KEY"),
        llm_model=os.environ.get("LLM_MODEL", "").strip() or "gpt-4o-mini",
        llm_timeout_seconds=float(os.environ.get("LLM_TIMEOUT_SECONDS", "30")),
    )

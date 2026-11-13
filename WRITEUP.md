# Bazarcheh Support Dashboard — Writeup

## 1. The Real Problem
Sara needs reliable daily triage numbers and a live, Persian RTL workspace that surfaces every unanswered high-severity issue (both overdue and approaching the 2-business-hour promise) without burning LLM quota or letting untrusted customer text produce unsafe replies.

## 2. Assumptions
- Jalali timestamps in CSV exports (`YYYY/MM/DD HH:MM`) represent `Asia/Tehran` local time and are converted to UTC on ingest.
- Messages with Persian/Arabic script should receive Persian (`fa`) draft replies; Latin-only messages receive English (`en`) drafts.
- Keyword rules serve as the deterministic fallback when `LLM_BASE_URL` is not configured or a batch fails, while `LLM_BASE_URL` can be plugged in via `.env` for production classification and drafting.

## 3. Bugs Found in the Existing Code (and How We Found Them)
- **Wrong calendar & SLA (`backend/app/sla.py`, `docker-compose.yml`):** Reading `sla.py` and `test_sla.py` showed `BUSINESS_WEEKDAYS = {0,1,2,3,4}` (Mon–Fri) in `UTC` with no holidays, and `docker-compose.yml` overrode `URGENT_SLA_BUSINESS_HOURS` to `"24"` instead of `"2"`. Fixed to Sat–Wed, `09:00–17:00 Asia/Tehran`, plus all 26 official 1405 holidays.
- **Jalali timestamps dropped/misread (`backend/app/ingest.py`):** Inspecting `messages_sample.csv` and `eval_messages.csv` revealed ~5% of `received_at` (35/652 and 18/332) and `answered_at` values are Jalali dates (e.g. `۱۴۰۵/۰۵/۲۳ ۱۱:۵۲`). Strict `ISO8601` parsing coerced them to `NaT`, dropping rows or marking answered tickets as unanswered. Added `jalali.py` and Tehran-to-UTC parsing.
- **Unreliable `severity_hint` (`backend/app/urgency.py`):** Inspecting `eval_messages.csv` showed double-charge and unauthorized-wallet-drain messages labeled `low`, while polite gift-card questions were labeled `high`. Stopped trusting `severity_hint` and moved severity detection into `classify.py` / `llm.py`.
- **Persian/Arabic digits & chars (`backend/app/orders.py`, `backend/app/dedup.py`):** Real rows used Persian (`BZ-۴۱۸۱۹۱`) and Arabic-Indic (`BZ-٢٧٩٥٥٥`) digits and Arabic `ك`/`ي`. Normalized digits and Arabic letters.
- **Quota burn & unsafe drafts (`backend/app/api.py`, `backend/app/drafts.py`, `backend/app/llm.py`):** `/api/analyze` called `prefetch_drafts=True` on upload, and `classify` sent 1 HTTP request per message. Removed prefetching, batched classification (`batch_size=20`), and added `/api/draft` safety guards.
- **Frontend gaps & XSS (`frontend/src/`):** Page was English/LTR, `AttentionList` only showed already-overdue IDs using wall-clock time, `draft-text` was a `<div>` instead of `<textarea>`, `draft-approve`/`draft-warning` were missing, and `MessagesTable` used `dangerouslySetInnerHTML` on untrusted message bodies. Fixed all of these, added live 30s browser-clock updates, and bundled `Vazirmatn` locally.
- **Docker Alpine build (`frontend/Dockerfile`):** `npm ci` failed with missing `@rollup/rollup-linux-x64-musl` (`npm/cli#4828`); switched container install to clean `npm install`.

## 4. What Was Cut and Why
- **External Jalali date-picker widget:** Left the manual `"Now"` override input as standard `datetime-local` (with Persian `fa-IR` date formatting in tables/lists) to keep QA automation compatible within the 4-hour scope.

## 5. Where AI Misled Us
- Initial starter tests (`test_sla.py`) and comments (`urgency.py`: *"severity_hint is reliable"*) encoded wrong assumptions that passed all starter unit tests until checked against actual CSV rows.
- Early regexes for delivered-not-received missed Finglish word order (`peyk nayomade o status shode delivered`), caught by writing explicit unit tests.

## 6. How We Know Classification & SLA Are Good Enough
- **22/22 backend tests** (`pytest`) and **7/7 frontend tests** (`vitest`) pass, including new tests for Jalali parsing, 1405 holidays, Persian/Arabic order refs, real high-severity detection, and safe draft blocking.
- Verified on `messages_sample.csv` (all 652 rows loaded, 44 duplicates caught, 608 unique) and `eval_messages.csv` (all 332 rows loaded, 310 unique, 5 urgent at `2026-04-15T07:00:00Z` using `qwen/qwen3.8-27b`).

## 7. How We Made AI-Written Replies Safe
- Customer subject/body are wrapped in `<untrusted_customer_message>` tags with explicit system instructions to ignore embedded commands.
- System prompt forbids promising money, refunds, compensation, amounts, or dates/deadlines.
- Post-generation `validate_draft()` regexes catch and block any slipped refund promises, currency amounts, or timeframes, returning HTTP `200` with `blocked: true` (and also on LLM timeout/unavailability).

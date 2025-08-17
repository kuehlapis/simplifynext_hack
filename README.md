# Tenant Rights Copilot (Singapore)
*Agentic AI that reads a residential tenancy agreement, flags risky/illegal clauses with citations, drafts a negotiation rider/email, and builds a dated action plan with calendar exports — using **Gemini API** + **LangChain/LangGraph** + **Supabase**. No application code in this README.*

---

## Why this exists
Singapore rentals are contract-heavy and time-bound (e.g., stamp duty deadlines). Tenants routinely miss critical items or accept one-sided clauses. This project ships an **agentic** workflow that: **plans**, **acts**, and **produces artifacts** (letter/rider + ICS), not just chat.

---

## What you get in 2 weeks (MVP)
- **Lease ingestion** (PDF/photos) → OCR → normalized text with page/line anchors.
- **Clause extraction** into a structured map (deposit, minor repairs, diplomatic/break, entry/inspection, subletting, occupancy, renewal, stamp duty responsibility, etc.).
- **Deterministic SG rule checks** driven by a YAML rulebook:
  - Stamp duty: who pays (contractual vs typical practice), when to stamp (14/30-day rule), computation preview (show formula basis without guaranteeing rates).
  - HDB path (when applicable): minimum tenancy, occupancy caps, approvals/notifications.
  - Private residential norms (based on CEA template patterns): unrelated occupier cap, viewing notice expectations, presence/shape of diplomatic clause, minor repairs cap pattern.
- **Explainability**: each flag shows the rule, rationale, evidence span, and non-binding reference link text.
- **Agentic plan**: generates dated tasks (e-stamp deadline, inspection window, notice windows) and exports **.ics**.
- **Drafts**: negotiation email + rider (with concrete clause edits); user can adjust tone (firm/courteous/neutral).
- **No legal advice**: informational tool with transparent sources and limitations.

> **Skeptical note:** Singapore tenancy practice is partly customary and depends on contract specifics. The rulebook **must** distinguish “mandatory requirement” vs “industry norm” and always surface sources. Do not hard-code rates or caps without verifying your rulebook content.

---

## Non-goals (MVP)
- No live scraping of gov websites.
- No fully automated e-stamping or submission to authorities.
- No multi-jurisdiction support beyond SG (HDB/private branches only).
- No guarantee of legal correctness; this is not a law practice tool.

---

## Tech at a glance
- **Reasoning & generation:** Gemini API (recommend: 1.5 Flash for speed, 1.5 Pro for drafting quality).
- **Orchestration:** LangChain + **LangGraph** (tool-using graph with retries & guardrails).
- **Storage:** **Supabase** (Postgres + pgvector; object storage optional).
- **OCR:** Tesseract/PaddleOCR locally; optionally compare with Gemini multimodal on small test sets for robustness.
- **Exports:** ICS file for tasks; annotated PDF with highlights/notes.

---

## Quickstart (developer workflow)
> This section intentionally avoids app code; it lists the minimum you must configure.

### Prerequisites
- Gemini API key.
- Supabase project with Postgres (pgvector enabled).
- OCR runtime (e.g., `tesseract` installed).
- A curated **Rulebook YAML** for SG (see below).
- A small dataset of sanitized tenancy agreements (PDF/images).

### Environment configuration
Set the following environment variables (names are suggestions; adapt to your runner/secret store):
- `GEMINI_API_KEY`
- `SUPABASE_URL`, `SUPABASE_ANON_KEY` (for client) and/or `SUPABASE_SERVICE_ROLE_KEY` (for server jobs)
- `SUPABASE_JWT_SECRET` (if you gate a simple admin UI)
- `SUPABASE_DB_SCHEMA` (default `public`)
- `SUPABASE_BUCKET` (for uploaded files)
- `OCR_ENGINE` = `tesseract` or `paddleocr`
- `MODEL_GENERATION` = `gemini-1.5-pro` (drafting)
- `MODEL_EXTRACTION` = `gemini-1.5-flash` (cheap extraction) or use local heuristics
- `EMBEDDINGS_MODEL` = a locally runnable sentence transformer or Gemini embeddings (if allowed)
- `HDB_MODE_DEFAULT` = `false` (user toggles per document)

### Supabase data model (conceptual)
*(Describe in Supabase Studio; no SQL provided here.)*
- **documents**: id, filename, mime, pages, sha256, created_at, uploaded_by
- **chunks**: id, document_id (fk), page, text, span_start, span_end, embedding (vector)
- **clauses**: id, document_id (fk), clause_type, tex

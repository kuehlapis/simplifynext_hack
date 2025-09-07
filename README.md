# Tenant Rights Copilot (Singapore)
*Agentic AI that reads a residential tenancy agreement, flags risky/illegal clauses with citations, drafts a negotiation rider/email, and builds a dated action plan with calendar exports — using **Gemini API** + **LangChain/LangGraph**. No application code in this README.*

---

## Why this exists
Singapore rentals are contract-heavy and time-bound (e.g., stamp duty deadlines). Tenants routinely miss critical items or accept one-sided clauses. This project ships an **agentic** workflow that: **plans**, **acts**, and **produces artifacts** (letter/rider + ICS), not just chat.

---

## Features
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

## Tech at a glance
- **Reasoning & generation:** Gemini API
- **Orchestration:** LangChain + **LangGraph** (tool-using graph with retries & guardrails).
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
- `OCR_ENGINE` = `tesseract` or `paddleocr`
- `MODEL_GENERATION` = `gemini-1.5-pro` (drafting)
- `MODEL_EXTRACTION` = `gemini-1.5-flash` (cheap extraction) or use local heuristics
- `EMBEDDINGS_MODEL` = a locally runnable sentence transformer or Gemini embeddings (if allowed)
- `HDB_MODE_DEFAULT` = `false` (user toggles per document)


## 1. Problem Statement & Tenant Pain Points

| Pain Point | Description | Impact | Copilot Response |
|------------|-------------|--------|------------------|
| Hidden one‑sided clauses | Repair caps, landlord entry, deposit forfeiture wording | Financial / privacy risk | Structured clause extraction + risk labeling |
| Missed statutory / procedural deadlines | Stamp duty window, diplomatic notice periods | Penalties / reduced options | Dated task plan + calendar export |
| Difficulty negotiating | Unsure how to rephrase vs delete | Weaker bargaining position | Draft rider + email with neutral / firm tones |
| Lack of transparency | Black-box “AI says so” | Low trust | Each flag shows rule, evidence span, source |
| Over-reliance on custom / anecdotal norms | Confusing difference: law vs practice | Misprioritization | Rule severity categories + classification tags |
| Manual, repetitive review | Time-consuming document scanning | Slower decision cycle | OCR → structured normalization + agents |
| Uncertain data handling | Private rental info | Privacy risk | Minimal PII persistence + hashed doc tracking |

---

## 2. Functional Requirements

### 2.1 Core (MVP)
1. Document Ingestion
   - Accept PDF or image set.
   - OCR with page + line anchor retention.
   - Compute SHA256 & deduplicate.
2. Clause Extraction
   - Segment into typed clauses (deposit, repairs, termination, diplomatic, access, renewal, subletting, occupancy, dispute resolution, governing law, stamp duty responsibility).
   - Store span indices & page references.
3. Rule Evaluation
   - Deterministic YAML rulebook executed against structured clauses / heuristics.
   - Severity taxonomy: ILLEGAL (if any), NON_COMPLIANT (procedural), RISKY_NORM_DEVIATION, UNUSUAL_PATTERN, INFO.
4. Flag Presentation
   - For each flag: rule id, rationale, evidence span excerpt, source citations (>=1).
5. Negotiation Drafting
   - Generate: (a) Rider edits (clause-by-clause); (b) Email template (tone selectable).
6. Action Plan
   - Task list with due dates (stamp duty window, inspection scheduling, notice periods).
   - Export ICS (one VEVENT per task).
7. Explainability
   - Provide rule text segment + version id.
8. Versioning
   - Rulebook version captured & persisted with evaluations.
9. Regeneration Controls
   - User may re-run: extraction, drafting, tasks (idempotent where possible).
10. No Legal Advice Disclaimer
   - Prominently displayed with each output batch.

### 2.2 Extended (Post-MVP / Stretch)
- Multi-document lease comparison (renewal vs prior).
- Landlord/agent perspective mode (mirror checks).
- FAQ retrieval (RAG) scoped to rule sources only.
- Counterparty clause similarity clustering (find non-standard anomalies).
- Multi-jurisdiction plugin model.
- Inline PDF annotation export (vector highlights).

---

## 3. Non-Functional Requirements (NFRs)
- Accuracy: ≥95% recall for presence of diplomatic clause in evaluation set.
- Latency: End-to-end (<= 2MB scanned PDF) < 120s p95 on baseline hardware.
- Observability: Structured logs per agent node (trace id binding).
- Privacy: No retention of full text longer than required unless user opts in.
- Security: Server-side hashing; rulebook integrity check (SHA256).
- Reproducibility: Each output references model id + rulebook version.
- Cost Control: Use cheaper model for extraction; fall back to deterministic regex where reliable.
- Extensibility: New clause types register via a manifest & mapping function.

---

## 4. Agentic Architecture

### 4.1 High-Level Graph (LangGraph / Orchestration)
1. IngestNode → OCRNode → NormalizeNode
2. ClauseExtractNode (LLM + pattern heuristics hybrid)
3. RuleEvalNode (deterministic engine; no LLM calls)
4. FlagSynthesisNode (LLM summarization of multi-rule overlaps)
5. TaskPlannerNode (temporal reasoning)
6. DraftRiderNode / DraftEmailNode (branch)
7. ExportNode (ICS + JSON bundle)
8. AuditAssembleNode (artifact packaging)

### 4.2 Tooling (Representative)
- OCRTool (tesseract / paddle)
- EmbeddingTool (optional if semantic grouping)
- RuleEngine (pure Python, safe eval subset)
- CalendarExportTool (ICS writer)
- PDFAnnotator (future)
- DraftGenerationTool (Gemini generation model)
- TaskDateResolver (business-day & weekend adjuster)

### 4.3 Concurrency & Control
- Parallel: Clause extraction & embeddings (if used).
- Guardrails: Max tokens per call; retry w/ backoff; reduction of hallucination by constrained prompt with structured schema (JSON mode where available).
- Deterministic layer boundary: RuleEvalNode isolated—no generative calls inside.

### 4.4 Failure Modes & Recovery
| Node | Failure Example | Strategy |
|------|-----------------|----------|
| OCRNode | Low confidence pages | Fuzzy flag + re-OCR attempt with alt engine |
| ClauseExtractNode | Oversplit / merge error | Heuristic post-pass consolidation |
| RuleEvalNode | Missing clause dependency | Emit INFO flag: prerequisite data absent |
| Draft Nodes | Hallucinated statute | Source citation validator rejects & retries |

---

## 5. Data Flow (End-to-End)

1. Upload
   - Accept file → compute SHA256 → store metadata.
2. OCR
   - Page-wise text + positional references.
3. Normalization
   - Clean whitespace, line anchors, unify quotes.
4. Chunking (if embeddings)
   - Semantic or fixed window; attach page + span offsets.
5. Clause Extraction
   - LLM extraction to JSON schema → validation (enum sets, page bounds).
6. Rule Evaluation
   - Load rulebook (YAML) → compile → run matchers (regex, predicate functions).
7. Flag Assembly
   - Merge overlapping; compute highest severity.
8. Planning
   - Derive deadlines relative to discovered effective dates / signing date.
9. Drafting
   - Condition prompts with flagged clauses + rule rationales only.
10. Export
   - Persist tasks, drafts, ICS file; generate evaluation manifest JSON.
11. Audit Log
   - Append event (timestamp, model ids, rulebook hash).

---

## 6. Rulebook Design & Governance

- Format: YAML
  - id, title, description, severity_default, category, match:
    - clause_types[], patterns[], required_presence, date_logic.
  - sources[]: label, url, classification.
- Validation Script:
  - Ensures every severity has at least one source.
  - Ensures no broken regex.
- Versioning:
  - Semantic bump for: patch (typo), minor (new rule), major (severity reclassification).
- Classification:
  - LEGAL_REQUIREMENT vs INDUSTRY_NORM vs RISK_PATTERN vs INFORMATIONAL.

---

## 7. Prompt Engineering Principles

- Strict JSON schema for extraction (reject & retry).
- Use retrieval-limited context (only clause text + rule rationales).
- "No invention" system instruction + refusal pattern if missing evidence.
- Deduplicate citations (normalize URLs).
- Temperature:
  - Extraction: 0.0–0.2
  - Draft generation: 0.5 (tone variability)
  - Summaries: 0.3

---

## 8. Security & Privacy

- No plaintext retention after session unless user persists (flag).
- Hash-only cross-session dedupe.
- PII Minimization: Avoid storing names; treat them as transient tokens.
- Access Control (future): Role-based (tenant vs collaborator).
- Transport: HTTPS only; integrity of rulebook checked before run.

---

## 9. Error Handling & Observability

- Structured event log: {trace_id, node, latency_ms, token_in/out, model_id}.
- Metrics: extraction_accuracy, rule_eval_coverage, draft_retry_count, ocr_confidence_avg.
- Alerting (future): SLA breach > threshold for critical nodes.

---

## 10. Extensibility Model

- Add New Clause Type:
  1. Update enum.
  2. Provide extraction examples (few-shot).
  3. Add validation constraints.
  4. Add rule references (optional).
- Add Jurisdiction:
  - Introduce jurisdiction dimension in rulebook & gating pre-filter.
- Plugin Rule:
  - Provide Python predicate (whitelisted safe environment).

---

## 11. Roadmap (Indicative)

| Phase | Focus | Highlights |
|-------|-------|-----------|
| MVP | Core extraction & rule flags | ICS export, negotiation drafts |
| 1 | PDF inline annotation | Visual diff |
| 2 | Multi-doc temporal comparison | Renewal optimization |
| 3 | Landlord-mode | Balanced negotiation tooling |
| 4 | Multi-jurisdiction | Modular rule packs |
| 5 | Active Monitoring | Mid-lease notice windows alerts |

---

## 12. Operational Runbook (Abbrev.)

- Pre-deploy: Rulebook validate → checksum store.
- Warm-up: Cache model metadata & rulebook parse tree.
- Health checks: OCR engine availability; embedding model readiness (if used).
- Rollback: Keep last 2 rulebook versions; revert pointer.
- Incident: High extraction failure → switch to heuristic fallback (regex library).

---

## 13. Glossary

- Diplomatic Clause: Early termination right triggered by relocation scenario.
- Minor Repairs Cap: Monetary cap tenant bears per incident.
- Stamp Duty Window: 14 days (local signing) / 30 days (overseas) typical statutory trigger.
- Rider: Attachment amending or clarifying existing tenancy clauses.

---

## 14. Disclaimer

This tool provides informational analysis based on supplied documents and curated sources. It does not constitute legal advice. Always consult a qualified professional for definitive interpretation. Generated computations (e.g., stamp duty previews) are illustrative only.

---

## 15. Developer Checklist (MVP Readiness)

- [x] OCR confidence > threshold on evaluation set
- [x] Clause extraction schema validation passing
- [x] Rule coverage report > target
- [x] ICS validator (RFC 5545) passes
- [x] Draft hallucination rate < agreed limit (manual spot checks)
- [x] Security lint & dependency scan clean
- [x] Rulebook checksum logged per run

---

## 16. Sample Evaluation Manifest (Illustrative)

```json
{
  "document_id": "doc_abc123",
  "sha256": "…",
  "model_generation": "gemini-1.5-pro",
  "model_extraction": "gemini-1.5-flash",
  "rulebook_version": "1.2.0",
  "extraction_stats": {"clauses": 42, "missing_expected": 1},
  "flags": {"total": 9, "by_severity": {"ILLEGAL":0,"NON_COMPLIANT":1,"RISKY_NORM_DEVIATION":3,"UNUSUAL_PATTERN":2,"INFO":3}},
  "tasks": 5,
  "drafts": {"email_id": "draft_e1", "rider_id": "draft_r1"},
  "generated_at": "2025-01-01T10:15:00Z"
}
```
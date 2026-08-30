---
name: open-kanoonak-case
description: Prepare an authenticated Kanoonak case for legal work with complete OCR-first coverage, narrowly targeted checks of named material uncertainties, and truthful readiness reporting without guessing or mutating case data. Use for direct or indirect requests to open, inspect, organize, prepare, or summarize readiness for a captured Kanoonak case; do not use for generic legal questions or destructive case-management requests.
---

# Open a Kanoonak case

**Skill version:** `2026-08-28.1`

Read [workflow-contract.md](../../references/workflow-contract.md) first. Use
the existing authenticated, read-only MCP connection for case and page data.

## Required order

1. Call `begin_task`. Verify the authenticated role and exact compatible
   `2026-08-28.1` capture versions; stop on a missing, older, newer, or unknown
   generation rather than falling back.
2. Call `list_cases` with `contract_version: "2026-08-28.1"` before selecting
   a case or proving readiness. If the user
   names a case, require exactly one authenticated exact match; zero or
   multiple exact matches require one short clarification question and stop.
   If no case is named, that alone is not ambiguous: a viable candidate has
   at least one listed page and every listed page at `state=ready`; select the
   sole viable candidate automatically.
   If there are zero or multiple viable candidates, ask one short clarification
   question and stop.
3. Prove readiness: at least one page exists and every listed page is `ready`.
   Every `processing`, `held`, `failed`, or `expired` page is a named gap. The
   denominator is every listed ready page, without content-based deduplication.
4. Fetch OCR text with `get_document`, `contract_version: "2026-08-28.1"`, and
   `mode: "text"`. Start at the first ready range and follow every returned
   `next_range` until it is absent. Each response contains at most 20 pages;
   the case itself is not limited to 20. Match every returned `page_id` and
   `page_no` to `list_cases`. A missing, expired, failed, held, processing, or
   skipped page means **not ready**.
5. Use OCR text for complete inventory, ordering, classification, duplicate and
   gap detection, and the initial legal review. Report exactly the eight
   contract counts and the named status distinctions.
6. Treat every page as `OCR-only` by default. Only when OCR identifies a
   specific material ambiguity, relied-on fact, physical mark, decisive or
   disputed issue, or potentially different duplicate, inspect the smallest
   useful image or region. Before every call, visibly state the page number, the
   exact OCR passage or fact, one allowed trigger, and the concrete question.
   If coordinates are unavailable, one full-page image may locate that named
   issue, followed by a region only if needed. Never automatically review every
   page or most of the case/corpus. Mark each visual result
   `image-verified`, `uncertain`, or `requires judicial clarification`.
7. Report every unresolved material issue. It blocks `case_ready` and later
   drafting only when it leaves a fact or visual uncertainty genuinely
   indispensable to the requested legal work unresolved. Never infer unclear
   identity or text.
8. If a requested local operation needs a missing canonical case structure,
   apply only the shared contract's identity-only case-information confirmation;
   an ordinary read-only opening never invokes it. Then follow the shared
   contract's local-folder rules and direct first-write confirmation before
   invoking `manage_workspace.py create-case` from the one connected folder.
   Establish the court from authenticated case papers, a valid `case_ref`, or a
   direct judge-supplied value resolved and reconfirmed under that rule, never
   from a root index. Create only the canonical case structure and never
   overwrite, move, merge, rename, or delete existing data.
9. Report cases, documents, pages, the exact eight counts/statuses,
   visual checks, gaps, and readiness. `case_ready` is only the result of this
   transient proof; never claim that readiness was persisted. Do not imply
   background work or whole-case image review.

## Stop rules

Stop with a truthful gap report when the case is ambiguous, readiness proof
fails, a required page is unavailable, a genuinely indispensable fact or visual
uncertainty is unresolved, versions are incompatible, or the connector would be
written through. A missing connected folder blocks only a requested local
write: use the shared contract's exact setup guidance and continue remote work.
Never request a raw path, inspect another folder, or offer an automatic
fallback. Do not guess or present a draft after a failed proof.

## Output separation

Keep this preparation report separate from any later judicial draft. Report
source coverage, uncertainties, and gaps explicitly; do not include hidden
metadata or claim that preparation proves legal correctness.

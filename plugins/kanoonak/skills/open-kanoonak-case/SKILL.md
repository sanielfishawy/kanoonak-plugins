---
name: open-kanoonak-case
description: Prepare an authenticated Kanoonak case for legal work with complete OCR-first coverage, narrowly targeted checks of named material uncertainties, and truthful readiness reporting without guessing or mutating case data. Use for direct or indirect requests to open, inspect, organize, prepare, or summarize readiness for a captured Kanoonak case; do not use for generic legal questions or destructive case-management requests.
---

# Open a Kanoonak case

**Skill version:** `2026-08-25.1`

Read [workflow-contract.md](../../references/workflow-contract.md) first. Use
the existing authenticated, read-only MCP connection for case and page data.

## Required order

1. Complete the shared contract's workspace entry gate before any connector
   call or case processing. The host must establish exactly one attached
   primary folder, then run the rootless `manage_workspace.py inspect` from
   that current folder. Only `ready` or a confirmed-and-revalidated
   `initialized` result may continue.
2. Call `begin_task`. Verify the authenticated role and compatible versions.
3. Call `list_cases` before selecting a case or proving readiness. If the user
   names a case, require exactly one authenticated exact match; zero or
   multiple exact matches require one short clarification question and stop.
   If no case is named, that alone is not ambiguous: a viable candidate has
   at least one listed batch and every listed batch at `state=processed` with
   `page_count>0`; select the sole viable candidate automatically.
   If there are zero or multiple viable candidates, ask one short clarification
   question and stop.
4. Prove readiness: at least one intended batch exists, and every intended batch is `state=processed` with
   `page_count>0`; rejected or expired batches are named gaps. The denominator
   is every manifest page `1..page_count`.
5. Fetch OCR text for every denominator page with `get_document` in `mode:
   "text"`, using explicit closed ranges and splitting only at the 20-page
   limit. A missing, expired, failed, or incomplete page means **not ready**.
6. Use OCR text for complete inventory, ordering, classification, duplicate and
   gap detection, and the initial legal review. Report exactly the eight
   contract counts and the named status distinctions.
7. Treat every page as `OCR-only` by default. Only when OCR identifies a
   specific material ambiguity, relied-on fact, physical mark, decisive or
   disputed issue, or potentially different duplicate, inspect the smallest
   useful image or region. Before every call, visibly state batch/page, the
   exact OCR passage or fact, one allowed trigger, and the concrete question.
   If coordinates are unavailable, one full-page image may locate that named
   issue, followed by a region only if needed. Never automatically review every
   page or most of the case/corpus. Mark each visual result
   `image-verified`, `uncertain`, or `requires judicial clarification`.
8. Any unresolved material issue blocks `case_ready` and every later drafting,
   audit, or presentation step. Never infer unclear identity or text.
9. If explicitly asked to start a new case, first require an unambiguous case
   identity and resolve the root index's `forum` placeholder. Inside the same
   validated root, create only missing `الملخص.md`, `المواعيد.md`, and the eight
   canonical case directories, exclusively and without overwriting, moving,
   merging, renaming, or deleting existing data.
10. Report cases, batches, documents, pages, the exact eight counts/statuses,
   visual checks, gaps, and readiness. `case_ready` is only the result of this
   transient proof; never claim that readiness was persisted. Do not imply
   background work or whole-case image review.

## Stop rules

Stop with a truthful gap report when the case is ambiguous, readiness proof
fails, a required page is unavailable, a material visual issue is unresolved,
versions are incompatible, the host cannot establish exactly one attached
primary root, workspace inspection is not ready, or the connector would be
written through. Give one next action for a workspace stop; never request a raw
path, inspect another attachment, or offer an automatic fallback. Do not guess
or present a draft after a failed proof.

## Output separation

Keep this preparation report separate from any later judicial draft. Report
source coverage, uncertainties, and gaps explicitly; do not include hidden
metadata or claim that preparation proves legal correctness.

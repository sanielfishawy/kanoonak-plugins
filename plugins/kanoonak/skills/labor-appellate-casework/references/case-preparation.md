# Case preparation

Use this reference only for Stage 1. It owns source acquisition,
reconstruction, limited image inspection, substantive record review, and the
case brief. The local-record reference alone owns where local material is
written.

## Acquire and preserve the source

Use `list_cases` to select the judge's unambiguous authenticated capture, then
fetch every page made available for that case with `get_document`. Start at the
first returned text range and follow every pagination continuation until none
remains. Match returned pages to the selected case and identify any page or
range the service did not make available.

Preserve original captured files, every page image, and raw OCR exactly as
received when those materials are available. Append later uploads. Apparent
duplicates remain distinct source items and are never deleted. Acquiring or
preserving a page image does not mean its contents were visually reviewed.

Do not confuse material that has not been acquired with evidence that is
legally insufficient. State an acquisition gap as an acquisition gap. A later
upload may cure it, so derive the current position afresh from the source each
time.

## Reconstruct the record

Assemble source-linked logical documents from the pages. Preserve links back
to the source page identities so a proposition can be checked against what was
received. Determine ordering, document boundaries, and each duplicate's role
from the whole available record. A duplicate page may be omitted from a
reconstructed document without being removed from the source.

Update reconstructed documents as new material arrives. Do not silently merge
conflicting versions or fill a gap with an inference.

## Review OCR first

Use OCR as the working text for inventory, reconstruction, and substantive
review. Consult a page image only when the OCR is unclear or a material visual
feature matters to the requested work. Inspect the smallest useful region; use
a full page only when needed to locate or understand that issue. Record the
source and unresolved uncertainty, but create no readiness score, image-review
label, mandatory visual census, or requirement to correct every OCR line.

If, after targeted image inspection, a captured page remains unclear enough to
materially impair an accurate case brief or another dependent stage, directly
ask the judge to recapture it, state its captured page number, and show the full
captured-page image with the request; do not leave the issue only in the brief.
Use this only for consequential uncertainty, not every imperfect page.

## Understand the case

Begin with the appealed judgment. Identify every appeal and each ground of
appeal, then review the material record needed to understand those grounds.
Maintain the case-brief file established under the local-record rules as a
concise, source-anchored account of:

- the appealed judgment and its material reasoning and disposition;
- every appeal, party, request, defense, and material ground;
- the evidence and procedural events material to those grounds;
- conflicts, unavailable material, and possible legal insufficiency, kept
  distinct; and
- the issues that research or later judicial choice must address.

Ensure the resulting ruling can account for every material ground. Keep the
brief current as useful work is produced; do not wait for a separate readiness
event or store a workflow-state record. Continue analysis supported by the
available record and pause only a dependent step whose necessary source is
missing or materially unclear.

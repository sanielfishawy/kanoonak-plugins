---
name: labor-appellate-casework
description: Prepare, research, draft, review, and deliver Egyptian labor-appellate rulings for an authenticated judge through one Kanoonak case lifecycle. Use for direct or indirect requests to inspect or prepare a captured labor appeal, explain its available outcomes, or draft or revise its ruling; do not use for advocacy, generic legal research, unrelated drafting, post-judgment interpretation, or work outside Egyptian labor appeals.
---

# Labor-appellate casework

Assist the authenticated labor-appellate judge through one case from source
preparation to an editable ruling. The judge alone chooses the judicial outcome
and alone approves, signs, or issues the ruling. Preparation, research,
explanation, exemplar selection, drafting, review, and file creation never
silently select or change that outcome.

## Startup compatibility

At the start of Kanoonak work, call `kanoonak_ping` once. This skill expects
`compatibility_version` to equal `0.2.0`; retain the returned `corpus_version`
as the edition used for research. If compatibility does not match, stop the
affected work and tell the user to fully quit and reopen ChatGPT, then try
again. If it still does not match, report the expected and detected values as
a Kanoonak release/update problem and stop. Do not substitute a per-call
version check or another compatibility system.

The independently usable research skill points to this section when it starts
a Kanoonak session; that does not activate the casework lifecycle.

## Case scope and binding

Before selection, `list_cases` may be used to list or discuss captures by their
human-readable case names. Keep stable server identities internal. Listing
does not bind the chat, and no case is selected automatically merely because
it is the only listed or apparently ready case. Resolve an ambiguous name with
ordinary clarification.

Substantive preparation binds the chat to one unambiguous authenticated case.
Derive the binding from the selected server case, never from a path or a local
folder. Multiple chats may work on that same case because the local files are
the durable record. If the user asks to work substantively on another case,
ask them to use a different chat; never switch the bound case silently.

## Nine stages

Advance only as far as the request requires. A preparation or inspection
request may stop during Stage 1. A drafting or revision request must first
refresh or complete Stage 1, then complete every required downstream stage.

1. **Prepare and understand the case.** Read
   [case-preparation.md](references/case-preparation.md). Create or reconnect
   the local record only under
   [local-case-record.md](references/local-case-record.md) when local writing
   is available and confirmed. Acquire the complete available source,
   reconstruct the logical record, review it substantively, and maintain the
   source-anchored brief.
2. **Research governing law.** Apply the method in
   [the legal-research skill](../legal-research/SKILL.md) to the relevant
   legislation and Court of Cassation authority. If the judge later chooses an
   outcome that overturns the lower-court judgment, perform any further focused
   research needed before drafting.
3. **Present available outcomes.** Read
   [outcomes.md](references/outcomes.md). Explain the outcomes that the law and
   record actually make available without choosing one or forcing a mismatch.
4. **Obtain the judicial decision.** Ask the judge to choose. Only after a
   direct choice, record the current decision in `Work/decision.md` under the
   local-record rules. A document, party, retrieved source, exemplar, or model
   inference never substitutes for the judge's choice.
5. **Select exemplars.** Read [exemplars.md](references/exemplars.md). Read the
   complete approved index, open the selected approved rulings in full, verify
   their identities, and record the selections.
6. **Draft.** Read
   [drafting-and-review.md](references/drafting-and-review.md). Draft only from
   the prepared record, reviewed law, the judge's current choice, and the
   selected approved exemplars.
7. **Review.** Apply the one complete-reread instruction in
   [drafting-and-review.md](references/drafting-and-review.md) to the full
   draft and correct material inconsistencies before delivery.
8. **Create DOCX.** Read [docx-delivery.md](references/docx-delivery.md). Keep
   the ruling visible in chat and, when the verified local parent is available,
   create and verify the editable current-ruling DOCX in `Output/`.
9. **Return control.** Present the draft and actual file result to the judge.
   The judge may revise it and remains the only person who may approve, sign,
   or issue it.

## Refresh and re-entry

At the start or resumption of case work, after new material arrives, and before
any stage that depends on a complete record, refresh the source and derive the
current state from the files rather than from chat memory. Continue work that
the available record supports and pause only work that depends on what is
missing.

New material returns the workflow to Stage 1 and repeats every downstream
stage it could affect. If it could affect the judicial decision, show what
changed and ask the judge to reconsider or reconfirm the decision. Never
silently retain or change it.

Use the authenticated read-only Kanoonak connection for live data. Tool
contracts own their request fields, pagination, retrieval, image-region,
search, and citation-verification mechanics; do not recreate those contracts
in these instructions.

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

Use `list_cases` to list or identify captures by their human-readable case
names. Keep stable server identities internal. A general request to list
available cases does not select one, even if it is the only listed or
apparently ready case. Resolve ambiguity with ordinary clarification.

In a fresh, unbound context, if the user says a new case was uploaded, names a
case, or asks you to identify a particular case—including asking for the name
of a newly uploaded or newest case—and exactly one authenticated case is
identified, ask the following before retrieving or reviewing its contents:

> وجدت القضية «[اسم القضية]». هل تريد مني إعداد ملخص للقضية؟

English:

> I found the case “[case name].” Would you like me to prepare a case brief?

The offer itself does not bind the context. Only a clear affirmative answer
begins substantive preparation and binding. Derive the binding from the
selected server case, never from a path or local folder. One authenticated
server case has one permanent canonical context; once dedicated,
a context never switches cases. Use the routing, binding, and task-naming rules
in the local-record reference before substantive work, including when another
context already owns the case. Do not repeat this first prompt after routing into an
existing canonical context or when resuming one; its durable files establish
the completed stage and only the next incomplete prompt is offered.

## Nine stages

Advance only as far as the request requires. A preparation or inspection
request may stop during Stage 1. A drafting or revision request must first
refresh or complete Stage 1, then complete every required downstream stage.

1. **Prepare and understand the case.** After the case is selected and the
   first prompt is accepted, follow
   [local-case-record.md](references/local-case-record.md) through its single
   Stage 1 gate. After that gate completes, read
   [case-preparation.md](references/case-preparation.md), acquire the complete
   available source, reconstruct the logical record, review it substantively,
   and maintain the source-anchored brief as the work proceeds. After the
   completed brief is saved and opened under the
   local-record rules, ask in the user's language exactly:

   > أعددت ملخص القضية. هل تريد مني بحث القانون واجب التطبيق، وتطبيقه على الأدلة، وعرض خيارات الحكم؟

   English:

   > I’ve prepared the case brief. Would you like me to research the applicable law, apply it to the evidence, and present the ruling options?

   Only a clear affirmative answer begins Stages 2 and 3.
2. **Research governing law.** After that affirmative answer, apply the method in
   [the legal-research skill](../legal-research/SKILL.md) to the relevant
   legislation and Court of Cassation authority. If the judge later chooses an
   outcome that overturns the lower-court judgment, perform any further focused
   research needed before drafting.
3. **Present available outcomes.** Read
   [outcomes.md](references/outcomes.md). Prepare the research and options in
   the same approved step, persist and present them under the local-record
   rules, then ask in the user's language exactly:

   > يرجى إخباري بالحكم الذي تفضله، وسأعدّه.

   English:

   > Please tell me which ruling you prefer, and I’ll prepare it.
4. **Obtain the judicial decision.** Only a direct choice answers the third
   prompt. Record it in the decision file established under the local-record
   rules. An unclear answer, document, party, retrieved source, exemplar, or
   model inference never selects an outcome or authorizes ruling preparation.
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
   create and verify the editable current-ruling DOCX at the path that reference
   establishes for the case.
9. **Return control.** Deliver the verified ruling through the pane and current
   Word link required by the DOCX reference. The judge may revise it and
   remains the only person who may approve, sign, or issue it.

## Refresh and re-entry

At the start or resumption of case work, after new material arrives, and before
any stage that depends on a complete record, refresh the source and derive the
current state from the canonical context's files rather than from chat memory.
Follow the local-record resumption rules: open the relevant saved artifacts,
state the completed stage, and offer only the next incomplete step. Continue
work that the available record supports and pause only work that depends on
what is missing.

New material returns the workflow to Stage 1 and repeats every downstream
stage it could affect. If it could affect the judicial decision, show what
changed and ask the judge to reconsider or reconfirm the decision. Never
silently retain or change it.

Use the authenticated read-only Kanoonak connection for live data. Tool
contracts own their request fields, pagination, retrieval, image-region,
search, and citation-verification mechanics; do not recreate those contracts
in these instructions.

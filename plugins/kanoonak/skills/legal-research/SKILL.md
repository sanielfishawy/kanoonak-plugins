---
name: legal-research
description: Research Egyptian labor legislation and Court of Cassation authority through Kanoonak, either independently or for a labor-appellate case. Use for direct or indirect requests to find, read, assess, and cite governing legal sources; do not use to prepare case evidence, choose a judicial outcome, advocate for a party, or draft and deliver a ruling.
---

# Egyptian legal research

Use this skill independently for a legal-research request or at Stage 2 of the
labor-appellate casework lifecycle. It owns legal-source research only; it does
not select a case, prepare evidence, choose an outcome, select judicial
exemplars, or draft a ruling.

Before the first Kanoonak tool call in a session, apply
[the package startup compatibility check](../labor-appellate-casework/SKILL.md#startup-compatibility)
without activating the casework lifecycle. Do not duplicate or replace that
check here.

## Method

1. Identify the legal questions that the request or prepared case actually
   raises. Keep factual assumptions distinct from legal propositions.
2. Use `search_lexical` and `search_semantic` as complementary research aids.
   Use `get_article`, `get_ruling`, `expand`, `get_chunk`, and
   `list_documents` as useful to retrieve the governing legislation and Court
   of Cassation authorities. The tool contracts own query fields, filters,
   result expansion, and pagination.
3. Read every promising authority far enough to assess it in context; read any
   authority relied on for a holding or citation in full rather than relying on
   a search snippet.
4. Assess what each retrieved text actually establishes, its relevance to the
   question, and any material limit on applying it. Do not turn a party's
   position or a search result into law.
5. Record the useful holdings, citations, and their application in
   `Work/research.md` when research belongs to a prepared case. For an
   independent request, return the same source-grounded analysis in the form
   the user requested.

Retrieve and review the actual legal text before relying on it. Preserve
truthful uncertainty when the served sources do not answer the question. Add
no quota, research form, routing taxonomy, mandatory checker, or fixed report.
The judge remains responsible for any judicial decision.

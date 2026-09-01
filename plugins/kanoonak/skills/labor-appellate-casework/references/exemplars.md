# Approved exemplars

Use this reference at Stage 5, after the judge has selected the current
outcome. Judicial exemplars guide structure and style; they never supply case
facts, governing law, or the judicial choice.

1. Call the authenticated, read-only `get_exemplar_index` tool with no input
   and read its entire Arabic-first Markdown response. Compare the complete
   approved collection; do not search, filter, classify, embed, or ask software
   to choose an exemplar.
2. Select the closest appropriate approved exemplar or exemplars for the
   material situation, chosen outcome, and useful drafting role. If there is no
   exact match, use the closest appropriate approved exemplar and respect every
   caution in the index.
3. For each selection, call `expand` with its opening `chunk_id`, follow the
   tool's retrieval mechanics until the ruling has been read in full, and
   verify that the returned `doc_id` exactly matches the index entry before
   using it.
4. Record each selected ruling's identity and, when useful, one short reason in
   `Work/exemplars.md`. Do not copy the complete index or full ruling text into
   that file.
5. Draft from the case record and reviewed law. Use the verified selected
   exemplars only for appropriate structure and style.

If the complete index cannot be read, an opening chunk is unknown, the full
ruling cannot be read, or its returned document identity does not match, stop
before drafting and explain what is unavailable. Never fall back to an
unapproved corpus ruling, a fixed template, or a removed directive.

The private index and ruling collection are server-private data. They are not
bundled in this plugin or written into a public catalogue. The tool supplies
the current approved index; add no client cache, sidecar, index schema,
version, hash, classifier, or resolver.

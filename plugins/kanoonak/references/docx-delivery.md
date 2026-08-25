# DOCX delivery reference

The ruling skill's clean artifact is a judge-editable Word draft. The MCP
connector does not write files. The host grants one exact, already existing
delivery directory and labels it:

- `drafts` — the selected case's existing `المسودات/` directory;
- `library-download` — the host's existing Library/download fallback.

The host also classifies the grant `local-unsynchronized`. The helper never
searches for, chooses, or creates a directory. If the exact grant or trusted
classification is unavailable, stop truthfully. This version supports the
existing Unix/macOS filesystem path and local NTFS Windows only. It refuses
synchronized/cloud placeholders, SMB, FAT/exFAT, and reparse-backed grants.
`storage-synchronization-classification` is instruction-led, not mechanically
proved by the ruling checks.

For a `library-download` delivery, the local pair is complete but case-folder
placement remains `shared-folder placement: PENDING` until the user confirms
both exact files were saved into the intended case's existing `المسودات/`
directory. Treat that confirmation as the exact save check; never describe a
download-only or DOCX-only save as shared-folder placement.

```text
قانونك/<case-folder>/المسودات/<next-name>.docx
قانونك/<case-folder>/المسودات/<next-name>.metadata.yaml
```

## Checked input

Before delivery, run the universal checker over the exact ruling text. Pass its
`ruling_sha256` unchanged as `expected_ruling_sha256`. The helper reruns that
checker, refuses any failure or digest mismatch, and performs no normalization,
date rewrite, digit shaping, trimming, or other text transformation.

Pass transient formatting JSON with exactly one item per canonical paragraph:

```json
{"paragraphs":[{"role":"title","opening_phrase":null}]}
```

The closed roles are:

- `title`: centered, wholly bold, no first-line indent;
- `transition`: centered, wholly bold, 360-twip first-line indent;
- `substantive`: fully justified, 360-twip first-line indent, with one non-empty
  exact paragraph prefix in `opening_phrase` to bold;
- `plain`: fully justified, unbolded, no first-line indent.

The workflow chooses these roles from the directive and bound exemplar. The
publisher validates the closed shape, count, nullability, and exact prefix, but
does not infer or certify the paragraph's legal role. Formatting JSON is never
persisted or logged.

## Publication

The host-side helper is
`plugins/kanoonak/scripts/create_ruling_docx.py`. Its command boundary is:

```text
--delivery-dir <exact-existing-directory>
--grant-label drafts|library-download
--storage-classification local-unsynchronized
--kind حكم|حكم-تمهيدي|قرار
--ruling-file <exact-UTF-8-text>
--expected-ruling-sha256 <universal-check-digest>
--formatting-json <transient-role-map>
--metadata-json <draft-metadata>
```

Allocation is per kind. Either same-number `.docx` or `.metadata.yaml` member
reserves that number. The helper creates the next two-digit pair and never
accepts, repairs, reuses, overwrites, or deletes an existing leaf:

```text
مسودة-حكم-01.docx
مسودة-حكم-تمهيدي-01.docx
مسودة-قرار-01.docx
```

Both payloads are complete-written, synced, reread, digest-checked, and
structurally reopened in same-directory staging. Unix uses its descriptor-held
private stage directory. Windows uses direct random `CREATE_NEW` stage leaves
whose native handles deny write/delete sharing until publication and whose
opened links are removed by handle disposition. Publication uses atomic
no-replace hard links, sidecar first and DOCX last. A concurrent
collision rolls back only a leaf whose stable identity proves this invocation
created it, then retries the next number. An unprovable or crash orphan is
preserved, visibly reported, and reserves its number.

The sidecar carries draft/state/case/kind metadata, the exact paired artifact
name, `ruling_text_sha256` for the checked UTF-8 body, and `artifact_sha256` for
the final DOCX bytes. The persistent case validator independently extracts the
ordinary Word paragraphs joined with exact `\n\n` and checks both digests.
Recomputing only the artifact digest after editing cannot validate stale
checked-text metadata.

## Word contract

The clean body contains only the checked ruling text. The helper explicitly
stores Arial 16 in every Word font/size slot, paragraph bidi and run RTL, full
justification where applicable, 1.5 automatic line spacing, zero after-spacing,
real 360-twip indentation, and real bold runs. Western U+0030–U+0039 digits and
already-unpadded slash dates are preserved exactly.

After publication, reopen and render-check the DOCX with Documents before
presenting it. Structural reopen is not visual approval. A create, reopen,
digest, extraction, or render failure is a workflow stop. The helper creates
drafts only and never writes an issued-rulings directory.

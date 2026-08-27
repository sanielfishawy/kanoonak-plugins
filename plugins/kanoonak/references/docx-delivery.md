# DOCX delivery reference

The ruling skill's clean artifact is a judge-editable Word draft. The MCP
connector does not write files. Local publication is available only after the
user has requested it and the shared [local-folder rules](workflow-contract.md#local-folder-rules)
have confirmed the connected project folder. The publisher uses that process
current working directory and accepts one canonical case-folder leaf plus the
minimal selected case identity described below, never a root path. It requires
the selected case's complete existing ten-item structure and derives the
destination as that case's exact existing `المسودات/` directory.

The helper accepts no workspace or delivery-root path, never searches for,
selects, or creates another root, case, or drafts directory. It validates only
the process-CWD/selected-canonical-case/`المسودات` boundary. It also accepts the
selected authenticated case's minimal full identity JSON—its full top-level
five-field case tuple and ordered appeal members/roles, with no surplus or
duplicate keys—and requires an exact match with the existing `الملخص.md`
identity before writing. The same strict JSON parsing applies to metadata and
formatting input. If that closed boundary is
absent, malformed, or belongs to a different identity, stop truthfully.
Existing local indirection is part of the user's folder arrangement; Kanoonak
makes no storage or physical ancestry certification claim.

```text
<connected-project-folder>/<case-folder>/المسودات/<next-name>.docx
<connected-project-folder>/<case-folder>/المسودات/<next-name>.metadata.yaml
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
--case-folder <one-canonical-existing-case-leaf>
--case-identity-json <minimal-full-case-identity>
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

Both payloads are complete-written with exclusive final-leaf creation, then
reread, digest-checked, and structurally reopened. A collision may advance only
before this invocation has made either member visible or uncertain. Once either
member was created or may have been created, preserve it, report the exact
partial outcome, and stop. Never delete, overwrite, silently retry a partial
pair, or publish elsewhere. Every preserved or uncertain member reserves its
number.

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

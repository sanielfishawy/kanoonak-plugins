# DOCX delivery reference

The ruling skill's clean artifact is a judge-editable Word draft. The MCP
connector does not write files. Publication is available only after the shared
workspace entry gate reports `ready`. The publisher uses the host-provided
current workspace root and accepts only one canonical case-folder leaf. It
revalidates the workspace marker and canonical root files, requires the case's
complete existing ten-item structure, and derives the destination as that
case's exact existing `المسودات/` directory.

The helper accepts no workspace or delivery-root path, never searches outside
the validated workspace, and never selects or creates a case or drafts
directory. If the exact boundary is absent, malformed, symlinked, replaced, or
no longer on accepted storage, stop truthfully. Storage synchronization remains
subject to the workspace gate's honest limitation; ruling checks do not prove
it independently.

```text
<validated-workspace>/<case-folder>/المسودات/<next-name>.docx
<validated-workspace>/<case-folder>/المسودات/<next-name>.metadata.yaml
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
no-replace hard links, sidecar first and DOCX last. A collision on the first
public link safely retries because this invocation published nothing. On Unix,
once either public link exists, any later collision or failure preserves and
reports every visible or uncertain final leaf: a pathname cannot be deleted
conditionally on inode identity. Windows retains its native handle-disposition
cleanup where the opened link identity is stable. Every preserved or crash
orphan visibly reserves its number.

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

# Native DOCX delivery reference

This is Kanoonak's single authority for ruling DOCX creation, delivery, and
Word formatting. Follow the shared
[local-folder rules](workflow-contract.md#local-folder-rules) for every local
write; do not restate or relax them elsewhere.

## Automatic artifact

For the initial content-safe ruling shown for review, and for every content-safe
revision shown afterward, automatically use the host's native Documents
capability to create a separate editable DOCX. Do not ask a per-draft save
question. Every DOCX remains a review draft; only the labor-appellate judge may
approve, sign, or issue a ruling.

Before the first local write for the case in the chat, obtain the one destination
confirmation required by the shared local-folder rules. Reuse it while its chat,
authenticated connector context, selected case, connected folder, and exact
case destination remain unchanged; any change requires fresh confirmation.

When that confirmed destination is available, save only in the selected
canonical case's existing `المسودات/` directory. Never create or use a fallback
folder and never write a review draft to `الأحكام/`. If no confirmed case
destination is available, create a native chat artifact when the host supports
one and say truthfully that it was not saved in the case folder. If native DOCX
creation itself is unavailable or fails, keep the content-safe chat draft and
say truthfully that no DOCX was created.

## Names and file safety

Allocate the lowest unused number from `01` through `99` for the ruling's own
kind:

```text
مسودة-حكم-NN.docx
مسودة-حكم-تمهيدي-NN.docx
مسودة-قرار-NN.docx
```

An existing DOCX or same-stem legacy `.metadata.yaml` file reserves that
number. Every revision gets a new number. Stop truthfully if all numbers for the
kind are reserved. Never overwrite, delete, repair, rename, reuse, or silently
replace an existing or uncertain file, and never switch destinations after a
conflict or failure.

The native Documents capability may inspect, render, and correct only the
current not-yet-delivered attempt. Before reporting success, verify that the
DOCX exists at the reported destination, is editable, and reopens and renders
cleanly. If verification fails or placement is incomplete, report what happened
as partial or uncertain rather than success, preserve the attempt unchanged, and
do not retry or mutate it.

## Clean text

The DOCX body contains only the exact clean ruling presented for review. Keep
preparation notes, checker results, audits, statuses, metadata, and delivery
messages outside it. Do not normalize, trim, rewrite, or otherwise transform
the body during creation. Preserve Western digits U+0030-U+0039 and unpadded
slash dates exactly.

## Word format

The selected legal template and, when available, the bound exemplar identify
each paragraph's semantic treatment and the exact opening phrase of a
substantive paragraph. Apply these rules with real Word paragraph and run
formatting:

- Use Arial 16 pt everywhere, including the complex-script font and size.
- Set Arabic text and paragraphs right-to-left/bidirectional.
- Use 1.5-line spacing within every paragraph, 0 pt before, and 8 pt after.
  Do not add blank spacer paragraphs.
- Use one-inch (2.54 cm) margins on all four sides.
- Title paragraphs are centered, wholly bold, and have no first-line indent.
- Transition paragraphs are centered, wholly bold, and have a 0.25-inch
  (360-twip) first-line indent.
- Substantive paragraphs are fully justified with a 0.25-inch (360-twip)
  first-line indent; bold only that paragraph's exact opening phrase.
- Plain paragraphs are fully justified, unbolded, and have no first-line indent.

Do not simulate indentation or spacing with spaces, tabs, or blank lines. Do
not use Markdown bold, visual-line bolding, or a first-comma heuristic. Page
size, orientation, line width, pagination, and other host layout defaults are
not pinned.

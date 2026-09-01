# Editable DOCX delivery

Use this reference for Stage 8 and for every later ruling revision. It is the
single authority for output names, archiving, exact Word formatting, and file
verification. The local-record reference alone owns parent proof and first-save
confirmation.

## Deliver each draft

Keep every initial or revised ruling visible in chat. When its verified local
case folder is available, use the host Documents capability to create an
editable DOCX automatically at:

`Output/الحكم الحالي.docx`

Before replacing an existing current file, move it to the next unused archive
name under `Output/النسخ السابقة/`: `الحكم 01.docx`, then `الحكم 02.docx`, and
so on. Use at least two digits for 1–99, continue with the next positive
integer without an artificial cap, never overwrite an archive, and never
delete a prior version. “Current” is deliberate because the judge may revise
the ruling later.

If the verified parent is unavailable, keep the full ruling visible in chat
and report that it was not saved locally. If DOCX creation fails, keep the full
ruling visible, explain the failure truthfully, and do not imply that a file
was created.

## Preserve exact text

The DOCX contains only the ruling. Preserve its exact wording, paragraph
boundaries, visible placeholders, Western digits U+0030–U+0039, and dates in
unpadded day/month/four-digit-year form such as `7/6/2026`. DOCX creation never
normalizes, trims, rewrites, or silently repairs the ruling. Correct the draft
first, recreate the current file, and verify its extracted text.

Use the host Documents capability, not client-side Python. Do not place
research notes, case material, status messages, Markdown bold markers, or file
delivery commentary inside the ruling.

## Exact Word formatting

- Arial 16 pt for all text, including complex-script font and size;
- right-to-left and bidi paragraph/run behavior;
- 1.5 line spacing, 0 points before, 8 points after, and no spacer paragraphs;
- 1-inch (2.54 cm) margins on all four sides;
- titles centered, wholly bold, with no first-line indent;
- transition paragraphs centered and wholly bold, with a 0.25-inch first-line
  (360-twip) indent;
- substantive paragraphs fully justified with a 0.25-inch first-line indent
  and only their exact opening phrase bold; the indent is 360 twips;
- plain paragraphs fully justified, unbolded, and unindented; and
- genuine Word formatting rather than spaces, tabs, blank lines, Markdown
  bolding, visual-line bolding, or a first-comma heuristic.

Page size, orientation, line width, pagination, and other host-layout defaults
remain unpinned. The selected exemplar and the ruling's actual structure
identify each paragraph treatment and the exact opening phrase; do not create a
fixed template, module bank, paragraph classifier, or formatting heuristic.

## Verify before reporting success

Reopen or render the DOCX and verify that it is editable, complete, readable,
text-exact, and formatted as required. Inspect Western digits, unpadded dates,
all four paragraph roles, margins, spacing, indents, bidi behavior, font, size,
and exact bold boundaries. If verification exposes a content error, correct
the ruling text first, recreate the file, and verify again. Report only the
file result actually achieved.

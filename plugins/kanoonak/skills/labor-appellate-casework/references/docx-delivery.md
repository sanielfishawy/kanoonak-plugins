# Editable DOCX delivery

Use this reference for Stage 8 and for every later ruling revision. It is the
single authority for output names, archiving, exact Word formatting, and file
verification. The local-record reference alone owns parent proof and first-save
confirmation.

## Deliver each draft

Keep every initial or revised ruling visible in chat. When its verified local
case folder is available, use the host Documents capability to create an
editable DOCX automatically at the path established for the case's naming
convention:

- Arabic default: `الأحكام/الحكم الحالي.docx`.
- Explicit English: `Output/current-ruling.docx`.

For an existing case, its exact current-file and archive paths already on disk
control instead. In particular, continue the 0.2.2 paths
`Output/الحكم الحالي.docx` and `Output/النسخ السابقة/` without migration or a
parallel current file.

Before replacing an existing current file, move it to the next unused archive
name for that same convention: `الأحكام/النسخ السابقة/الحكم 01.docx`, then
`الحكم 02.docx`, and so on by default; or
`Output/previous-versions/ruling-01.docx`, then `ruling-02.docx`, and so on in
explicit-English cases. Use at least two digits for 1–99, continue with the
next positive integer without an artificial cap, never overwrite an archive,
and never delete a prior version. “Current” is deliberate because the judge
may revise the ruling later.

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
- the opening title-block paragraphs — court, circuit, draft label, appeal
  identity, and hearing date — centered, wholly bold, underlined, and with no
  first-line indent;
- the opening procedural paragraph, such as
  `بعد سماع المرافعة ومطالعة الأوراق والمداولة قانوناً:`, physically
  right-aligned using logical-start paragraph alignment
  (`<w:jc w:val="start"/>`), wholly bold, not underlined, and with a 0.25-inch
  (360-twip) first-line indent from the right;
- substantive paragraphs fully justified with a 0.25-inch first-line indent
  and only their exact opening phrase bold; the indent is 360 twips;
- plain paragraphs fully justified, unbolded, and unindented; and
- genuine Word formatting rather than spaces, tabs, blank lines, Markdown
  bolding, visual-line bolding, or a first-comma heuristic.

The title block ends with the hearing-date paragraph. The immediately
following procedural-opening paragraph is a separate paragraph role and must
not inherit the title block's centering or underline.

These are paragraph roles, not visual lines; wrapping in Word does not create
another role.

For every Arabic/RTL run, apply right-to-left run behavior. When the run is
intended to be bold, apply both ordinary bold and complex-script bold
(`<w:b/>` and `<w:bCs/>`) together with `<w:rtl/>`. When it is intended not to
be bold, explicitly disable both bold properties so bold is not inherited.

Page size, orientation, line width, pagination, and other host-layout defaults
remain unpinned. The selected exemplar and the ruling's actual structure
identify the treatment of the remaining substantive and plain paragraphs and
the exact substantive opening phrase; they do not override the fixed opening
title-block and procedural roles. Do not create a fixed template, module bank,
paragraph classifier, or formatting heuristic.

## Verify before reporting success

Before delivery, reopen the saved DOCX and verify that it is editable, complete,
text-exact, and that its document properties match the formatting rules above.
Perform a targeted RTL-format audit: confirm that every Arabic paragraph has
`<w:bidi/>` in valid paragraph-property order before spacing, indentation, and
alignment; every Arabic/RTL run has `<w:rtl/>`; bold Arabic has both `<w:b/>`
and `<w:bCs/>`; and non-bold Arabic explicitly disables both. Use logical-start
alignment and a 360-twip first-line indent for the opening procedural paragraph.
Never position text with spaces or tabs.

If verification exposes a content error, correct the ruling text first,
recreate the file, and verify again. Report only the checks actually completed
and the file result achieved.

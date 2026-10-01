# Local case record

This reference is the sole authority for the one Stage 1 local-project gate,
canonical case context, legal-identity prerequisite, record-derived task naming,
first-save confirmation, case-record paths, and milestone pane presentation.
Substantive work on a selected case requires local writing. The gate begins
only after the judge accepts preparation of one unambiguous case brief, at the
transition from case discussion into real casework. Listing cases, asking
questions about cases, selecting or resolving which case the user means, the
initial brief-offer prompt, and independent general research do not run this
gate.

Within the single gate, prove the attached parent; route to or bind the canonical
context; review enough authenticated case material to establish a clear legal
identity; name the canonical task when needed; confirm the first save; and
create or reconnect the local record. The identity review may read any or all
available case material when useful. Do not create a case folder, save case
contents, or prepare a case brief until the legal identity is clear and the
destination is confirmed.

## Prove the attached parent

Before substantive casework, verify that the current task is inside a local
Kanoonak project whose attached folder is the intended parent for Kanoonak case
folders. Use that verified attached folder as the parent. Do not accept a path
merely supplied in chat or send host or project metadata to Kanoonak.

If host inspection succeeds but there is no exact registered local-project
match, show no proposed path, write nothing, do not retrieve, read, or analyze
the case contents, and say exactly in the user's language:

> لا أستطيع مراجعة هذه القضية أو حفظ ملفاتها من هذه المحادثة.
>
> 1. افتح مشروع «قانونك»، أو أنشئه إذا لم يكن موجوداً.
> 2. تأكد من ربط المجلد الرئيسي لقضايا «قانونك» بالمشروع.
> 3. ابدأ محادثة جديدة من داخل المشروع بدلاً من نقل هذه المحادثة.
> 4. قل للمحادثة الجديدة أن تعمل على هذه القضية.
> 5. أرشف هذه المحادثة.
>
> لم أراجع القضية ولم أحفظ شيئاً.

English:

> I can’t review or save this case from this chat.
>
> 1. Open your Kanoonak project, or create one if it does not exist.
> 2. Make sure the parent folder for your Kanoonak cases is attached to the project.
> 3. Start a new chat inside the project rather than moving this chat.
> 4. Tell the new chat to work on this case.
> 5. Archive this chat.
>
> I have not reviewed the case or saved anything.

If the verification fails for any other technical reason, show no proposed
path, write nothing, do not retrieve, read, or analyze the case contents, and
say exactly in the user's language:

> لم أستطع التأكد من مجلد الحفظ الآن. لم أراجع القضية ولم أحفظ شيئاً. حاول مرة أخرى.

English:

> I couldn’t check the save folder right now. I haven’t reviewed the case or saved anything. Please try again.

A user response cannot supply or override this verification. Re-establish it
before the first local write in each later turn.

## Route one canonical context

Before substantive casework, identify the unique task associated with the
selected authenticated server case in the current project. If the current task
is already canonical, continue here. If another task is uniquely canonical,
direct the user there and continue the case only there. Do not bind or rename
the current task, and do not review or save the case here. State that nothing
was reviewed or saved here and that the duplicate task may be archived; never
archive it automatically. If no canonical task exists, associate the current
unbound task. Never switch a task already associated with another case. If the
association is ambiguous, stop and explain the ambiguity. The authenticated
server case, not its Capture name, task title, path, or folder, controls the
association. Complete routing before any task naming. Only the canonical task
may receive a record-derived title.

If the current context is bound to another case and no verified target exists,
do not retitle, archive, or write. Say exactly in the user's language:

> هذه المحادثة مخصصة بالفعل للقضية «[القضية الحالية]». افتح محادثة جديدة داخل مشروع «قانونك» للقضية «[القضية المطلوبة]»، ثم اطلب مني المتابعة هناك. لم أراجع القضية المطلوبة ولم أحفظ لها شيئاً هنا.

English:

> This context is already dedicated to “[current case].” Open a new context in the Kanoonak project for “[requested case],” then ask me to continue there. I haven’t reviewed or saved anything for the requested case here.

Durable saved files govern resumption. Inspect them to establish the completed
stage and offer the next incomplete step; another task's unsaved memory does
not establish case progress.

## Establish the legal identity and name the canonical task

Before resolving a destination, review enough authenticated case material to
establish a clear legal identity for the matter. Read any or all available
material when useful. If the authenticated material does not establish a clear
identity, or establishes conflicting identities, create no folder, save
nothing, and prepare no case brief. Explain the specific gap and ask for the
identifying or clarifying material needed. When new material arrives, resume
the same authenticated case and canonical context.

The Capture name identifies the uploaded case but is not evidence of its legal
identity. Establish the identity from authenticated case material. When that
material verifies an appeal number and judicial year, use that verified appeal
identifier as the concise task title and new folder name, even if it matches
the Capture name. Do not replace an available verified appeal identifier with
a description based on the parties or subject matter.

Before first-save confirmation, ensure that the current canonical task uses
that record-verified identifier as its concise title. Preserve an explicit
user-chosen title; otherwise replace a generic, inaccurate, or agent-invented
descriptive title. Verify that the displayed title still identifies the same
case without requiring character-for-character equality.
Treat harmless host normalization, including whitespace normalization, as
success. If renaming is unavailable or fails, explain exactly what happened and
continue when the case association remains unambiguous.

## Confirm the first save

After the legal identity is clear, inspect only direct-child folder names under
the verified parent. If exactly one clearly corresponds to the authenticated
case, select its exact existing leaf and paths. If several are plausible, ask
the user to choose among those shown children; never accept an arbitrary path
or open their contents before confirmation. Preserve every existing convention,
including the 0.2.2 `Source/`, `Record/`, `Work/`, and `Output/` layout, without
switching, renaming, or migrating it.

If no existing folder is selected, use the same record-verified appeal
identifier as the concise, filesystem-safe leaf. Use Arabic by default
regardless of conversation language; use English only when explicitly
requested before the first save. Do not guess or translate party names.

For either an existing or new destination, before opening the local folder or
making the first local save, show the exact full case folder and ask exactly:
> Save this case here?

One clear affirmative answer in the current chat confirms later saves while
the authenticated case, parent, and destination remain unchanged. A decline,
unclear answer, case switch, parent change, or destination change means write
nothing until the current destination is proved and confirmed again.

## Maintain and present the record

A new case folder contains exactly this four-folder record. Use the Arabic
column by default and the English column only when explicitly requested:

| Purpose | Arabic default | Explicit English |
|---|---|---|
| Case folder | `<اسم القضية>/` | `<Case Name>/` |
| Source | `المصادر/` | `Source/` |
| Record | `سجل القضية/` | `Record/` |
| Work | `ملفات العمل/` | `Work/` |
| Brief | `ملفات العمل/ملخص القضية.md` | `Work/case-brief.md` |
| Decision | `ملفات العمل/النتيجة القضائية المختارة.md` | `Work/decision.md` |
| Research | `ملفات العمل/البحث القانوني.md` | `Work/research.md` |
| Options | `ملفات العمل/خيارات الحكم.md` | `Work/ruling-options.md` |
| Exemplars | `ملفات العمل/الأحكام الاسترشادية المختارة.md` | `Work/exemplars.md` |
| Output | `الأحكام/` | `Output/` |

The source folder contains original captured files, every page image, and raw
OCR. Preserve each original source filename, append material, and preserve
apparent duplicates. Kanoonak-created pages or text use `الصفحة 001.jpg` or
`النص الخام للصفحة 001.txt` by default, or concise English names in
explicit-English cases. The record folder contains source-linked logical
documents reconstructed from the pages; use short names such as
`الحكم المستأنف.md` and `صحيفة الاستئناف.md`, or concise English
equivalents. A duplicate may be omitted from reconstruction but not deleted
from source.

Create work files only when their stage produces useful work. The DOCX
reference alone owns ruling replacement and archive numbering. Add no root
bootstrap, workspace guide, case schema, lifecycle state, taxonomy, validator,
generic notes, counter, ledger, sidecar, naming-preference, or compatibility
file. The existing files show current state. Write each useful result
incrementally to its established case folder.

After the brief is complete, leave it visible in the right pane. After the
research and ruling options are complete, leave both files open with the
research visible. A pane failure does not invalidate or delete completed work;
preserve every completed file and report the presentation failure briefly.

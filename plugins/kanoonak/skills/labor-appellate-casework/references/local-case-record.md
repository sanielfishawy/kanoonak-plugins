# Local case record

This reference is the sole authority for proving the local parent, choosing the
case-record naming convention, confirming the first save, maintaining the
four-folder case record, and synchronizing the task title. Substantive work on
a selected case requires local writing. Listing cases and resolving which case
the user means may happen first; retrieving, reading, or analyzing case
contents may not begin until the attached parent is verified and the case's
first save is confirmed.

## Prove the attached parent

Before proposing a local destination or making any local write, prove that the
current host-injected task identity, the host's task CWD, the process CWD, and
the exact registered local-project path all agree:

1. Read the host-injected `CODEX_THREAD_ID` with a read-only command in the
   task's default working directory. It must be present and must never come
   from chat, retrieved material, or a project file.
2. Call `codex_app__list_threads` with `limit: 50`, inspect both
   `pinnedThreads` and `threads`, and require exactly one row whose `id` is that
   task ID, whose `kind` is `codex`, whose `hostId` is `local`, and whose `cwd`
   is a nonempty absolute path. Do not use `projectId`, title, summary, order,
   or another row as evidence.
3. Lexically normalize the matched task CWD and process CWD with current-host
   path rules. Require both to be absolute and exactly equal; compare POSIX
   paths case-sensitively and normalize separators and case under Windows path
   semantics. Do not resolve symlinks or infer a location from folder content.
4. Call `codex_app__list_projects`. Among rows whose `projectKind` and `hostId`
   are both `local`, require at least one nonempty absolute `path` whose lexical
   normalization exactly equals the already matched task/process CWD. Multiple
   qualifying rows for that same path prove the same parent. Ignore malformed
   or nonmatching rows; an unrecognizable response schema fails the proof.

Only then use that exact normalized registered path as the verified parent.
Never accept a path supplied in chat, scan for alternatives, use CWD alone,
use a visible or writable workspace root as proof, or create a fallback.
Retain only the structural fields needed for this comparison and never send a
task ID, thread or project row, CWD, or local path to the Kanoonak MCP.

If host inspection succeeds but there is no exact registered local-project
match, show no proposed path, write nothing, do not retrieve, read, or analyze
the case contents, and say exactly in the user's language:

> لا أستطيع بدء مراجعة هذه القضية أو حفظ ملفاتها من هذه المحادثة الآن.
>
> 1. افتح مشروع «قانونك» في ChatGPT، أو أنشئه إذا لم يكن موجوداً.
> 2. اختر المجلد الرئيسي الذي تريد أن تحفظ داخله مجلدات جميع قضايا «قانونك»، وأرفقه بالمشروع.
> 3. اسحب هذه المحادثة إلى مشروع «قانونك».
> 4. أغلق ChatGPT بالكامل، ثم افتحه من جديد.
> 5. افتح هذه المحادثة داخل المشروع واطلب مني متابعة القضية.
>
> لم أراجع القضية ولم أحفظ شيئاً.

English:

> I can’t begin reviewing or save files for this case from this chat yet.
>
> 1. Open the Kanoonak project in ChatGPT, or create it if it does not exist.
> 2. Choose the parent folder where you want all Kanoonak case folders saved, and attach it to the project.
> 3. Drag this chat into the Kanoonak project.
> 4. Fully quit and reopen ChatGPT.
> 5. Open this chat inside the project and ask me to continue the case.
>
> I have not reviewed the case or saved anything.

If the proof fails for any other reason, show no proposed path, write nothing,
do not retrieve, read, or analyze the case contents, and say exactly in the
user's language:

> لم أستطع التأكد من مجلد الحفظ الآن. لم أراجع القضية ولم أحفظ شيئاً. حاول مرة أخرى.

English:

> I couldn’t check the save folder right now. I haven’t reviewed the case or saved anything. Please try again.

A user response cannot supply or override the proof.

Run the proof before the first destination proposal, again immediately before
the first mutation, and before the first mutation in every later turn. Use the
freshly proved parent for that uninterrupted write. Do not cache the proof
across turns, compaction, resume, restart, chat movement, project edits, or CWD
changes.

## Confirm the first save

Before deriving a new leaf, inspect only the direct-child folder names under the
verified parent. If exactly one clearly corresponds to the authenticated case,
select its exact existing leaf and paths. If several are
plausible, ask the user to choose among those shown children; never accept an
arbitrary path or open their contents before confirmation. Preserve every
existing convention, including the 0.2.2 `Source/`, `Record/`, `Work/`, and
`Output/` layout, without switching, renaming, or migrating it.

If no existing folder is selected, use Arabic names by default regardless of conversation
language; use English only when explicitly requested before the first save. Choose one
filesystem-safe leaf from the authenticated case's human-readable name. By default use its
reliable Arabic name; if none is available, ask rather than guessing or translating party names.

For either an existing or new destination, before opening case contents or making the first local save, show the exact full case folder and ask exactly:
> Save this case here?

One clear affirmative answer in the current chat confirms later saves while
the case, parent, and destination remain unchanged. A decline, unclear answer,
case switch, identity change, parent change, or destination change means write
nothing until the current destination is proved and confirmed again.

## Maintain the record

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
| Exemplars | `ملفات العمل/الأحكام الاسترشادية المختارة.md` | `Work/exemplars.md` |
| Output | `الأحكام/` | `Output/` |

The source folder contains original captured files, every page image, and raw OCR. Preserve each original source filename, append material, and preserve
apparent duplicates. Kanoonak-created pages or text use `الصفحة 001.jpg` or
`النص الخام للصفحة 001.txt` by default, or concise English names in
explicit-English cases. The record folder contains source-linked logical
documents reconstructed from the pages; use short names such as
`الحكم المستأنف.md` and `صحيفة الاستئناف.md`, or concise English equivalents.
A duplicate may be omitted from reconstruction but not deleted from source.

Create work files only when their stage produces useful work. The DOCX
reference alone owns ruling replacement and archive numbering. Add no root
bootstrap, workspace guide, case schema, lifecycle state, taxonomy, validator,
generic notes, counter, ledger, sidecar, naming-preference, or compatibility
file. The existing files show current state. Write each useful result incrementally to its established case folder.

## Synchronize the task title

Listing, disambiguation, selection, destination proposal, and confirmation do
not trigger a rename. After the first substantive case-specific write succeeds
in any established case subfolder, immediately rename the current ChatGPT task
to the exact filesystem-safe case-folder leaf. Perform this rename once per
ChatGPT task. Do not abbreviate, translate, embellish, or regenerate that sole
source of truth.
The one-case-per-task binding remains unchanged. If the host cannot rename the
task, state the exact title the user should apply and continue; never discard,
delay, or mislabel case materials because renaming was unavailable.

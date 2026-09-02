# Local case record

This reference is the sole authority for proving the local parent, confirming
the first save, and maintaining the four-folder case record. Substantive work
on a selected case requires local writing. Listing cases and resolving which
case the user means may happen first; retrieving, reading, or analyzing case
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

Choose one filesystem-safe case leaf from the selected authenticated case's
human-readable name, confined as a direct child of the verified parent. Do not
derive it from a chat-supplied path. Before the first local save for that case
in this chat, show the exact full case folder and ask exactly:

> Save this case here?

Only a clear affirmative answer in the current chat confirms the save. One
affirmative answer covers later saves for that same case in the same chat while
the authenticated case, verified parent, and exact destination remain
unchanged. A decline, unclear answer, case switch, identity change, parent
change, or destination change means write nothing until the current
destination is proved and confirmed again.

## Maintain the record

The case folder contains this record and no root bootstrap, workspace guide,
case schema, lifecycle state, taxonomy, or validator:

```text
<verified parent>/<case>/
├── Source/
├── Record/
├── Work/
└── Output/
    └── النسخ السابقة/
```

- `Source/` contains original captured files, every page image, and raw OCR as
  received. Append new material and preserve apparent duplicates.
- `Record/` contains source-linked logical documents reconstructed from the
  pages. A duplicate may be excluded from reconstruction without being deleted
  from `Source/`.
- `Work/` contains `case-brief.md`, `decision.md`, `research.md`, and
  `exemplars.md`, created or updated only when their stage produces useful
  work. Do not create a generic review-notes or workflow-state file.
- `Output/` contains the current editable ruling and its automatically archived
  prior DOCX versions under `النسخ السابقة/`. The DOCX reference alone owns
  their names and replacement procedure.

Write useful results incrementally: acquisition updates `Source/`,
reconstruction updates `Record/`, analysis and choices update `Work/`, and a
ruling revision updates `Output/`. Files show what work exists; do not add a
counter, status ledger, preflight record, sidecar, or compatibility file.

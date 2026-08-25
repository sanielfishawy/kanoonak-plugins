# Kanoonak

Kanoonak adds authenticated Egyptian labor-law case-preparation and judicial-drafting workflows to your AI app. The workflows use your own private Kanoonak account through the stable remote service at https://kanoonak-mcp.com/mcp.

## Install

1. Open **Plugins**, choose **Add marketplace**, and enter `https://github.com/sanielfishawy/kanoonak-plugins` as **Source**.
2. Set **Git ref** to `main`, leave **Sparse paths** empty, and add the marketplace.
3. Install **Kanoonak** and complete Kanoonak sign-in when prompted. If sign-in is cancelled, retry it from the installed connection; repository access alone does not grant access to any case.
4. Fully quit and reopen Codex, then open a fresh task.
5. Confirm that exactly two Kanoonak skills—`open-kanoonak-case` and `draft-labor-appellate-ruling`—and one `kanoonak` MCP connection are available.
6. For the installation check, invoke only `kanoonak_ping`. Do not open or upload a real case.

If **Add marketplace** reports `program not found` while cloning, Codex could not find Git. Install Git for Windows, fully quit and reopen Codex, and retry the same Plugins UI steps. A GitHub account is not required for this public marketplace.

## Identity and privacy

Each user signs in separately. A dedicated identity is isolated, so cases belonging to another identity may not appear. Before any future real-data use, capture and MCP must resolve to the same identity.

> Privacy notice: Installing Kanoonak does not grant access to case data. Each
> user signs in separately. Do not upload a real case until the capture
> experience displays the approved privacy and retention notice and records
> your acknowledgment.

## Update

This marketplace tracks `main`. To receive an update, fully quit and reopen Codex, then open a fresh task and check the loaded Kanoonak version and inventory there. An existing task may retain the version it loaded. No update button is expected.

If the version is still old after a complete restart and a fresh task, use this last-resort recovery: remove and re-add the same marketplace with the Source, Git ref, and empty Sparse paths shown above; reinstall Kanoonak; and sign in again if prompted. This can require a new connection code. Removing or reinstalling the plugin does not delete Kanoonak case data.

## Document-runtime repair

Basic installation, sign-in, and `kanoonak_ping` do not require the document runtime. If document drafting reports that the bundled runtime or `python-docx==1.2.0` is unavailable:

1. Open **Settings → Workspace Dependencies**.
2. Enable **Codex dependencies** and choose **Reinstall**.
3. Allow approximately 0.5 GB for the one-time Windows x64 download, wait for a successful installation, fully quit and reopen Codex, and open a fresh Windows-native task.
4. Ask Codex to resolve its managed Workspace Dependencies and confirm that the returned bundled Python imports `docx` at exactly version `1.2.0` and that the Documents capability is available in the fresh task.

Use only the Python returned by Codex's managed Workspace Dependencies—not `py`, system Python, or a repository virtual environment. Do not install Python or `python-docx` separately, and do not install the Documents plugin as a runtime repair. If **Workspace Dependencies** is absent, update the Windows app, fully restart it, and retry. If installation or diagnosis reports an error, stop and preserve the exact diagnostic.

This documented runtime repair is currently for Windows x64. If Windows reports ARM64, stop and preserve the diagnostic rather than installing a separate runtime.

## Remove

Uninstalling the plugin removes the local plugin. It does not delete Kanoonak case data, and it is not promised to revoke or forget OAuth state. Connection and sign-out management are separate.

Product information is available at https://kanoonak.com.

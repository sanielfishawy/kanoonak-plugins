# Kanoonak

Kanoonak adds authenticated Egyptian labor-law case-preparation and judicial-drafting workflows to your AI app. The workflows use your own private Kanoonak account through the stable remote service at https://kanoonak-mcp.com/mcp.

## Install

1. Run `codex plugin marketplace add sanielfishawy/kanoonak-plugins --ref main`.
2. Open the plugin browser, choose the **Kanoonak** marketplace, and install **kanoonak**.
3. Complete Kanoonak sign-in when prompted. If sign-in is cancelled, retry it from the installed connection; repository access alone does not grant access to any case.
4. Restart the app, open a fresh Work chat, and confirm that exactly two Kanoonak skills—`open-kanoonak-case` and `draft-labor-appellate-ruling`—and one `kanoonak` MCP connection are available.
5. For the installation check, invoke only `kanoonak_ping`. Do not open or upload a real case.

If the marketplace-add command requires GitHub authentication or a separate Git setup, stop and report that limitation. Do not use a ZIP, manual file copy, or private App mapping as a fallback.

## Identity and privacy

Each user signs in separately. A dedicated identity is isolated, so cases belonging to another identity may not appear. Before any future real-data use, capture and MCP must resolve to the same identity.

> Privacy notice: Installing Kanoonak does not grant access to case data. Each
> user signs in separately. Do not upload a real case until the capture
> experience displays the approved privacy and retention notice and records
> your acknowledgment.

## Update

Run `codex plugin marketplace upgrade kanoonak`, then `codex plugin add kanoonak@kanoonak` to select the refreshed version. Restart the app and open a fresh chat before checking the installed version and connection inventory.

## Remove or reinstall

Uninstalling the plugin removes the local plugin. It does not delete Kanoonak case data, and it is not promised to revoke or forget OAuth state. Connection and sign-out management are separate. Reinstall from the **Kanoonak** marketplace and complete sign-in if prompted.

Product information is available at https://kanoonak.com.

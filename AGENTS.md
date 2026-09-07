# Project FALCON Repository Instructions

## Scope and preservation

- Preserve user-authored work already present in the working tree.
- Do not revert, overwrite, or reformat unrelated changes.
- Include existing changes in a commit only when they belong to the requested FALCON update.
- Keep changes focused on the requested behavior, documentation, or validation work.

## Validation

- Run the narrowest relevant validation after editing.
- For backend changes, run `PYTHONPATH=edge python3 -m unittest discover -s edge/tests -v`.
- For dashboard changes, run `npm run build` from `dashboard-next/`.
- For thesis or DOCX changes, compile and run the relevant updater, then inspect the generated document text.
- Run `git diff --check` before committing.
- Do not describe simulated, planned, or unvalidated hardware as field-deployed or production-ready.

## Git and backup

- After completing and verifying a requested production update, commit the relevant changes and push the current branch to `origin`.
- Use a focused commit message that describes the actual update.
- Confirm the final branch is synchronized with `origin` and the working tree is clean.

## Files that must not be committed

- Temporary browser profiles and caches.
- Generated preview screenshots or unrelated media exports.
- Local databases and runtime telemetry files.
- Secrets, credentials, API keys, SIM details, and private certificates.
- Unrelated machine-specific files or generated build output unless the task explicitly requires them.

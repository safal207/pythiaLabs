# GitHub ↔ Gmail Sync Runbook

This runbook operationalizes [`GITHUB_GMAIL_SYNC_PROTOCOL.md`](./GITHUB_GMAIL_SYNC_PROTOCOL.md).

## Safety model

The workflow is manual and read-only by default.

- It never posts GitHub comments or reactions.
- Gmail only discovers candidate events.
- GitHub verifies comment identity and current content.
- Unverified events can appear in the report but cannot be appended to the journal.
- The journal changes only when `apply=true` is explicitly selected.

## Run with the example fixture

1. Open **Actions**.
2. Select **GitHub Gmail event sync**.
3. Choose **Run workflow**.
4. Keep:
   - `source=file`
   - `candidate_file=data/github-gmail-event-candidates.example.jsonl`
   - `apply=false`
5. Download the `github-gmail-sync-report` artifact.

## Enable Gmail mode

Configure either:

- `GMAIL_ACCESS_TOKEN`, or
- all three refresh-token secrets:
  - `GMAIL_CLIENT_ID`
  - `GMAIL_CLIENT_SECRET`
  - `GMAIL_REFRESH_TOKEN`

The Gmail credential needs read-only access to the mailbox. Do not grant send, modify, or delete scopes.

Then run the workflow with:

- `source=gmail`
- a narrow query such as `newer_than:1d from:notifications@github.com`
- `apply=false` for the first real run

## Review the report

The report groups events into:

- `needs-reply`
- `needs-code-fix`
- `new-important`
- `duplicate`
- `closed-no-action`

A direct mention becomes `needs-reply` only after the corresponding GitHub comment is successfully retrieved.

## Apply journal changes

After reviewing a dry run, rerun with `apply=true`.

Only non-duplicate comments with `verification_status=verified` are appended to:

```text
data/github-gmail-event-journal.jsonl
```

The workflow commits journal changes to the branch from which it was manually started.

## Local test

```bash
python -m unittest discover -s tests -p 'test_sync_github_gmail_events.py' -v
```

## Local dry run

```bash
python scripts/sync_github_gmail_events.py \
  --source file \
  --candidate-file data/github-gmail-event-candidates.example.jsonl \
  --journal data/github-gmail-event-journal.jsonl
```

## Governing boundary

> Gmail detects. GitHub verifies. Only verified events may mutate the journal.

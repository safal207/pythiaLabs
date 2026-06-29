# GitHub ↔ Gmail Sync Protocol

## Purpose

Use Gmail as a **notification radar** and GitHub as the **source of truth**.

The goal is to:

- detect new activity quickly;
- reconstruct the real thread state;
- avoid duplicate replies;
- distinguish discussion from code-action items;
- keep a durable record of what was reviewed, answered, or deferred.

---

## Core rule

> Gmail reports that something may have changed.  
> GitHub confirms what actually changed.  
> The event journal records what we did about it.

---

## Source roles

### Gmail

Gmail is used to detect:

- new issue or PR comments;
- mentions;
- review feedback;
- CI status changes;
- issue or PR state changes;
- follow-up messages in active threads.

Gmail is **not** treated as authoritative for final thread state because:

- several emails may describe the same GitHub event;
- close/reopen/review notifications may arrive separately;
- email ordering may differ from actual thread ordering;
- snippets may be truncated;
- a later GitHub comment may already supersede the email.

### GitHub

GitHub is used to verify:

- the complete comment body;
- the actual chronological order;
- the current issue or PR state;
- whether we already replied;
- whether a newer comment supersedes the notification;
- whether the event requires a reply, reaction, code fix, review, or no action.

---

## Unique event key

The primary deduplication key is:

```text
repository + issue_or_pr_number + comment_id
```

Example:

```text
langchain-ai/langgraph + 5672 + 4835616520
```

Compact form:

```text
langchain-ai/langgraph#5672:4835616520
```

For review comments:

```text
repository + pr_number + review_comment_id
```

For CI-only events:

```text
repository + workflow_run_id + job_or_status
```

---

## Processing workflow

### Step 1 — Scan Gmail

Search recent GitHub notifications and group them by:

```text
repository + issue/PR number
```

### Step 2 — Remove obvious noise

Ignore or collapse:

- duplicate emails for the same comment;
- test comments;
- repeated CI notifications for the same failed run;
- push notifications already reflected in the PR;
- separate “closed/completed” emails when the thread already shows the final state;
- bot summaries that repeat inline findings;
- older notifications superseded by newer comments.

### Step 3 — Open GitHub

For each remaining thread, verify:

- latest comment;
- full context;
- current state;
- whether we already replied;
- whether a later message changed the meaning;
- whether the item is discussion or implementation work.

### Step 4 — Classify the event

Use one status:

- `new-important`
- `needs-reply`
- `needs-reaction`
- `needs-code-fix`
- `needs-review`
- `already-answered`
- `duplicate`
- `superseded`
- `informational`
- `closed-no-action`

### Step 5 — Take one action only

Possible actions:

- reply on GitHub;
- add a reaction;
- fix code;
- update a PR;
- mark as informational;
- do nothing.

Never send more than one reply for the same GitHub comment ID.

### Step 6 — Record the result

Every processed event should be written to the event journal.

---

## Event journal schema

| Field | Description |
|---|---|
| `event_key` | Stable deduplication key |
| `repository` | `owner/repo` |
| `thread_type` | `issue` or `pr` |
| `thread_number` | Issue or PR number |
| `comment_id` | GitHub comment/review ID |
| `author` | Comment author |
| `detected_via` | Usually `gmail` |
| `verified_via` | Usually `github` |
| `status` | Classification |
| `action` | What was done |
| `response_comment_id` | Our reply ID, if any |
| `processed_at` | Timestamp |
| `notes` | Short explanation |

Example:

| event_key | author | status | action |
|---|---|---|---|
| `langchain-ai/langgraph#5672:4835616520` | Tuttotorna | `already-answered` | no action |
| `ag2ai/ag2#2967:4835171029` | babyblueviper1 | `needs-reply` | reply |
| `safal207/LS#766:3493488041` | CodeRabbit | `needs-code-fix` | patch code |

---

## Reply rule

Before replying, confirm all of the following:

- the comment is still current;
- no newer reply already covers the point;
- we have not already answered it;
- the reply adds new technical value;
- the thread accepts comments from the integration;
- the event is not primarily a code-fix task.

---

## Output format for summaries

When presenting the synchronized result, use these sections:

### New and important
Only genuinely new state changes.

### Needs reply
Comments where a response adds value.

### Needs action in code
Review or CI findings that should not be answered with prose.

### Already handled
Events already answered, reacted to, merged, closed, or superseded.

### Duplicates ignored
Repeated Gmail notifications or bot noise.

---

## Governing principle

> Not every email is a new event.  
> A new event exists only when the verified GitHub thread state has changed.

And:

> Gmail detects. GitHub verifies. The journal preserves continuity.

#!/usr/bin/env python3
"""Build a deduplicated Gmail→GitHub event report.

Default mode is read-only. ``--apply`` appends only GitHub-verified comments to
``data/github-gmail-event-journal.jsonl``. No replies or reactions are sent.
"""

from __future__ import annotations

import argparse
import base64
import dataclasses
import datetime as dt
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

COMMENT_URL = re.compile(
    r"https://github\.com/(?P<repo>[\w.-]+/[\w.-]+)/(?P<kind>issues|pull)/"
    r"(?P<number>\d+)#(?P<anchor>issuecomment|discussion_r)-?(?P<comment>\d+)"
)
SUBJECT_THREAD = re.compile(
    r"\[(?P<repo>[\w.-]+/[\w.-]+)\].*?"
    r"\((?P<kind>Issue|PR|Pull Request)\s*#(?P<number>\d+)\)",
    re.IGNORECASE,
)
AUTHOR = re.compile(r"(?P<author>[\w.-]+) left a comment", re.IGNORECASE)
MENTION = re.compile(r"(?<![\w-])@safal207(?![\w-])", re.IGNORECASE)
TEST_ONLY = re.compile(r"^\s*test(?: comment)?(?: from [^\n]+)?\s*$", re.IGNORECASE)


class SyncError(RuntimeError):
    pass


@dataclasses.dataclass(frozen=True)
class Candidate:
    gmail_message_id: str
    repository: str
    thread_type: str
    thread_number: int
    comment_id: int | None
    comment_kind: str | None
    author: str | None
    subject: str
    snippet: str
    body: str
    detected_at: str | None
    github_url: str | None

    @property
    def event_key(self) -> str:
        suffix = str(self.comment_id) if self.comment_id is not None else f"gmail:{self.gmail_message_id}"
        return f"{self.repository}#{self.thread_number}:{suffix}"


@dataclasses.dataclass(frozen=True)
class Verification:
    status: str
    github_url: str | None
    author: str | None
    body: str | None
    error: str | None = None


@dataclasses.dataclass(frozen=True)
class Decision:
    event_key: str
    status: str
    action: str
    reason: str
    candidate: Candidate
    verification: Verification


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SyncError(f"invalid JSONL at {path}:{line_no}: {exc}") from exc
        if not isinstance(value, dict):
            raise SyncError(f"expected object at {path}:{line_no}")
        rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]], *, append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a" if append else "w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n")


def parse_candidate(row: Mapping[str, Any]) -> Candidate | None:
    message_id = str(row.get("gmail_message_id") or row.get("id") or "").strip()
    if not message_id:
        raise SyncError("candidate is missing gmail_message_id/id")
    subject = html.unescape(str(row.get("subject") or ""))
    snippet = html.unescape(str(row.get("snippet") or ""))
    body = html.unescape(str(row.get("body") or ""))
    combined = "\n".join((subject, snippet, body))

    match = COMMENT_URL.search(combined)
    if match:
        repository = match.group("repo")
        thread_type = "issue" if match.group("kind") == "issues" else "pr"
        thread_number = int(match.group("number"))
        comment_id = int(match.group("comment"))
        comment_kind = "issue_comment" if match.group("anchor") == "issuecomment" else "review_comment"
        github_url = match.group(0)
    else:
        match = SUBJECT_THREAD.search(subject)
        if not match:
            return None
        repository = match.group("repo")
        thread_type = "issue" if match.group("kind").lower() == "issue" else "pr"
        thread_number = int(match.group("number"))
        raw_comment_id = row.get("comment_id")
        comment_id = int(raw_comment_id) if raw_comment_id not in (None, "") else None
        comment_kind = str(row.get("comment_kind") or "") or None
        github_url = str(row.get("github_url") or "") or None

    author_match = AUTHOR.search(combined)
    author = str(row.get("author") or "").strip() or (
        author_match.group("author") if author_match else None
    )
    return Candidate(
        gmail_message_id=message_id,
        repository=repository,
        thread_type=thread_type,
        thread_number=thread_number,
        comment_id=comment_id,
        comment_kind=comment_kind,
        author=author,
        subject=subject,
        snippet=snippet,
        body=body,
        detected_at=str(row.get("detected_at") or row.get("email_ts") or "") or None,
        github_url=github_url,
    )


def http_json(
    url: str,
    *,
    headers: Mapping[str, str] | None = None,
    form: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    request_headers = {"User-Agent": "pythiaLabs-github-gmail-sync/0.1", **(headers or {})}
    data = urllib.parse.urlencode(form).encode() if form else None
    if form:
        request_headers["Content-Type"] = "application/x-www-form-urlencoded"
    request = urllib.request.Request(url, data=data, headers=request_headers, method="POST" if form else "GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            result = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise SyncError(f"HTTP {exc.code} for {url}: {detail[:300]}") from exc
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise SyncError(f"request failed for {url}: {exc}") from exc
    if not isinstance(result, dict):
        raise SyncError(f"expected JSON object from {url}")
    return result


def gmail_token(env: Mapping[str, str]) -> str:
    if env.get("GMAIL_ACCESS_TOKEN", "").strip():
        return env["GMAIL_ACCESS_TOKEN"].strip()
    names = ("GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN")
    missing = [name for name in names if not env.get(name, "").strip()]
    if missing:
        raise SyncError("gmail mode missing: " + ", ".join(missing))
    response = http_json(
        "https://oauth2.googleapis.com/token",
        form={
            "client_id": env["GMAIL_CLIENT_ID"],
            "client_secret": env["GMAIL_CLIENT_SECRET"],
            "refresh_token": env["GMAIL_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        },
    )
    token = str(response.get("access_token") or "")
    if not token:
        raise SyncError("OAuth response had no access_token")
    return token


def decode_part(value: str) -> str:
    try:
        return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4)).decode(errors="replace")
    except ValueError:
        return ""


def gmail_text(payload: Mapping[str, Any]) -> str:
    chunks: list[str] = []

    def visit(part: Mapping[str, Any]) -> None:
        mime = str(part.get("mimeType") or "")
        data = (part.get("body") or {}).get("data")
        if isinstance(data, str) and mime in {"text/plain", "text/html"}:
            text = decode_part(data)
            chunks.append(html.unescape(re.sub(r"<[^>]+>", " ", text)) if mime == "text/html" else text)
        for child in part.get("parts") or []:
            if isinstance(child, Mapping):
                visit(child)

    visit(payload)
    return "\n".join(chunk.strip() for chunk in chunks if chunk.strip())


def fetch_gmail(query: str, max_results: int) -> list[dict[str, Any]]:
    headers = {"Authorization": f"Bearer {gmail_token(os.environ)}"}
    params = urllib.parse.urlencode({"q": query, "maxResults": max_results})
    listing = http_json(f"https://gmail.googleapis.com/gmail/v1/users/me/messages?{params}", headers=headers)
    rows: list[dict[str, Any]] = []
    for item in listing.get("messages") or []:
        message_id = str(item.get("id") or "")
        if not message_id:
            continue
        message = http_json(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full",
            headers=headers,
        )
        payload = message.get("payload") or {}
        header_map = {
            str(header.get("name") or "").lower(): str(header.get("value") or "")
            for header in payload.get("headers") or []
            if isinstance(header, Mapping)
        }
        rows.append(
            {
                "gmail_message_id": message_id,
                "subject": header_map.get("subject", ""),
                "snippet": message.get("snippet", ""),
                "body": gmail_text(payload),
                "detected_at": message.get("internalDate"),
            }
        )
    return rows


def verify_candidate(candidate: Candidate, token: str | None) -> Verification:
    if candidate.comment_id is None:
        return Verification("thread-only", candidate.github_url, candidate.author, None)
    if not token:
        return Verification("unverified", candidate.github_url, candidate.author, None, "GITHUB_TOKEN not provided")
    path = "pulls/comments" if candidate.comment_kind == "review_comment" else "issues/comments"
    endpoint = f"https://api.github.com/repos/{candidate.repository}/{path}/{candidate.comment_id}"
    try:
        response = http_json(
            endpoint,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
    except SyncError as exc:
        return Verification("verification-failed", candidate.github_url, candidate.author, None, str(exc))
    user = response.get("user") or {}
    return Verification(
        "verified",
        str(response.get("html_url") or candidate.github_url or "") or None,
        str(user.get("login") or candidate.author or "") or None,
        str(response.get("body") or ""),
    )


def classify(candidate: Candidate, verification: Verification, existing: set[str]) -> Decision:
    if candidate.event_key in existing:
        return Decision(candidate.event_key, "duplicate", "none", "event_key already exists in the journal", candidate, verification)
    body = verification.body if verification.body is not None else candidate.body
    lowered = "\n".join((candidate.subject, candidate.snippet, body)).lower()
    if TEST_ONLY.fullmatch(body.strip()):
        return Decision(candidate.event_key, "duplicate", "none", "test-only comment", candidate, verification)
    if any(mark in lowered for mark in ("actionable comments posted", "codex review", "p1 badge", "p2 badge")):
        return Decision(candidate.event_key, "needs-code-fix", "review-code", "automated review contains actionable code findings", candidate, verification)
    if any(mark in lowered for mark in ("closed #", "closed as completed", "merged pull request")):
        return Decision(candidate.event_key, "closed-no-action", "none", "thread state notification does not require a prose reply", candidate, verification)
    if verification.status == "verified" and MENTION.search(body):
        return Decision(candidate.event_key, "needs-reply", "draft-reply", "verified comment directly mentions @safal207", candidate, verification)
    reason = (
        "new verified thread event; human classification required"
        if verification.status == "verified"
        else f"event requires human review because verification status is {verification.status}"
    )
    return Decision(candidate.event_key, "new-important", "review", reason, candidate, verification)


def report_row(item: Decision) -> dict[str, Any]:
    candidate, verification = item.candidate, item.verification
    return {
        "event_key": item.event_key,
        "repository": candidate.repository,
        "thread_type": candidate.thread_type,
        "thread_number": candidate.thread_number,
        "comment_id": candidate.comment_id,
        "author": verification.author or candidate.author,
        "status": item.status,
        "recommended_action": item.action,
        "reason": item.reason,
        "verification_status": verification.status,
        "verification_error": verification.error,
        "github_url": verification.github_url or candidate.github_url,
        "gmail_message_id": candidate.gmail_message_id,
        "detected_at": candidate.detected_at,
    }


def journal_row(item: Decision) -> dict[str, Any]:
    row = report_row(item)
    return {
        "event_key": row["event_key"],
        "repository": row["repository"],
        "thread_type": row["thread_type"],
        "thread_number": row["thread_number"],
        "comment_id": row["comment_id"],
        "author": row["author"],
        "detected_via": "gmail",
        "verified_via": "github",
        "status": row["status"],
        "action": "pending" if row["recommended_action"] != "none" else "none",
        "response_comment_id": None,
        "processed_at": now_iso(),
        "notes": row["reason"],
    }


def markdown(decisions: Sequence[Decision]) -> str:
    groups = (
        ("Needs reply", {"needs-reply"}),
        ("Needs action in code", {"needs-code-fix"}),
        ("New and important", {"new-important"}),
        ("Already handled or ignored", {"duplicate", "closed-no-action"}),
    )
    lines = ["# GitHub ↔ Gmail sync report", "", f"Generated: `{now_iso()}`", ""]
    for title, statuses in groups:
        lines += [f"## {title}", ""]
        selected = [item for item in decisions if item.status in statuses]
        if not selected:
            lines += ["_None._", ""]
            continue
        for item in selected:
            url = item.verification.github_url or item.candidate.github_url
            label = f"[{item.event_key}]({url})" if url else item.event_key
            lines.append(f"- {label} — **{item.status}**: {item.reason}")
        lines.append("")
    return "\n".join(lines)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--source", choices=("file", "gmail"), default="file")
    result.add_argument("--candidate-file", type=Path, default=Path("data/github-gmail-event-candidates.jsonl"))
    result.add_argument("--journal", type=Path, default=Path("data/github-gmail-event-journal.jsonl"))
    result.add_argument("--report-jsonl", type=Path, default=Path("artifacts/sync-report.jsonl"))
    result.add_argument("--report-md", type=Path, default=Path("artifacts/sync-report.md"))
    result.add_argument("--gmail-query", default="newer_than:1d from:notifications@github.com")
    result.add_argument("--max-results", type=int, default=50)
    result.add_argument("--apply", action="store_true")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        raw = fetch_gmail(args.gmail_query, args.max_results) if args.source == "gmail" else read_jsonl(args.candidate_file)
        candidates = [candidate for row in raw if (candidate := parse_candidate(row))]
        existing = {str(row["event_key"]) for row in read_jsonl(args.journal) if row.get("event_key")}
        token = os.environ.get("GITHUB_TOKEN", "").strip() or None
        decisions = [classify(candidate, verify_candidate(candidate, token), existing) for candidate in candidates]
        write_jsonl(args.report_jsonl, (report_row(item) for item in decisions))
        args.report_md.parent.mkdir(parents=True, exist_ok=True)
        args.report_md.write_text(markdown(decisions), encoding="utf-8")
        if args.apply:
            verified = [item for item in decisions if item.status != "duplicate" and item.verification.status == "verified"]
            write_jsonl(args.journal, (journal_row(item) for item in verified), append=True)
        counts: dict[str, int] = {}
        for item in decisions:
            counts[item.status] = counts.get(item.status, 0) + 1
        print(json.dumps({"candidates": len(candidates), "counts": counts, "applied": args.apply}))
        return 0
    except SyncError as exc:
        print(f"sync error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Synchronize GitHub notification candidates with a durable event journal.

Gmail is used as a notification source. GitHub is used to verify comment identity
and current content. The script is deliberately non-destructive by default:
it writes a report and only appends to the journal when --apply is supplied.

The script uses only the Python standard library.
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

GITHUB_COMMENT_URL_RE = re.compile(
    r"https://github\.com/(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)"
    r"/(?P<thread_type>issues|pull)/(?P<thread_number>\d+)"
    r"#(?P<anchor>issuecomment|discussion_r)-?(?P<comment_id>\d+)"
)
SUBJECT_THREAD_RE = re.compile(
    r"\[(?P<repository>[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)\].*?"
    r"\((?P<thread_type>Issue|PR|Pull Request)\s*#(?P<thread_number>\d+)\)",
    re.IGNORECASE,
)
AUTHOR_RE = re.compile(r"(?P<author>[A-Za-z0-9_.-]+) left a comment", re.IGNORECASE)
TEST_COMMENT_RE = re.compile(r"^\s*test(?: comment)?(?: from [^\n]+)?\s*$", re.IGNORECASE)
DIRECT_MENTION_RE = re.compile(r"(?<![A-Za-z0-9_-])@safal207(?![A-Za-z0-9_-])", re.IGNORECASE)


class SyncError(RuntimeError):
    """Raised for configuration or remote API failures that should stop a run."""


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
        if self.comment_id is not None:
            return f"{self.repository}#{self.thread_number}:{self.comment_id}"
        return f"{self.repository}#{self.thread_number}:gmail:{self.gmail_message_id}"


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


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SyncError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise SyncError(f"Expected an object at {path}:{line_number}")
            rows.append(value)
    return rows


def write_jsonl(path: Path, rows: Iterable[Mapping[str, Any]], *, append: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with path.open(mode, encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(dict(row), ensure_ascii=False, sort_keys=True) + "\n")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def _extract_text_from_gmail_payload(payload: Mapping[str, Any]) -> str:
    chunks: list[str] = []

    def walk(part: Mapping[str, Any]) -> None:
        mime_type = str(part.get("mimeType") or "")
        body = part.get("body") or {}
        data = body.get("data") if isinstance(body, Mapping) else None
        if isinstance(data, str) and mime_type in {"text/plain", "text/html"}:
            try:
                text = _b64url_decode(data).decode("utf-8", errors="replace")
            except (ValueError, UnicodeDecodeError):
                text = ""
            if mime_type == "text/html":
                text = re.sub(r"<[^>]+>", " ", text)
            chunks.append(html.unescape(text))
        for child in part.get("parts") or []:
            if isinstance(child, Mapping):
                walk(child)

    walk(payload)
    return "\n".join(chunk.strip() for chunk in chunks if chunk.strip())


def _header_map(payload: Mapping[str, Any]) -> dict[str, str]:
    headers: dict[str, str] = {}
    for item in payload.get("headers") or []:
        if not isinstance(item, Mapping):
            continue
        name = str(item.get("name") or "").lower()
        value = str(item.get("value") or "")
        if name:
            headers[name] = value
    return headers


def parse_candidate(record: Mapping[str, Any]) -> Candidate | None:
    message_id = str(record.get("gmail_message_id") or record.get("id") or "").strip()
    subject = html.unescape(str(record.get("subject") or ""))
    snippet = html.unescape(str(record.get("snippet") or ""))
    body = html.unescape(str(record.get("body") or ""))
    detected_at = str(record.get("detected_at") or record.get("email_ts") or "") or None

    if not message_id:
        raise SyncError("Candidate is missing gmail_message_id/id")

    combined = "\n".join([subject, snippet, body])
    url_match = GITHUB_COMMENT_URL_RE.search(combined)
    if url_match:
        repository = url_match.group("repository")
        thread_type = "issue" if url_match.group("thread_type") == "issues" else "pr"
        thread_number = int(url_match.group("thread_number"))
        comment_id = int(url_match.group("comment_id"))
        comment_kind = "issue_comment" if url_match.group("anchor") == "issuecomment" else "review_comment"
        github_url = url_match.group(0)
    else:
        subject_match = SUBJECT_THREAD_RE.search(subject)
        if not subject_match:
            return None
        repository = subject_match.group("repository")
        raw_type = subject_match.group("thread_type").lower()
        thread_type = "issue" if raw_type == "issue" else "pr"
        thread_number = int(subject_match.group("thread_number"))
        comment_id = _optional_int(record.get("comment_id"))
        comment_kind = str(record.get("comment_kind") or "") or None
        github_url = str(record.get("github_url") or "") or None

    author_match = AUTHOR_RE.search(combined)
    author = str(record.get("author") or "").strip() or (
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
        detected_at=detected_at,
        github_url=github_url,
    )


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise SyncError(f"Expected integer comment_id, got {value!r}") from exc


def _http_json(
    url: str,
    *,
    method: str = "GET",
    headers: Mapping[str, str] | None = None,
    data: Mapping[str, str] | None = None,
    timeout: int = 30,
) -> dict[str, Any]:
    request_headers = {"User-Agent": "pythiaLabs-github-gmail-sync/0.1"}
    if headers:
        request_headers.update(headers)
    encoded_data = None
    if data is not None:
        encoded_data = urllib.parse.urlencode(data).encode("utf-8")
        request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
    request = urllib.request.Request(url, data=encoded_data, headers=request_headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise SyncError(f"HTTP {exc.code} for {url}: {detail[:500]}") from exc
    except urllib.error.URLError as exc:
        raise SyncError(f"Network error for {url}: {exc.reason}") from exc
    try:
        result = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise SyncError(f"Non-JSON response from {url}") from exc
    if not isinstance(result, dict):
        raise SyncError(f"Expected JSON object from {url}")
    return result


def gmail_access_token_from_env(env: Mapping[str, str]) -> str:
    direct = env.get("GMAIL_ACCESS_TOKEN", "").strip()
    if direct:
        return direct

    required = ["GMAIL_CLIENT_ID", "GMAIL_CLIENT_SECRET", "GMAIL_REFRESH_TOKEN"]
    missing = [name for name in required if not env.get(name, "").strip()]
    if missing:
        raise SyncError(
            "Gmail mode requires GMAIL_ACCESS_TOKEN or refresh-token credentials: "
            + ", ".join(missing)
        )
    response = _http_json(
        "https://oauth2.googleapis.com/token",
        method="POST",
        data={
            "client_id": env["GMAIL_CLIENT_ID"],
            "client_secret": env["GMAIL_CLIENT_SECRET"],
            "refresh_token": env["GMAIL_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        },
    )
    token = str(response.get("access_token") or "").strip()
    if not token:
        raise SyncError("OAuth token response did not contain access_token")
    return token


def fetch_gmail_records(query: str, env: Mapping[str, str], max_results: int) -> list[dict[str, Any]]:
    token = gmail_access_token_from_env(env)
    headers = {"Authorization": f"Bearer {token}"}
    params = urllib.parse.urlencode({"q": query, "maxResults": max_results})
    listing = _http_json(
        f"https://gmail.googleapis.com/gmail/v1/users/me/messages?{params}", headers=headers
    )
    messages = listing.get("messages") or []
    records: list[dict[str, Any]] = []
    for summary in messages:
        if not isinstance(summary, Mapping) or not summary.get("id"):
            continue
        message_id = str(summary["id"])
        message = _http_json(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full",
            headers=headers,
        )
        payload = message.get("payload") or {}
        if not isinstance(payload, Mapping):
            continue
        headers_map = _header_map(payload)
        records.append(
            {
                "gmail_message_id": message_id,
                "subject": headers_map.get("subject", ""),
                "snippet": message.get("snippet", ""),
                "body": _extract_text_from_gmail_payload(payload),
                "detected_at": message.get("internalDate"),
            }
        )
    return records


def verify_candidate(candidate: Candidate, github_token: str | None) -> Verification:
    if candidate.comment_id is None:
        return Verification(
            status="thread-only",
            github_url=candidate.github_url,
            author=candidate.author,
            body=None,
            error=None,
        )
    if not github_token:
        return Verification(
            status="unverified",
            github_url=candidate.github_url,
            author=candidate.author,
            body=None,
            error="GITHUB_TOKEN not provided",
        )

    if candidate.comment_kind == "review_comment":
        endpoint = (
            f"https://api.github.com/repos/{candidate.repository}/pulls/comments/"
            f"{candidate.comment_id}"
        )
    else:
        endpoint = (
            f"https://api.github.com/repos/{candidate.repository}/issues/comments/"
            f"{candidate.comment_id}"
        )
    try:
        response = _http_json(
            endpoint,
            headers={
                "Authorization": f"Bearer {github_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
    except SyncError as exc:
        return Verification(
            status="verification-failed",
            github_url=candidate.github_url,
            author=candidate.author,
            body=None,
            error=str(exc),
        )

    user = response.get("user") or {}
    author = str(user.get("login") or candidate.author or "") or None
    return Verification(
        status="verified",
        github_url=str(response.get("html_url") or candidate.github_url or "") or None,
        author=author,
        body=str(response.get("body") or ""),
        error=None,
    )


def classify(
    candidate: Candidate,
    verification: Verification,
    existing_event_keys: set[str],
) -> Decision:
    if candidate.event_key in existing_event_keys:
        return Decision(
            candidate.event_key,
            "duplicate",
            "none",
            "event_key already exists in the journal",
            candidate,
            verification,
        )

    authoritative_body = verification.body if verification.body is not None else candidate.body
    normalized_body = authoritative_body.strip()
    combined = "\n".join([candidate.subject, candidate.snippet, authoritative_body])
    lowered = combined.lower()

    if TEST_COMMENT_RE.fullmatch(normalized_body):
        return Decision(
            candidate.event_key,
            "duplicate",
            "none",
            "test-only comment",
            candidate,
            verification,
        )

    if any(marker in lowered for marker in ("actionable comments posted", "codex review", "p1 badge", "p2 badge")):
        return Decision(
            candidate.event_key,
            "needs-code-fix",
            "review-code",
            "automated review contains actionable code findings",
            candidate,
            verification,
        )

    if any(marker in lowered for marker in ("closed #", "closed as completed", "merged pull request")):
        return Decision(
            candidate.event_key,
            "closed-no-action",
            "none",
            "thread state notification does not require a prose reply",
            candidate,
            verification,
        )

    if DIRECT_MENTION_RE.search(authoritative_body):
        return Decision(
            candidate.event_key,
            "needs-reply",
            "draft-reply",
            "verified comment directly mentions @safal207",
            candidate,
            verification,
        )

    return Decision(
        candidate.event_key,
        "new-important",
        "review",
        "new verified thread event; human classification required",
        candidate,
        verification,
    )


def decision_to_report_row(decision: Decision) -> dict[str, Any]:
    candidate = decision.candidate
    verification = decision.verification
    return {
        "event_key": decision.event_key,
        "repository": candidate.repository,
        "thread_type": candidate.thread_type,
        "thread_number": candidate.thread_number,
        "comment_id": candidate.comment_id,
        "author": verification.author or candidate.author,
        "status": decision.status,
        "recommended_action": decision.action,
        "reason": decision.reason,
        "verification_status": verification.status,
        "verification_error": verification.error,
        "github_url": verification.github_url or candidate.github_url,
        "gmail_message_id": candidate.gmail_message_id,
        "detected_at": candidate.detected_at,
    }


def decision_to_journal_row(decision: Decision) -> dict[str, Any]:
    candidate = decision.candidate
    verification = decision.verification
    return {
        "event_key": decision.event_key,
        "repository": candidate.repository,
        "thread_type": candidate.thread_type,
        "thread_number": candidate.thread_number,
        "comment_id": candidate.comment_id,
        "author": verification.author or candidate.author,
        "detected_via": "gmail",
        "verified_via": "github" if verification.status == "verified" else verification.status,
        "status": decision.status,
        "action": "pending" if decision.action != "none" else "none",
        "response_comment_id": None,
        "processed_at": utc_now_iso(),
        "notes": decision.reason,
    }


def render_markdown(decisions: Sequence[Decision]) -> str:
    groups = [
        ("Needs reply", {"needs-reply"}),
        ("Needs action in code", {"needs-code-fix"}),
        ("New and important", {"new-important"}),
        ("Already handled or ignored", {"duplicate", "closed-no-action"}),
    ]
    lines = ["# GitHub ↔ Gmail sync report", "", f"Generated: `{utc_now_iso()}`", ""]
    for title, statuses in groups:
        lines.extend([f"## {title}", ""])
        selected = [item for item in decisions if item.status in statuses]
        if not selected:
            lines.extend(["_None._", ""])
            continue
        for item in selected:
            candidate = item.candidate
            verification = item.verification
            url = verification.github_url or candidate.github_url
            label = item.event_key
            if url:
                label = f"[{label}]({url})"
            lines.append(f"- {label} — **{item.status}**: {item.reason}")
        lines.append("")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("file", "gmail"), default="file")
    parser.add_argument(
        "--candidate-file",
        type=Path,
        default=Path("data/github-gmail-event-candidates.jsonl"),
    )
    parser.add_argument(
        "--journal",
        type=Path,
        default=Path("data/github-gmail-event-journal.jsonl"),
    )
    parser.add_argument("--report-jsonl", type=Path, default=Path("artifacts/sync-report.jsonl"))
    parser.add_argument("--report-md", type=Path, default=Path("artifacts/sync-report.md"))
    parser.add_argument(
        "--gmail-query",
        default="newer_than:1d from:notifications@github.com",
    )
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--apply", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.source == "gmail":
            raw_records = fetch_gmail_records(args.gmail_query, os.environ, args.max_results)
        else:
            raw_records = read_jsonl(args.candidate_file)

        candidates = [candidate for row in raw_records if (candidate := parse_candidate(row))]
        journal_rows = read_jsonl(args.journal)
        existing_event_keys = {
            str(row.get("event_key")) for row in journal_rows if row.get("event_key")
        }
        github_token = os.environ.get("GITHUB_TOKEN", "").strip() or None
        decisions = [
            classify(candidate, verify_candidate(candidate, github_token), existing_event_keys)
            for candidate in candidates
        ]

        write_jsonl(args.report_jsonl, (decision_to_report_row(item) for item in decisions))
        args.report_md.parent.mkdir(parents=True, exist_ok=True)
        args.report_md.write_text(render_markdown(decisions), encoding="utf-8")

        if args.apply:
            appendable = [
                item
                for item in decisions
                if item.status != "duplicate"
                and item.verification.status in {"verified", "thread-only"}
            ]
            write_jsonl(
                args.journal,
                (decision_to_journal_row(item) for item in appendable),
                append=True,
            )

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

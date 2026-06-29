from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import sync_github_gmail_events as sync


class CandidateParsingTests(unittest.TestCase):
    def test_parses_issue_comment_url(self) -> None:
        candidate = sync.parse_candidate(
            {
                "gmail_message_id": "m1",
                "subject": "Re: [langchain-ai/langgraph] Example (Issue #5672)",
                "body": (
                    "Tuttotorna left a comment "
                    "(https://github.com/langchain-ai/langgraph/issues/5672"
                    "#issuecomment-4835616520)"
                ),
            }
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.event_key, "langchain-ai/langgraph#5672:4835616520")
        self.assertEqual(candidate.author, "Tuttotorna")
        self.assertEqual(candidate.comment_kind, "issue_comment")

    def test_subject_fallback_without_comment_url(self) -> None:
        candidate = sync.parse_candidate(
            {
                "gmail_message_id": "m2",
                "subject": "Re: [openai/codex] Something happened (Issue #28495)",
                "body": "Closed #28495 as completed.",
            }
        )
        self.assertIsNotNone(candidate)
        assert candidate is not None
        self.assertEqual(candidate.repository, "openai/codex")
        self.assertEqual(candidate.event_key, "openai/codex#28495:gmail:m2")


class ClassificationTests(unittest.TestCase):
    def make_candidate(self, body: str = "@safal207 useful point"):
        return sync.Candidate(
            gmail_message_id="m1",
            repository="owner/repo",
            thread_type="issue",
            thread_number=1,
            comment_id=10,
            comment_kind="issue_comment",
            author="author",
            subject="subject",
            snippet="",
            body=body,
            detected_at=None,
            github_url="https://github.com/owner/repo/issues/1#issuecomment-10",
        )

    def test_existing_event_is_duplicate(self) -> None:
        candidate = self.make_candidate()
        verification = sync.Verification("verified", candidate.github_url, "author", candidate.body)
        decision = sync.classify(candidate, verification, {candidate.event_key})
        self.assertEqual(decision.status, "duplicate")

    def test_direct_mention_needs_reply(self) -> None:
        candidate = self.make_candidate()
        verification = sync.Verification("verified", candidate.github_url, "author", candidate.body)
        decision = sync.classify(candidate, verification, set())
        self.assertEqual(decision.status, "needs-reply")

    def test_unverified_direct_mention_stays_for_review(self) -> None:
        candidate = self.make_candidate()
        verification = sync.Verification(
            "unverified", candidate.github_url, "author", None, "token missing"
        )
        decision = sync.classify(candidate, verification, set())
        self.assertEqual(decision.status, "new-important")

    def test_review_feedback_needs_code_fix(self) -> None:
        candidate = self.make_candidate("Actionable comments posted: 2")
        verification = sync.Verification("verified", candidate.github_url, "bot", candidate.body)
        decision = sync.classify(candidate, verification, set())
        self.assertEqual(decision.status, "needs-code-fix")

    def test_test_comment_is_ignored(self) -> None:
        candidate = self.make_candidate("Test comment from HeartFlow")
        verification = sync.Verification("verified", candidate.github_url, "author", candidate.body)
        decision = sync.classify(candidate, verification, set())
        self.assertEqual(decision.status, "duplicate")


class JsonlTests(unittest.TestCase):
    def test_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "events.jsonl"
            sync.write_jsonl(path, [{"event_key": "a"}, {"event_key": "b"}])
            self.assertEqual(sync.read_jsonl(path), [{"event_key": "a"}, {"event_key": "b"}])


if __name__ == "__main__":
    unittest.main()

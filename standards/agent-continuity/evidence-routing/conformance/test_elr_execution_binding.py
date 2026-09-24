from __future__ import annotations

import unittest

from execution_binding import check_execution_binding

ALLOW_HASH = "sha256:" + ("a" * 64)


class ELRExecutionBindingTests(unittest.TestCase):
    def test_31_matching_content_generation_and_unused_nonce_is_ready(self):
        expected = {
            "state_hash": ALLOW_HASH,
            "generation": 41,
            "use_nonce": "use-41-001",
        }
        observed = {
            "state_hash": ALLOW_HASH,
            "generation": 41,
        }

        status, detail = check_execution_binding(expected, observed, set())

        self.assertEqual(status, "EXECUTION_BINDING_READY")
        self.assertEqual(detail["generation"], 41)
        self.assertEqual(detail["use_nonce"], "use-41-001")

    def test_32_aba_same_hash_after_transition_cycle_is_rejected(self):
        # Synthetic authorization cycle:
        # generation 41: ALLOW -> 42: DENY -> 43: ALLOW.
        # The byte-identical ALLOW state restores the same content hash, but the
        # old proof/attempt is bound to a different authoritative generation.
        expected = {
            "state_hash": ALLOW_HASH,
            "generation": 41,
            "use_nonce": "use-41-001",
        }
        observed_after_aba = {
            "state_hash": ALLOW_HASH,
            "generation": 43,
        }

        status, detail = check_execution_binding(expected, observed_after_aba, set())

        self.assertEqual(status, "BLOCKED_EXECUTION_GENERATION_DRIFT")
        self.assertEqual(detail["expected_generation"], 41)
        self.assertEqual(detail["observed_generation"], 43)
        self.assertEqual(detail["state_hash"], ALLOW_HASH)

    def test_33_consumed_nonce_replay_is_rejected(self):
        expected = {
            "state_hash": ALLOW_HASH,
            "generation": 41,
            "use_nonce": "use-41-001",
        }
        observed = {
            "state_hash": ALLOW_HASH,
            "generation": 41,
        }

        status, detail = check_execution_binding(
            expected,
            observed,
            {"use-41-001"},
        )

        self.assertEqual(status, "BLOCKED_EXECUTION_NONCE_REPLAY")
        self.assertEqual(detail["generation"], 41)
        self.assertEqual(detail["use_nonce"], "use-41-001")


if __name__ == "__main__":
    unittest.main()

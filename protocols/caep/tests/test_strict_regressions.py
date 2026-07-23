from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_caep import load_packet  # noqa: E402
from validate_caep_strict import validate_packet  # noqa: E402


class StrictRegressionTests(unittest.TestCase):
    def test_malformed_sequence_is_reported_without_crash(self):
        packet = load_packet(
            ROOT / "examples" / "hypothetical_sandbox_escape_episode.json"
        )
        packet["records"][1]["sequence"] = None
        errors, _ = validate_packet(packet)
        self.assertTrue(any(".sequence must be an integer" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import base64
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from caep_canonical import (  # noqa: E402
    CANONICALIZATION,
    CanonicalizationError,
    canonical_bytes,
    record_payload,
    strict_json_loads,
)
from export_caep_jsonl import verify_jsonl, write_jsonl  # noqa: E402
from verify_caep_proofs import load_keyset, verify_packet  # noqa: E402

try:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
except ImportError:
    Ed25519PrivateKey = None

ROLES = {
    "authorization": "policy_decision_point",
    "dispatch": "enforcement_point",
    "outcome": "independent_observer",
    "recovery": "incident_controller",
}


def b64url(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


@unittest.skipUnless(Ed25519PrivateKey, "cryptography package is required")
class VerifiedEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads(
            (ROOT / "examples" / "hypothetical_sandbox_escape_episode.json").read_text()
        )
        self.packet["evidence_level"] = "F3"
        self.keys = []
        for record in self.packet["records"]:
            role = ROLES.get(record["record_type"])
            if not role:
                continue
            private_key = Ed25519PrivateKey.generate()
            public_key = private_key.public_key().public_bytes(
                Encoding.Raw, PublicFormat.Raw
            )
            key_id = f"{record['record_type']}-test-key"
            signature = private_key.sign(canonical_bytes(record_payload(record)))
            record["integrity_proof"] = {
                "scheme": f"Ed25519+{CANONICALIZATION}",
                "key_id": key_id,
                "value": b64url(signature),
            }
            self.keys.append(
                {
                    "key_id": key_id,
                    "scheme": "Ed25519",
                    "issuer": record["issuer"],
                    "authority_role": role,
                    "public_key": b64url(public_key),
                }
            )

    def keyset(self, directory: Path):
        path = directory / "keyset.json"
        path.write_text(
            json.dumps({"caep_keyset_version": "0.1.0", "keys": self.keys}),
            encoding="utf-8",
        )
        return load_keyset(path)

    def test_valid_f3_packet_is_verified(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors, warnings = verify_packet(self.packet, self.keyset(Path(tmp)))
        self.assertEqual([], errors)
        self.assertEqual([], warnings)

    def test_tampering_breaks_signature(self):
        self.packet["records"][1]["policy_version"] = "changed-after-signing"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = verify_packet(self.packet, self.keyset(Path(tmp)))
        self.assertTrue(
            any("signature verification failed" in error for error in errors)
        )

    def test_unknown_key_fails_closed(self):
        self.packet["records"][1]["integrity_proof"]["key_id"] = "unknown"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = verify_packet(self.packet, self.keyset(Path(tmp)))
        self.assertTrue(any("unknown key_id" in error for error in errors))

    def test_invalid_base64url_fails_closed(self):
        self.packet["records"][1]["integrity_proof"]["value"] = "not+base64"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = verify_packet(self.packet, self.keyset(Path(tmp)))
        self.assertTrue(any("unsupported characters" in error for error in errors))

    def test_wrong_authority_role_fails_closed(self):
        self.keys[0]["authority_role"] = "independent_observer"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = verify_packet(self.packet, self.keyset(Path(tmp)))
        self.assertTrue(any("authority role must be" in error for error in errors))

    def test_key_reuse_across_roles_is_rejected(self):
        self.keys[1]["public_key"] = self.keys[0]["public_key"]
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "keyset.json"
            path.write_text(
                json.dumps({"caep_keyset_version": "0.1.0", "keys": self.keys})
            )
            with self.assertRaisesRegex(ValueError, "same public key"):
                load_keyset(path)

    def test_jsonl_round_trip_and_payload_tamper_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "episode.jsonl"
            write_jsonl(self.packet, path)
            errors, rebuilt = verify_jsonl(path)
            self.assertEqual([], errors)
            self.assertEqual(self.packet["records"], rebuilt["records"])

            lines = path.read_text().splitlines()
            envelope = json.loads(lines[2])
            envelope["record"]["policy_version"] = "tampered"
            lines[2] = json.dumps(envelope, separators=(",", ":"))
            path.write_text("\n".join(lines) + "\n")
            errors, _ = verify_jsonl(path)
            self.assertTrue(
                any("record_digest does not match" in error for error in errors)
            )

    def test_jsonl_signature_tamper_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "episode.jsonl"
            write_jsonl(self.packet, path)
            lines = path.read_text().splitlines()
            envelope = json.loads(lines[2])
            proof = envelope["record"]["integrity_proof"]
            proof["value"] = ("A" if proof["value"][0] != "A" else "B") + proof["value"][1:]
            lines[2] = json.dumps(envelope, separators=(",", ":"))
            path.write_text("\n".join(lines) + "\n")
            errors, _ = verify_jsonl(path)
            self.assertTrue(
                any("record_digest does not match" in error for error in errors)
            )


class CanonicalizationTests(unittest.TestCase):
    def test_floats_are_rejected(self):
        with self.assertRaisesRegex(CanonicalizationError, "floating-point"):
            canonical_bytes({"value": 1.5})

    def test_non_ascii_object_member_names_are_rejected(self):
        with self.assertRaisesRegex(CanonicalizationError, "non-ASCII"):
            canonical_bytes({"ключ": "value"})

    def test_duplicate_json_members_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "duplicate JSON member"):
            strict_json_loads('{"a":1,"a":2}')

    def test_non_finite_json_constants_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "non-finite JSON constant"):
            strict_json_loads('{"value":NaN}')


if __name__ == "__main__":
    unittest.main()

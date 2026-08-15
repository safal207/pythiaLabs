from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "lotus_ltp_acceptance.py"
SPEC = importlib.util.spec_from_file_location("lotus_ltp_acceptance", MODULE_PATH)
assert SPEC and SPEC.loader
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


def fixture() -> tuple[dict, dict, dict]:
    transition = "airbnb-garden-test"
    subject = "airbnb-listing-1418689551881927394"
    action_digest = "sha256:" + "1" * 64
    binding_digest = "sha256:" + "2" * 64
    auth_record = {
        "transition_id": transition,
        "subject_id": subject,
        "action_identity_digest": action_digest,
        "binding_digest": binding_digest,
        "decision": "ALLOW",
        "current_state": "ACTIVE",
        "scope": {
            "kind": "public_readonly_airbnb_currency_history_probe",
            "prohibited": ["login", "host_contact", "payment", "reservation", "external_submission"],
        },
        "authority": {"external_submission": False, "deployment": False, "merge": False},
    }
    authorization = {"record": auth_record, "record_ref": adapter.sha256_ref(auth_record)}
    run_authority = {
        "mode": "audit_only",
        "ownership": False,
        "approval": False,
        "execution": False,
        "delivery": False,
        "external_submission": False,
        "deployment": False,
        "merge": False,
        "product_verdict_override": False,
    }
    advisory_authority = dict(run_authority)
    advisory_authority["mode"] = "advisory_only"
    result = {
        "run": {
            "authority": run_authority,
            "live_garden_probe_confirmed": True,
            "safe_readonly_probe": True,
            "probe_summary": {
                "confirmed_defect": False,
                "payment_submitted": False,
                "reservation_created": False,
                "outcomes": ["consistent", "consistent"],
                "normalized_signatures": [["TRY", "EUR", "TRY", "EUR"], ["TRY", "EUR", "TRY", "EUR"]],
                "evidence_grade": "F2",
            },
        },
        "advisory": {
            "authority": advisory_authority,
            "classification": "NO_DEFECT_OBSERVED",
            "product_verdict_source": "normalized_evidence_not_liminalos",
        },
        "workflow": {"ltp_commit": "b1fcf43977a2de5cd21b84887d6dcdc1d451acd1"},
    }
    obs_record = {
        "transition_id": transition,
        "subject_id": subject,
        "authorization_ref": authorization["record_ref"],
        "action_identity_digest": action_digest,
        "binding_digest": binding_digest,
        "execution_status": "EXECUTED",
        "result": result,
        "result_digest": adapter.sha256_ref(result),
    }
    observation = {"record": obs_record, "record_ref": adapter.sha256_ref(obs_record)}
    supported_claim = {
        "claim_id": "no-confirmed-defect",
        "claim_text": "No confirmed Airbnb defect was observed.",
        "evidence_level": "FULL_LIFECYCLE_JOINED",
        "required_record_refs": [authorization["record_ref"], observation["record_ref"]],
        "verdict": "SUPPORTED",
    }
    packet = {
        "schema_version": "airbnb-ltp-transition-v0.1",
        "ltp_commit": "b1fcf43977a2de5cd21b84887d6dcdc1d451acd1",
        "transition_id": transition,
        "subject_id": subject,
        "authorization_ref": authorization["record_ref"],
        "observation_ref": observation["record_ref"],
        "verified_response": {
            "transition_id": transition,
            "subject_id": subject,
            "verification_level": "FULL_LIFECYCLE_JOINED",
            "dimensions": {"authority": "VALID", "execution": "OBSERVED_EXECUTED", "response_integrity": "VERIFIED"},
            "response_integrity_record": {
                "overall_verdict": "VERIFIED",
                "authorization_ref": authorization["record_ref"],
                "observation_refs": [observation["record_ref"]],
                "claims": [supported_claim],
            },
        },
        "fabricated_claim_control": {
            "transition_id": transition,
            "subject_id": subject,
            "verification_level": "FULL_LIFECYCLE_JOINED",
            "response_integrity_record": {
                "overall_verdict": "FAILED",
                "claims": [{"claim_id": "fabricated", "verdict": "CONTRADICTED"}],
            },
        },
    }
    return packet, authorization, observation


class LotusLtpAcceptanceTest(unittest.TestCase):
    def test_valid_packet_emits_bounded_memory_candidate(self) -> None:
        packet, authorization, observation = fixture()
        validated = adapter.validate_packet(packet, authorization, observation)
        packet_hash = adapter.sha256_hex(packet)
        judgment = adapter.build_judgment(validated, packet_hash, "2026-07-19T23:40:00+03:00")
        event = adapter.build_event(
            judgment,
            "safal207/LiminalQAengineer",
            "agent/test",
            "c7af3e210d007026fedc57eb9435069a958fac6f",
            "03efe66e1d7920480fe6fa1dc310fe6b17faaf80",
            packet_hash,
            "2026-07-19T23:40:00+03:00",
        )
        self.assertEqual(judgment["verdict"], "ALLOW")
        self.assertEqual(judgment["result_class"], "VERIFIED_NEGATIVE_OBSERVATION")
        self.assertFalse(judgment["memory_candidate"]["durable_memory"])
        self.assertFalse(judgment["authority"]["external_submission"])
        self.assertFalse(judgment["authority"]["durable_memory_write"])
        unhashed = copy.deepcopy(event)
        recorded = unhashed["details"].pop("event_sha256")
        self.assertEqual(recorded, adapter.sha256_hex(unhashed))

    def test_tampered_authorization_ref_is_rejected(self) -> None:
        packet, authorization, observation = fixture()
        authorization["record_ref"] = "sha256:" + "0" * 64
        with self.assertRaisesRegex(ValueError, "record_ref mismatch"):
            adapter.validate_packet(packet, authorization, observation)

    def test_tampered_observation_result_is_rejected(self) -> None:
        packet, authorization, observation = fixture()
        observation["record"]["result"]["run"]["safe_readonly_probe"] = False
        with self.assertRaisesRegex(ValueError, "record_ref mismatch"):
            adapter.validate_packet(packet, authorization, observation)

    def test_unverified_response_is_rejected(self) -> None:
        packet, authorization, observation = fixture()
        packet["verified_response"]["response_integrity_record"]["overall_verdict"] = "FAILED"
        with self.assertRaisesRegex(ValueError, "overall_verdict"):
            adapter.validate_packet(packet, authorization, observation)

    def test_missing_contradicted_control_is_rejected(self) -> None:
        packet, authorization, observation = fixture()
        packet["fabricated_claim_control"]["response_integrity_record"]["claims"][0]["verdict"] = "SUPPORTED"
        with self.assertRaisesRegex(ValueError, "CONTRADICTED"):
            adapter.validate_packet(packet, authorization, observation)

    def test_authority_escalation_is_rejected(self) -> None:
        packet, authorization, observation = fixture()
        observation["record"]["result"]["run"]["authority"]["external_submission"] = True
        result = observation["record"]["result"]
        observation["record"]["result_digest"] = adapter.sha256_ref(result)
        observation["record_ref"] = adapter.sha256_ref(observation["record"])
        packet["observation_ref"] = observation["record_ref"]
        response = packet["verified_response"]["response_integrity_record"]
        response["observation_refs"] = [observation["record_ref"]]
        response["claims"][0]["required_record_refs"][-1] = observation["record_ref"]
        with self.assertRaisesRegex(ValueError, "external_submission must be false"):
            adapter.validate_packet(packet, authorization, observation)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

from typing import AbstractSet, Any, Mapping


def _valid_state_hash(value: Any) -> bool:
    if not isinstance(value, str) or not value.startswith("sha256:"):
        return False
    digest = value.removeprefix("sha256:")
    return len(digest) == 64 and all(ch in "0123456789abcdef" for ch in digest)


def check_execution_binding(
    expected: Mapping[str, Any],
    observed: Mapping[str, Any],
    consumed_nonces: AbstractSet[str],
) -> tuple[str, dict[str, Any] | None]:
    """Evaluate the executor-owned legs of an ELR use attempt.

    `state_hash` identifies content, `generation` identifies transition history,
    and `use_nonce` identifies the concrete consumption occurrence.

    This helper is intentionally not a transaction manager. It does not mutate
    `consumed_nonces` and it cannot make an external side effect atomic. A real
    executor must perform the final nonce reservation/consumption and effect as
    one fail-closed boundary using its own concurrency primitive.
    """
    expected_hash = expected.get("state_hash")
    expected_generation = expected.get("generation")
    use_nonce = expected.get("use_nonce")
    observed_hash = observed.get("state_hash")
    observed_generation = observed.get("generation")

    if (
        not _valid_state_hash(expected_hash)
        or not _valid_state_hash(observed_hash)
        or not isinstance(expected_generation, int)
        or isinstance(expected_generation, bool)
        or expected_generation < 0
        or not isinstance(observed_generation, int)
        or isinstance(observed_generation, bool)
        or observed_generation < 0
        or not isinstance(use_nonce, str)
        or not use_nonce
    ):
        return "INVALID_EXECUTION_BINDING_INPUT", None

    if observed_hash != expected_hash:
        return "BLOCKED_EXECUTION_CONTENT_DRIFT", {
            "expected_state_hash": expected_hash,
            "observed_state_hash": observed_hash,
        }

    if observed_generation != expected_generation:
        return "BLOCKED_EXECUTION_GENERATION_DRIFT", {
            "expected_generation": expected_generation,
            "observed_generation": observed_generation,
            "state_hash": observed_hash,
        }

    if use_nonce in consumed_nonces:
        return "BLOCKED_EXECUTION_NONCE_REPLAY", {
            "generation": observed_generation,
            "state_hash": observed_hash,
            "use_nonce": use_nonce,
        }

    return "EXECUTION_BINDING_READY", {
        "generation": observed_generation,
        "state_hash": observed_hash,
        "use_nonce": use_nonce,
    }

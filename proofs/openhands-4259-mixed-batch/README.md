# OpenHands mixed-batch analyzer association

This packet proposes a tests-only change to
[`test_security_analysis_event.py`](https://github.com/OpenHands/software-agent-sdk/blob/4cc058275c5a08d845bd846576aafc80e5dd7d0d/tests/sdk/agent/test_security_analysis_event.py)
at SDK revision `4cc058275c5a08d845bd846576aafc80e5dd7d0d`.
The current production implementation passes the strengthened test.

## The coverage gap

The existing three-action batch test uses identical analyzer risks and details,
then checks dictionary key sets. It cannot distinguish a correct mapping from
a permutation of those identical values between action IDs.

[mixed-batch.patch](mixed-batch.patch) strengthens that existing test with
`LOW`, `HIGH`, and `MEDIUM` analyzer risks and a different detail marker for
each tool-call ID. It checks both complete dictionaries keyed by the actual
`ActionEvent.id` values, and preserves the acting model's separate `LOW`
labels. The proposed upstream diff changes one test file: 35 additions and
8 deletions. It changes no production code.

## Replay

Use a disposable SDK checkout and the native locked development environment.
The recorded environment is Python 3.13.16 and uv 0.12.23.

```bash
git clone https://github.com/OpenHands/software-agent-sdk.git /tmp/openhands-mixed-batch
git -C /tmp/openhands-mixed-batch checkout 4cc058275c5a08d845bd846576aafc80e5dd7d0d
```

Run `make build` in that SDK checkout, as required by its contributor guide.
From the root of this repository, run:

```bash
python3 proofs/openhands-4259-mixed-batch/replay.py \
  --source /tmp/openhands-mixed-batch \
  --output /tmp/openhands-mixed-batch-results
```

The output directory must be new. The driver verifies the source revision and
known input bytes, uses `uv run --frozen`, and restores the exact input
production and test bytes in `finally`. It accepts either the pinned original
test or the supplied strengthened test as its input state.

Expected replay results:

| Experiment | Original test file | Strengthened test file |
|---|---:|---:|
| Unmodified production | 11 pass | 11 pass |
| Rotate only risk values between action IDs | 11 pass | 10 pass, 1 expected failure |
| Rotate only detail values between action IDs | 11 pass | 10 pass, 1 expected failure |

In this three-action fixture, each controlled mutation keeps the dictionary
keys and the original policy input intact. The only failing strengthened case must be
`test_one_event_per_batch_keyed_by_action_id`. These are deliberately introduced
faults used to measure test sensitivity, not defects observed in upstream.

After removing the production mutations, the driver runs the strengthened
test with the native async secret-masking and security suites:

```bash
uv run --frozen pytest \
  tests/sdk/agent/test_security_analysis_event.py \
  tests/sdk/agent/test_async_secret_masking.py \
  tests/sdk/security \
  -p no:cacheprovider -o 'addopts=-q --tb=short'
```

Expected result: **491 passed, 7 skipped, 10 xfailed**. The local native
[per-file pre-commit checks](pre-commit.txt) also passed for the proposed test diff.
[The dedicated workflow](../../.github/workflows/openhands-mixed-batch.yml)
replays this packet against the immutable SDK revision using its frozen lock.
It is separate from this repository's Elixir/Rust CI.

The driver writes `report.json`, `manifest.json`, and raw pytest/JUnit output.
Retained local evidence is in [results](results/). A workflow run produces a
fresh report rather than treating the retained result as a passing test.

## Scope

This is a native unit-test proposal using the existing `Agent.step` helper,
mocked LLM completion, and a no-op tool. It covers analyzer risk/detail
association to action-event IDs and separation from the model's action label.
It does not establish tool-argument integrity, `Conversation.run`/`arun`
integration, restart durability, authorization, external execution, or effect
count.

[Upstream PR #5182](https://github.com/OpenHands/software-agent-sdk/pull/5182)
merged the native analyzer audit event on 2026-10-09 and references
[issue #4259](https://github.com/OpenHands/software-agent-sdk/issues/4259).
That public reference does not establish adoption of Pythia's receipt protocol
or direct causal attribution to the earlier proposal. The interoperability
[mapping correction](../../docs/integrations/OPENHANDS_EVIDENCE_GATE_DECISION_EVENT.md#native-sdk-mapping-checked-on-2026-10-11)
uses the current native event while keeping analyzer evidence separate from
gate decisions and dispatch.

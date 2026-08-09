#!/usr/bin/env bash
set -euo pipefail

: "${DAO_DIR:?set DAO_DIR}"
: "${GARDEN_DIR:?set GARDEN_DIR}"
: "${LIMINALDB_DIR:?set LIMINALDB_DIR}"
: "${EVIDENCE_DIR:?set EVIDENCE_DIR}"

mkdir -p "$EVIDENCE_DIR"
EVIDENCE_DIR="$(cd "$EVIDENCE_DIR" && pwd)"

DAO_PID=""
LIMINALDB_PID=""
cleanup() {
  set +e
  if [[ -n "$DAO_PID" ]]; then kill "$DAO_PID" 2>/dev/null || true; fi
  if [[ -n "$LIMINALDB_PID" ]]; then kill "$LIMINALDB_PID" 2>/dev/null || true; fi
}
trap cleanup EXIT

record_sha() {
  git -C "$1" rev-parse HEAD
}

DAO_SHA="$(record_sha "$DAO_DIR")"
GARDEN_SHA="$(record_sha "$GARDEN_DIR")"
LIMINALDB_SHA="$(record_sha "$LIMINALDB_DIR")"

cat > "$EVIDENCE_DIR/components.json" <<JSON
{
  "dao_lim": "$DAO_SHA",
  "garden_liminal": "$GARDEN_SHA",
  "liminal_db": "$LIMINALDB_SHA"
}
JSON

# ---------------------------------------------------------------------------
# 1. DAO_lim: produce an actual explainable routing decision.
# ---------------------------------------------------------------------------
(
  cd "$DAO_DIR"
  exec stdbuf -oL -eL ./target/debug/dao --config configs/dao.toml
) > "$EVIDENCE_DIR/dao.log" 2>&1 &
DAO_PID=$!

for _ in $(seq 1 60); do
  if "$DAO_DIR/target/debug/daoctl" --server http://127.0.0.1:9103 health \
      > "$EVIDENCE_DIR/dao-health.txt" 2>&1; then
    break
  fi
  sleep 0.25
done

"$DAO_DIR/target/debug/daoctl" \
  --server http://127.0.0.1:9103 \
  explain \
  --host api.example.com \
  --path /v1/chat/completions \
  --intent realtime \
  --json > "$EVIDENCE_DIR/dao-decision.json"

SELECTED_UPSTREAM="$(python3 - "$EVIDENCE_DIR/dao-decision.json" <<'PY'
import json, sys
p=sys.argv[1]
data=json.load(open(p))
selected=data.get('selected')
assert isinstance(selected,str) and selected, data
assert data.get('no_route') is False, data
winners=[c.get('name') for c in data.get('candidates',[]) if c.get('winner')]
assert winners == [selected], (selected,winners,data)
print(selected)
PY
)"
printf '%s\n' "$SELECTED_UPSTREAM" > "$EVIDENCE_DIR/dao-selected-upstream.txt"

# ---------------------------------------------------------------------------
# 2. Real LiminalDB process: application parser + impulse routing.
# Keep stdin open because liminal-cli's interactive task exits on EOF.
# ---------------------------------------------------------------------------
LDB_STORE="$EVIDENCE_DIR/liminaldb-store"
mkdir -p "$LDB_STORE"
(
  cd "$LIMINALDB_DIR/liminal-db"
  tail -f /dev/null | stdbuf -oL -eL ./target/debug/liminal-cli \
    --store "$LDB_STORE" \
    --ws-port 8787
) > "$EVIDENCE_DIR/liminaldb.log" 2>&1 &
LIMINALDB_PID=$!

for _ in $(seq 1 80); do
  if nc -z 127.0.0.1 8787 2>/dev/null; then
    break
  fi
  sleep 0.25
done
nc -z 127.0.0.1 8787

# ---------------------------------------------------------------------------
# 3. GardenLiminal: explicit orchestration handoff from the DAO decision.
# The selected upstream becomes immutable workload evidence. The workload has
# a fresh network namespace, while Garden's Store/LiminalDB adapter remains on
# the host-supervisor side by the already-validated namespace boundary.
# ---------------------------------------------------------------------------
ROOTFS="$EVIDENCE_DIR/rootfs"
mkdir -p "$ROOTFS/bin"
cp "$(command -v busybox)" "$ROOTFS/bin/busybox"
chmod 0755 "$ROOTFS/bin/busybox"

SEED="$EVIDENCE_DIR/stack-e2e-seed.yaml"
cat > "$SEED" <<YAML
apiVersion: v0
kind: Seed
meta:
  name: liminal-stack-e2e
  id: liminal-stack-e2e-v0-1
rootfs:
  path: $ROOTFS
entrypoint:
  cmd: ["/bin/busybox", "sh", "-c", "echo DAO_SELECTED_UPSTREAM=$SELECTED_UPSTREAM"]
  env:
    - "DAO_SELECTED_UPSTREAM=$SELECTED_UPSTREAM"
  cwd: "/"
net:
  enable: true
security:
  drop_caps: []
user:
  uid: 1000
  gid: 1000
  map_rootless: false
store:
  kind: "liminal"
YAML

LIMINAL_URL=ws://127.0.0.1:8787 \
  sudo -E "$GARDEN_DIR/target/debug/gl" run -f "$SEED" --store liminal \
  > "$EVIDENCE_DIR/garden.log" 2>&1

# Give the LiminalDB command loop a bounded moment to route frames already
# accepted by its WebSocket server.
for _ in $(seq 1 40); do
  if grep -q 'garden.lifecycle.v1:' "$EVIDENCE_DIR/liminaldb.log"; then
    break
  fi
  sleep 0.25
done

# Application-level acceptance checks. A transport-only success is not enough.
if grep -q 'impulse requires pattern' "$EVIDENCE_DIR/liminaldb.log"; then
  echo 'LiminalDB rejected Garden impulse schema' >&2
  exit 1
fi
if grep -q 'ws command failed' "$EVIDENCE_DIR/liminaldb.log"; then
  echo 'LiminalDB reported an application command failure' >&2
  grep 'ws command failed' "$EVIDENCE_DIR/liminaldb.log" >&2 || true
  exit 1
fi
grep -q 'garden.lifecycle.v1:' "$EVIDENCE_DIR/liminaldb.log"

# We require multiple lifecycle records, not a one-frame connectivity probe.
LIFECYCLE_MATCHES="$(grep -c 'garden.lifecycle.v1:' "$EVIDENCE_DIR/liminaldb.log" || true)"
if (( LIFECYCLE_MATCHES < 3 )); then
  echo "expected >=3 accepted Garden lifecycle impulses, got $LIFECYCLE_MATCHES" >&2
  exit 1
fi

python3 - "$EVIDENCE_DIR" "$SELECTED_UPSTREAM" "$DAO_SHA" "$GARDEN_SHA" "$LIMINALDB_SHA" "$LIFECYCLE_MATCHES" <<'PY'
import json, pathlib, sys
root=pathlib.Path(sys.argv[1])
selected, dao_sha, garden_sha, db_sha, matches=sys.argv[2:]
decision=json.loads((root/'dao-decision.json').read_text())
summary={
  'schema':'liminal-stack-e2e-evidence-v0.1',
  'result':'PASS',
  'components':{
    'dao_lim':dao_sha,
    'garden_liminal':garden_sha,
    'liminal_db':db_sha,
  },
  'dao':{
    'route':decision.get('route'),
    'policy':decision.get('policy'),
    'request_intent':decision.get('request_intent'),
    'selected_upstream':selected,
    'candidate_count':len(decision.get('candidates',[])),
  },
  'handoff':{
    'mode':'explicit_orchestration',
    'selected_upstream_embedded_in_garden_workload':True,
  },
  'garden':{
    'workload_exit':0,
    'network_namespace_requested':True,
    'store':'liminal',
  },
  'liminaldb':{
    'real_process':True,
    'websocket_port':8787,
    'accepted_garden_lifecycle_log_matches':int(matches),
    'application_schema_error_detected':False,
    'durable_per_impulse_ack_claimed':False,
  },
}
(root/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
PY

cat "$EVIDENCE_DIR/summary.json"

#!/usr/bin/env bash
# prime.sh — SessionStart hook. Sets the OODA posture once per session. The
# per-turn nudge (nudge.sh) fires only when a decision/action/iteration appears.
#
# Output protocol: print JSON with hookSpecificOutput.additionalContext on
# stdout, exit 0. Best-effort — any failure exits 0 silently.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

read -r -d '' MSG <<'EOF'
[ooda] Standing prior for this session: drive with the real OODA loop (Boyd) —
NOT a four-box speed circle. Observe: MEASURE, do not assume (profile, run the
cheapest-falsifier probe; your own prior actions changed what there is to see).
Orient (the schwerpunkt — the highest-leverage step): reframe against your stale
models and bias — genetic/cultural/experience priors + new information +
analysis-and-synthesis; on a surprise or a failing baseline, run one
destruction-and-creation pass (break the old frame, synthesize a new
hypothesis). Decide: pick ONE lever, tag it a hypothesis. Act: ship it as a
TEST, feed the result back to Observe. Loop fast — many cheap, revert-safe,
VARIED cycles beat one slow-perfect one. Tempo is unpredictable rhythm that
outpaces the problem, not raw haste; a predictable fast loop is counterable.
When Orientation is a proven repertoire, take the Orient→Act shortcut and skip
explicit Decide. The full loop + anti-patterns are in the ooda skill.
EOF

printf '%s' "${MSG}" | bash "${ROOT}/scripts/run-python.sh" -c \
  'import json,sys
print(json.dumps({"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":sys.stdin.read()}}))' \
  2>/dev/null || true

exit 0

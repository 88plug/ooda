#!/usr/bin/env bash
# smoke.sh — prime always injects; nudge fires ONLY on decision/action language;
# a back-to-back same-session repeat is suppressed (per-session anti-nag cooldown).
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
fail=0

# Isolate cooldown state to a fresh per-run dir so asserts are deterministic.
CLAUDE_PLUGIN_DATA="$(mktemp -d)"
export CLAUDE_PLUGIN_DATA

out="$(printf '{"session_id":"s"}' | bash "${ROOT}/hooks/prime.sh" 2>/dev/null)"
printf '%s' "${out}" | bash "${ROOT}/scripts/run-python.sh" -c '
import json,sys
c=json.load(sys.stdin)["hookSpecificOutput"]["additionalContext"]
assert "ooda" in c and len(c)>40
print("PASS prime always injects")' 2>/dev/null || { echo "FAIL prime: ${out}"; fail=1; }

# Each assertion uses a distinct session_id so its first fire always fires.
fire() {
  local label="$1" prompt="$2" want="$3" sid="$4"
  local out; out="$(printf '{"prompt":"%s","session_id":"%s"}' "${prompt}" "${sid}" | bash "${ROOT}/hooks/nudge.sh" 2>/dev/null)"
  local got="silent"; [ -n "${out}" ] && got="fires"
  if [ "${got}" = "${want}" ]; then echo "PASS ${label} (${got})"; else echo "FAIL ${label}: want ${want} got ${got}: ${out}"; fail=1; fi
}
fire "decide-approach"   "how should we approach beating the incumbent on latency" fires sess-a
fire "iterate/ship"      "let us iterate and ship a fix then re-measure"            fires sess-b
fire "stuck/diagnose"    "we are stuck on this outage, what is the root cause"      fires sess-c
fire "neutral mechanical" "rename the variable foo to bar in utils.py"             silent sess-d
fire "neutral lookup"     "print the current git branch name"                      silent sess-e

# Anti-nag cooldown: a back-to-back repeat in the SAME session is suppressed.
fire "cooldown first fire"        "how should we approach the migration"           fires  sess-cd
fire "cooldown repeat suppressed" "how should we approach the migration"           silent sess-cd

python3 -c '
import json,sys
m=json.load(open(sys.argv[1]))
assert m["name"]=="ooda"
assert "SessionStart" in m["hooks"] and "UserPromptSubmit" in m["hooks"]
print("PASS manifest")' "${ROOT}/.claude-plugin/plugin.json" || fail=1

exit "${fail}"

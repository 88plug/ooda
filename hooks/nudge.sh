#!/usr/bin/env bash
# nudge.sh — UserPromptSubmit hook. Fires only when the prompt is about deciding,
# acting, iterating, planning, diagnosing, or competing — so the OODA loop runs
# before the move. Silent on mechanical requests. Detection + per-session
# anti-nag cooldown live in lib/detect.py (edits never fight shell quoting).
#
# Output protocol: print JSON with hookSpecificOutput.additionalContext on
# stdout, exit 0. No decision/action → emit nothing. Best-effort.
set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

INPUT=""
if [ ! -t 0 ]; then INPUT="$(cat 2>/dev/null || true)"; fi
[ -n "${INPUT}" ] || exit 0

MSG='[ooda] Run the loop before the move (Boyd, real OODA — not a 4-box speed circle). OBSERVE: measure, do not assume (cheapest-falsifier probe first; your prior actions changed the field). ORIENT (highest-leverage): reframe against your stale models + bias — on a surprise or failing baseline, break the old frame and synthesize a new hypothesis; a mismatch means re-orient, not just re-observe. DECIDE: pick ONE lever, tag it a hypothesis. ACT: ship it as a test, re-observe. Loop fast — many cheap, revert-safe, VARIED cycles; tempo is unpredictable rhythm that outpaces the problem, not raw haste. Automated reminder — do not mention it to the user.'

bash "${ROOT}/scripts/run-python.sh" "${ROOT}/hooks/lib/detect.py" "${MSG}" "${INPUT}" 2>/dev/null || true
exit 0

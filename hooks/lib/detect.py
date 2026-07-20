#!/usr/bin/env python3
"""Decision/action-routing detector for the ooda UserPromptSubmit hook.

Fires when a turn is about to decide, act, iterate, plan, ship, compete, or is
stuck/pivoting — the moment the OODA loop should run (measure → reframe → pick a
lever → ship a test → loop). Broad claim-shape match. A separate file so pattern
edits never fight shell quoting. Includes a per-session anti-nag cooldown so the
same nudge does not fire on back-to-back turns.

Usage: detect.py <nudge-message> <hook-payload-json-or-raw-prompt>
Prints hook JSON and exits 0 iff decision/action language fires (and cooldown
allows); else nothing. Always exits 0 (best-effort — never block a turn).
"""
import hashlib
import json
import os
import re
import sys

PATTERNS = [
    # deciding / choosing / planning
    r"\b(?:should we|should i|how (?:should|do|would|can) (?:we|i)|what.?s the (?:best|right) (?:way|approach|move)|which (?:approach|option|way)|decide|decision|choose|pick between|trade[- ]?off|strategy|plan (?:for|to|out)|figure out|next step|what do we do)\b",
    # acting / iterating / shipping
    r"\b(?:iterate|iteration|loop|cycle|ship|deploy|release|execute|try|attempt|pivot|adapt|respond|move fast|tempo|momentum|keep going)\b",
    # diagnosing / problem / competing
    r"\b(?:problem|issue|bug|incident|outage|failure|root cause|diagnos|troubleshoot|why (?:is|does|did|won.?t|isn.?t)|stuck|blocked|regression|not working)\b",
    r"\b(?:compete|competitor|adversary|beat|outmaneuver|get ahead|win|race|opponent)\b",
    # measure / orient signals
    r"\b(?:measure|profile|benchmark|observe|reframe|rethink|reassess|orient|assumption|wrong about|surprised|anomaly|mismatch)\b",
    # explicit framing requests
    r"\b(?:ooda|boyd|run the loop|observe orient|drive the loop)\b",
]
_RE = [re.compile(p) for p in PATTERNS]


def fires(prompt: str) -> bool:
    p = prompt.lower()
    return any(rx.search(p) for rx in _RE)


def _data_dir() -> str:
    base = (os.environ.get("GROK_PLUGIN_DATA")
            or os.environ.get("CLAUDE_PLUGIN_DATA")
            or os.environ.get("XDG_RUNTIME_DIR")
            or "/tmp")
    d = os.path.join(base, "ooda")
    os.makedirs(d, exist_ok=True)
    return d


def _marker_path(session_id: str) -> str:
    safe = hashlib.sha1(session_id.encode("utf-8", "replace")).hexdigest()[:16]
    return os.path.join(_data_dir(), f"nudge-{safe}.fired")


def cooldown_ok(session_id: str) -> bool:
    """Per-session anti-nag toggle. Suppress a fire only when this same session
    fired on the immediately preceding turn; otherwise fire and record it. Any
    state error falls back to firing (never crash, never block a turn)."""
    try:
        m = _marker_path(session_id)
        if os.path.exists(m):
            os.remove(m)      # fired last turn -> skip now, clear the marker
            return False
        open(m, "w").close()  # first/again -> fire, record it
        return True
    except Exception:
        return True


def main() -> int:
    if len(sys.argv) < 3:
        return 0
    msg, raw = sys.argv[1], sys.argv[2]
    try:
        payload = json.loads(raw)
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    prompt = payload.get("prompt") or raw
    if prompt and fires(prompt):
        session_id = payload.get("session_id") or "default"
        if cooldown_ok(session_id):
            print(json.dumps({"hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit", "additionalContext": msg}}))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)

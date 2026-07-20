#!/usr/bin/env bash
# Resolve a usable Python ≥3.10 and exec it with the given args.
#
# Claude Code's MCP/hook spawn PATH is thin (often no Homebrew/pyenv). Never
# put bare "python3" in plugin.json / hooks.json — route every Python invoke
# through this script.
#
# MCP-safe: diagnostics go to stderr only; stdout is reserved for the child.
#
# Override (first match, version-gated):
#   EIGHTYEIGHT_PYTHON  fleet-wide
#   PLUGIN_PYTHON       generic
#   OODA_PYTHON      this plugin
#
# Also honors VIRTUAL_ENV and a plugin-local .venv.
set -euo pipefail

MIN_MAJOR=3
MIN_MINOR=10

_version_ok() {
  local py="$1"
  [ -n "$py" ] && [ -x "$py" ] || return 1
  "$py" -c "import sys; raise SystemExit(0 if sys.version_info >= (${MIN_MAJOR}, ${MIN_MINOR}) else 1)" 2>/dev/null
}

_try() {
  local cand="$1"
  [ -n "$cand" ] || return 1
  if [ -x "$cand" ] && _version_ok "$cand"; then
    printf '%s' "$cand"
    return 0
  fi
  if command -v "$cand" >/dev/null 2>&1; then
    local resolved
    resolved="$(command -v "$cand")"
    if _version_ok "$resolved"; then
      printf '%s' "$resolved"
      return 0
    fi
  fi
  return 1
}

find_python() {
  local c root
  root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

  for c in "${EIGHTYEIGHT_PYTHON:-}" "${PLUGIN_PYTHON:-}" "${OODA_PYTHON:-}"; do
    _try "$c" && return 0
  done

  if [ -n "${VIRTUAL_ENV:-}" ]; then
    for c in "${VIRTUAL_ENV}/bin/python3" "${VIRTUAL_ENV}/bin/python"; do
      _try "$c" && return 0
    done
  fi

  for c in "${root}/.venv/bin/python" "${root}/.venv/bin/python3" \
           "${root}/venv/bin/python" "${root}/venv/bin/python3"; do
    _try "$c" && return 0
  done

  for c in python3 python3.13 python3.12 python3.11 python3.10 python; do
    _try "$c" && return 0
  done

  for c in \
    /opt/homebrew/bin/python3 \
    /usr/local/bin/python3 \
    /usr/bin/python3 \
    "${HOME}/.local/bin/python3" \
    /usr/bin/python
  do
    _try "$c" && return 0
  done

  return 1
}

PY="$(find_python)" || {
  echo "ooda: no Python >=${MIN_MAJOR}.${MIN_MINOR} found." >&2
  echo "  Set EIGHTYEIGHT_PYTHON=/path/to/python3 (or OODA_PYTHON), or install Python 3." >&2
  echo "  Checked: env overrides, VIRTUAL_ENV, plugin .venv, PATH, Homebrew, /usr/bin." >&2
  exit 1
}

exec "$PY" "$@"

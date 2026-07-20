<div align="center">

# OODA

**Route any decision or action through John Boyd's real OODA loop for Claude Code + Grok — Observe, Orient (the schwerpunkt), Decide, Act, loop fast. Not a 4-box speed circle.**

[![plugin-validate](https://github.com/88plug/ooda/actions/workflows/plugin-validate.yml/badge.svg)](https://github.com/88plug/ooda/actions/workflows/plugin-validate.yml)
[![License: FSL-1.1-ALv2](https://img.shields.io/badge/license-FSL--1.1--ALv2-blue?style=flat)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-blue?style=flat)](https://88plug.github.io/ooda/)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2?style=flat)](https://github.com/88plug/claude-code-plugins)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/88plug/ooda)

</div>

OODA (Col. John Boyd) is a theory of **winning through faster, better
adaptation** — not a checklist and not a race. This plugin runs the *real* loop
at the moment you decide, act, iterate, diagnose, or compete.

The anti-patterns that void it, up front: it is **not a four-box speed circle**,
it is **not a pure speed race**, and **Orient is not one step of four — it
dominates.** The killer failure is *Orient-blindness*: acting fast on an
un-reframed, biased model.

## Install

### Claude Code

```text
/plugin marketplace add 88plug/claude-code-plugins
/plugin install ooda@88plug
```

### Grok Build

```text
grok plugin marketplace add 88plug/claude-code-plugins
grok plugin install ooda@88plug --trust
```

The hooks and the bundled skill load automatically from the manifest. No MCP
server, no database, no dependencies beyond `python3` (routed through a
thin-PATH-safe resolver). `install.sh` is a no-op.

## What it does

| Hook | Event | What it does |
|---|---|---|
| `prime.sh` | `SessionStart` | Sets the OODA posture once per session |
| `nudge.sh` | `UserPromptSubmit` | Fires **only when** the prompt is a decision/action/iteration/incident/compete turn; silent on mechanical requests |

Detection lives in `hooks/lib/detect.py` with a per-session anti-nag cooldown so
the same nudge does not fire on back-to-back turns. `/ooda:loop` runs the loop on
demand.

## The loop (real, not the cartoon)

| Phase | Boyd's meaning | Do |
|---|---|---|
| **Observe** | intake unfolding circumstances + your interaction with them | measure, don't assume — your prior acts changed the field |
| **Orient** | the schwerpunkt: genetic/cultural/experience priors + new info + analysis & synthesis | reframe against stale models (the highest-leverage step) |
| **Decide** | "Decision (Hypothesis)" | pick one lever, as a hypothesis |
| **Act** | "Action (Test)" | ship a test; the result re-enters Observe |

Two **implicit-guidance** arrows run Orient→Observe and Orient→Act, bypassing
explicit Decide — the trained-operator fast path for proven moves.

## Orient dominates

Orientation shapes what you observe and how you decide and act, and is reshaped
by feedback. On a surprise or a failing baseline it runs **destruction and
creation**: break the stale frame into its parts, synthesize a new hypothesis —
because Gödel, Heisenberg, and the 2nd law guarantee any closed model drifts from
reality. Orientation is never finished.

## Tempo is not speed

Getting "inside the loop" is unpredictable **rhythm and variety** that outpaces
the problem's Orient — not stopwatch haste. A predictable fast loop is
counterable. For work: cheapest-falsifier-first, short varied revert-safe cycles
that re-orient before your own model goes stale.

## Composes with

- **cynefin** — Cynefin lives inside Orient: classify the domain by its constraints before choosing the response.
- **scientific-method** — Observe and Act are the experiment: the cheapest-falsifier probe and the ship-as-a-test.
- **break-dogma** — a stale previous-experience input to Orient is exactly the inherited assumption to test.

## Test

```bash
bash tests/smoke.sh                # prime injects; nudge fires on decision/action language, silent on mechanical; cooldown suppresses a repeat
python3 .ci/validate_plugin.py .   # manifest, keywords, hook paths, skill frontmatter
```

## Credits

The framework is John Boyd's. This plugin packages his published work (the
briefings collected in *A Discourse on Winning and Losing*; Frans Osinga's
*Science, Strategy and War*; Chet Richards; Robert Coram) as a routing
discipline — see the skill's Sources section.

## License

FSL-1.1-ALv2.

# OODA

**Route any decision or action through John Boyd's real OODA loop — Observe, Orient (the schwerpunkt), Decide, Act, loop fast. Not a 4-box speed circle.**

[![plugin-validate](https://github.com/88plug/ooda/actions/workflows/plugin-validate.yml/badge.svg)](https://github.com/88plug/ooda/actions/workflows/plugin-validate.yml)
[![License: FSL-1.1-ALv2](https://img.shields.io/badge/license-FSL--1.1--ALv2-blue?style=flat)](https://github.com/88plug/ooda/blob/main/LICENSE)
[![Docs](https://img.shields.io/badge/docs-online-blue?style=flat)](https://88plug.github.io/ooda/)
[![Claude Code plugin](https://img.shields.io/badge/Claude%20Code-plugin-8A2BE2?style=flat)](https://github.com/88plug/claude-code-plugins)
[![DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/88plug/ooda)


OODA (Col. John Boyd) is a theory of winning through faster, better adaptation.
This plugin runs the *real* loop at the moment you decide, act, or iterate — not
the popular four-box speed circle. **Orient dominates**, and tempo is
unpredictable rhythm, not raw haste.

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

The hooks and the bundled `ooda` skill load automatically from the manifest.
`install.sh` is a no-op.

## The loop

| Phase | Boyd's meaning | Do |
|---|---|---|
| Observe | intake unfolding circumstances; your prior acts changed the field | measure, don't assume |
| Orient | the schwerpunkt — 5 inputs + destruction/creation | reframe against stale models (highest-leverage) |
| Decide | "Decision (Hypothesis)" | pick one lever, as a hypothesis |
| Act | "Action (Test)" | ship a test, re-observe |

Two implicit-guidance arrows run Orient→Observe and Orient→Act, bypassing Decide
— the trained-operator fast path.

## What it does

| Hook | Event | What it does |
|---|---|---|
| `prime.sh` | `SessionStart` | Sets the OODA posture once per session |
| `nudge.sh` | `UserPromptSubmit` | Fires only on a decision/action/iteration turn; silent on mechanical requests |

The full loop, the Orient schwerpunkt, tempo-not-speed, and the anti-patterns are
in the bundled **`ooda` skill**.

## License

FSL-1.1-ALv2.

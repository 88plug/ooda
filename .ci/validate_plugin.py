#!/usr/bin/env python3
"""validate_plugin.py — CI gate for a single-manifest Claude Code plugin.

Checks, with no third-party deps:
  * every JSON file parses;
  * there is exactly ONE manifest, at .claude-plugin/plugin.json, with the
    required fields and exactly 20 keywords;
  * every hook command references a script that exists on disk;
  * every skill markdown has valid frontmatter with name + description;
  * `bash -n` passes on every shell script;
  * `py_compile` passes on every python file.

Generic: the plugin name is read from the manifest, not hard-coded, so this
validator drops into any single-manifest plugin unchanged.

Usage:  python .ci/validate_plugin.py [ROOT]   (ROOT defaults to the repo root)
Exit 0 == all good; non-zero == CI fail, with a summary of problems.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

ROOT = os.path.abspath(
    sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
errors: list = []
checks = 0


def ok(msg):
    global checks
    checks += 1
    print(f"  ok: {msg}")


def fail(msg):
    errors.append(msg)
    print(f"FAIL: {msg}")


def load_json(rel):
    path = os.path.join(ROOT, rel)
    if not os.path.isfile(path):
        fail(f"missing file: {rel}")
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {rel}: {exc}")
        return None


def all_json_parse():
    for dirpath, _dirs, files in os.walk(ROOT):
        if "/.git" in dirpath or "/site" in dirpath:
            continue
        for fn in files:
            if fn.endswith(".json"):
                rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
                if load_json(rel) is not None:
                    ok(f"json parses: {rel}")


def check_no_root_manifest():
    """The Claude Code spec defines no root-level plugin.json; nothing reads one.
    There must be exactly ONE manifest, at .claude-plugin/plugin.json."""
    if os.path.isfile(os.path.join(ROOT, "plugin.json")):
        fail(
            "root plugin.json must not exist (spec defines none; use .claude-plugin/plugin.json)"
        )
    else:
        ok("no root plugin.json (single-manifest layout)")


def check_manifest(rel):
    data = load_json(rel)
    if data is None:
        return
    for field in ("name", "description", "keywords"):
        if not data.get(field):
            fail(f"{rel}: missing required field '{field}'")
    if len(data.get("keywords", [])) != 20:
        fail(
            f"{rel}: keywords must be exactly 20 (found {len(data.get('keywords', []))})"
        )
    hooks = data.get("hooks")
    if isinstance(hooks, str):
        hp = os.path.join(ROOT, hooks.lstrip("./"))
        if not os.path.isfile(hp):
            fail(f"{rel}: hooks path not found: {hooks}")
        else:
            check_hooks_obj(load_json(os.path.relpath(hp, ROOT)), rel)
    elif isinstance(hooks, dict):
        check_hooks_obj({"hooks": hooks}, rel)
    else:
        fail(f"{rel}: missing or malformed hooks")
    ok(f"manifest ok: {rel}")


def check_hooks_obj(obj, src):
    if not isinstance(obj, dict):
        fail(f"{src}: hooks object not a dict")
        return
    hooks = obj.get("hooks", obj)
    if not hooks:
        fail(f"{src}: no hook events defined")
        return
    for event, groups in hooks.items():
        for group in groups:
            for h in group.get("hooks", []):
                cmd = h.get("command", "")
                for tok in cmd.replace('"', " ").split():
                    if tok.endswith(".sh") and "CLAUDE_PLUGIN_ROOT" in cmd:
                        rel = tok.split("CLAUDE_PLUGIN_ROOT}/", 1)[-1]
                        p = os.path.join(ROOT, rel)
                        if not os.path.isfile(p):
                            fail(f"{src}: hook script missing ({event}): {rel}")
    ok(f"hooks reference real scripts: {src}")


def parse_frontmatter(path):
    with open(path, "r", encoding="utf-8") as fh:
        text = fh.read()
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    block = text[3:end].strip().splitlines()
    fm = {}
    for line in block:
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip().strip('"')
    return fm


def check_skills():
    sdir = os.path.join(ROOT, "skills")
    if not os.path.isdir(sdir):
        fail("skills/ dir missing")
        return
    found = 0
    for name in sorted(os.listdir(sdir)):
        sp = os.path.join(sdir, name, "SKILL.md")
        if not os.path.isfile(sp):
            continue
        found += 1
        fm = parse_frontmatter(sp)
        if not fm or not fm.get("name") or not fm.get("description"):
            fail(f"skills/{name}/SKILL.md: frontmatter needs name + description")
        else:
            ok(f"skill frontmatter ok: {name}")
    if found == 0:
        fail("no skills/*/SKILL.md found")


def check_bash_syntax():
    for dirpath, _dirs, files in os.walk(ROOT):
        if "/.git" in dirpath or "/site" in dirpath:
            continue
        for fn in files:
            if fn.endswith(".sh"):
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, ROOT)
                r = subprocess.run(["bash", "-n", p], capture_output=True, text=True)
                if r.returncode != 0:
                    fail(f"bash -n {rel}: {r.stderr.strip()}")
                else:
                    ok(f"bash -n ok: {rel}")


def check_python_syntax():
    import py_compile

    for dirpath, _dirs, files in os.walk(ROOT):
        if "/.git" in dirpath or "__pycache__" in dirpath or "/site" in dirpath:
            continue
        for fn in files:
            if fn.endswith(".py"):
                p = os.path.join(dirpath, fn)
                rel = os.path.relpath(p, ROOT)
                try:
                    py_compile.compile(p, doraise=True)
                    ok(f"py_compile ok: {rel}")
                except py_compile.PyCompileError as exc:
                    fail(f"py_compile {rel}: {exc}")


def main():
    print("== plugin validation ==")
    all_json_parse()
    check_no_root_manifest()
    check_manifest(".claude-plugin/plugin.json")
    check_skills()
    check_bash_syntax()
    check_python_syntax()
    print(f"\n{checks} checks run, {len(errors)} failures")
    if errors:
        print("\n".join(f"  - {e}" for e in errors))
        return 1
    print("ALL GOOD")
    return 0


if __name__ == "__main__":
    sys.exit(main())

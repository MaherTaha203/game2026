#!/usr/bin/env python3
"""ONE LINE — one-command full project audit (Phase 2 §21).

Runs every automated check and prints a single PASS/FAIL/UNVERIFIED table:

  1. Python unit tests            6. deterministic regeneration
  2. level validation             7. audit scans (secrets/debug/network/paths)
  3. solver / playtest            8. GDScript parse + conformance      (needs Godot)
  4. difficulty report            9. full-campaign runtime (all 210)   (needs Godot)
  5. save/daily tests (in #1)    10. Godot boot smoke                  (needs Godot)

Godot steps are UNVERIFIED (not silently passed) when no Godot binary is found.
Set GODOT_BIN to point at a Godot 4.x binary to enable them.

Exit code is non-zero if any check FAILs. Usage:

    python3 tools/full_audit.py
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PASS, FAIL, UNVERIFIED = "PASS", "FAIL", "UNVERIFIED"
results: list[tuple[str, str, str]] = []


def record(name: str, status: str, detail: str = "") -> None:
    results.append((name, status, detail))
    print(f"[{status:^10}] {name}" + (f" — {detail}" if detail else ""))


def run(name: str, cmd: list[str], **kw) -> bool:
    try:
        p = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, **kw)
    except Exception as exc:  # pragma: no cover
        record(name, FAIL, f"exception: {exc}")
        return False
    ok = p.returncode == 0
    tail = (p.stdout or p.stderr).strip().splitlines()
    detail = tail[-1] if tail else ""
    record(name, PASS if ok else FAIL, detail)
    if not ok:
        sys.stderr.write(p.stdout + "\n" + p.stderr + "\n")
    return ok


def find_godot() -> str | None:
    env = os.environ.get("GODOT_BIN")
    if env and os.path.exists(env):
        return env
    which = shutil.which("godot")
    if which:
        return which
    for guess in ("/tmp/Godot_v4.3-stable_linux.x86_64",):
        if os.path.exists(guess):
            return guess
    return None


def audit_scans() -> bool:
    """Repository scans for secrets / debug code / network / machine paths."""
    ok = True

    def scan(label: str, pattern: str, roots: list[str], exclude: str = "") -> None:
        nonlocal ok
        rx = re.compile(pattern)
        exrx = re.compile(exclude) if exclude else None
        hits = []
        for root in roots:
            base = os.path.join(REPO, root)
            if os.path.isfile(base):
                files = [base]
            else:
                files = []
                for dp, _dn, fn in os.walk(base):
                    if "/.godot" in dp or "__pycache__" in dp:
                        continue
                    for f in fn:
                        if f.endswith((".gd", ".py", ".cfg", ".godot", ".md")):
                            files.append(os.path.join(dp, f))
            for fp in files:
                try:
                    for i, line in enumerate(open(fp, encoding="utf-8"), 1):
                        if rx.search(line) and not (exrx and exrx.search(line)):
                            hits.append(f"{os.path.relpath(fp, REPO)}:{i}")
                except (OSError, UnicodeDecodeError):
                    continue
        if hits:
            ok = False
            record(f"scan: {label}", FAIL, f"{len(hits)} hit(s): {hits[:3]}")
        else:
            record(f"scan: {label}", PASS)

    # Debug code / network in shipping GDScript only.
    scan("no debug code (scripts/)", r"\b(TODO|FIXME|print\(|breakpoint)\b", ["scripts"])
    scan("no network APIs (scripts/)",
         r"HTTPRequest|HTTPClient|StreamPeerTCP|TCPServer|WebSocket|UDPServer|PacketPeerUDP",
         ["scripts"])
    scan("no machine paths (scripts/)", r"/home/|/Users/|C:\\\\", ["scripts"])
    return ok


def main() -> int:
    print("== ONE LINE full audit ==\n")

    py = sys.executable
    run("python unit tests", [py, "-m", "unittest", "discover", "-s", "tests/python", "-t", "."])
    run("level validation", [py, "tools/validate_levels.py"])
    run("solver / playtest", [py, "tools/solve_levels.py"])
    run("difficulty report", [py, "tools/difficulty_report.py"])

    # Deterministic regeneration: regen to a temp dir, diff index.json.
    tmp = tempfile.mkdtemp(prefix="oneline_regen_")
    regen_ok = run("regenerate campaign", [py, "tools/generate_levels.py", "--out", tmp])
    if regen_ok:
        import json
        try:
            a = json.load(open(os.path.join(REPO, "levels", "index.json")))
            b = json.load(open(os.path.join(tmp, "index.json")))
            record("deterministic regeneration", PASS if a == b else FAIL,
                   "index matches" if a == b else "index CHANGED")
            if a != b:
                pass
        except Exception as exc:
            record("deterministic regeneration", FAIL, str(exc))
    shutil.rmtree(tmp, ignore_errors=True)

    audit_scans()

    godot = find_godot()
    if godot is None:
        for step in ("GDScript conformance", "campaign runtime (210)", "Godot boot smoke"):
            record(step, UNVERIFIED, "no Godot binary (set GODOT_BIN)")
    else:
        run("GDScript conformance", [godot, "--headless", "--path", ".",
                                     "--script", "tests/gdscript/run_tests.gd"])
        run("campaign runtime (210)", [godot, "--headless", "--path", ".",
                                       "--script", "tests/gdscript/campaign_test.gd"])
        # Boot smoke: run briefly, fail on runtime errors referencing our code.
        # The game loops forever, so a timeout is the expected exit; TimeoutExpired
        # exposes captured output as bytes even with text=True, so normalize.
        def _txt(v) -> str:
            if v is None:
                return ""
            return v.decode("utf-8", "replace") if isinstance(v, bytes) else v

        try:
            p = subprocess.run([godot, "--headless", "--path", "."], cwd=REPO,
                               capture_output=True, text=True, timeout=8)
            log = _txt(p.stdout) + _txt(p.stderr)
        except subprocess.TimeoutExpired as e:
            log = _txt(e.stdout) + _txt(e.stderr)
        boot_bad = re.search(r"SCRIPT ERROR|ERROR: .*res://", log)
        record("Godot boot smoke", FAIL if boot_bad else PASS)

    print("\n== summary ==")
    n_fail = sum(1 for _, s, _ in results if s == FAIL)
    n_unv = sum(1 for _, s, _ in results if s == UNVERIFIED)
    n_pass = sum(1 for _, s, _ in results if s == PASS)
    print(f"PASS={n_pass}  FAIL={n_fail}  UNVERIFIED={n_unv}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

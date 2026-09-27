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


def _campaign_files(root: str) -> set[str]:
    """Relative names of campaign data files in a directory."""
    names = set()
    for f in os.listdir(root):
        if f == "index.json" or (f.startswith("level_") and f.endswith(".json")):
            names.add(f)
    return names


def compare_campaign(committed: str, regen: str) -> list[str]:
    """Compare two campaign directories fully. Returns a list of human-readable
    differences (empty == identical). Checks the file SET (paths + counts) and
    byte-for-byte content of every file present in either directory."""
    a = _campaign_files(committed)
    b = _campaign_files(regen)
    diffs: list[str] = []
    for missing in sorted(a - b):
        diffs.append(f"missing from regen: {missing}")
    for extra in sorted(b - a):
        diffs.append(f"unexpected in regen: {extra}")
    if len(a) != len(b):
        diffs.append(f"file count differs: committed={len(a)} regen={len(b)}")
    for name in sorted(a & b):
        with open(os.path.join(committed, name), "rb") as fh:
            ca = fh.read()
        with open(os.path.join(regen, name), "rb") as fh:
            cb = fh.read()
        if ca != cb:
            diffs.append(f"content differs: {name}")
    return diffs


def secret_scan() -> bool:
    """Explicit, reproducible scan for accidentally committed credentials and
    signing material across ALL Git-tracked files (not just .gd/.md).

    Never prints a matched secret value — only the file, line number and which
    rule fired. Known-safe placeholders/patterns are excluded to separate real
    findings from false positives.
    """
    ok = True
    try:
        tracked = subprocess.run(
            ["git", "ls-files"], cwd=REPO, capture_output=True, text=True, check=True
        ).stdout.splitlines()
    except Exception as exc:
        record("secret scan (git-tracked)", FAIL, f"git ls-files failed: {exc}")
        return False

    # Content rules. Patterns are conservative to limit false positives.
    content_rules = [
        ("AWS access key id", re.compile(r"AKIA[0-9A-Z]{16}")),
        ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY-----")),
        ("google api key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
        ("slack token", re.compile(r"xox[baprs]-[0-9A-Za-z-]{10,}")),
        ("github token", re.compile(r"gh[pousr]_[0-9A-Za-z]{36,}")),
        ("generic secret assignment",
         re.compile(r"(?i)(password|passwd|secret|api[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}['\"]")),
        ("keystore/signing password prop",
         re.compile(r"(?i)(storePassword|keyPassword|keyalias\s*password)\s*[:=]\s*\S+")),
    ]
    # Lines that look like secrets but are safe (docs, placeholders, empty fields).
    safe_line = re.compile(
        r"(?i)(placeholder|example|never commit|do not commit|<your|your-|changeme|"
        r"redacted|xxxx|\.\.\.|=\s*['\"]?\s*['\"]?\s*$|password\"\s*:|signature=\"\")"
    )
    # File extensions/names that must never be committed at all (signing material).
    forbidden_ext = re.compile(r"\.(keystore|jks|p12|pfx|mobileprovision|pem|key|cer|der|p8)$", re.I)
    forbidden_name = re.compile(r"(?i)(id_rsa|id_ed25519|\.env$|secrets?\.(json|ya?ml|txt))")

    findings: list[str] = []
    for rel in tracked:
        # 1) Forbidden file types (signing / secret files).
        if forbidden_ext.search(rel) or forbidden_name.search(rel):
            findings.append(f"{rel}: forbidden file type committed")
            continue
        path = os.path.join(REPO, rel)
        if not os.path.isfile(path):
            continue
        # Skip obvious binaries and large files.
        if os.path.getsize(path) > 2_000_000:
            continue
        try:
            with open(path, "r", encoding="utf-8") as fh:
                for i, line in enumerate(fh, 1):
                    if safe_line.search(line):
                        continue
                    for label, rx in content_rules:
                        if rx.search(line):
                            findings.append(f"{rel}:{i}: {label}")
        except (OSError, UnicodeDecodeError):
            continue  # binary or unreadable; extension check already covered files

    if findings:
        ok = False
        record("secret scan (git-tracked)", FAIL,
               f"{len(findings)} finding(s): {findings[:5]}")
        sys.stderr.write("Secret-scan findings (values NOT shown):\n  "
                         + "\n  ".join(findings) + "\n")
    else:
        record("secret scan (git-tracked)", PASS,
               f"scanned {len(tracked)} tracked files; no secrets/signing material")
    return ok


def run_only_campaign() -> int:
    """CI helper: regenerate to a temp dir and compare the full campaign."""
    py = sys.executable
    tmp = tempfile.mkdtemp(prefix="oneline_regen_")
    try:
        r = subprocess.run([py, "tools/generate_levels.py", "--out", tmp], cwd=REPO)
        if r.returncode != 0:
            print("FAIL: generation failed")
            return 1
        diffs = compare_campaign(os.path.join(REPO, "levels"), tmp)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    if diffs:
        print(f"FAIL: {len(diffs)} campaign file difference(s):")
        for d in diffs:
            print("  " + d)
        return 1
    print("PASS: full campaign reproduces byte-for-byte")
    return 0


def run_only_secrets() -> int:
    return 0 if secret_scan() else 1


def main() -> int:
    # Focused CI entry points.
    if len(sys.argv) > 1 and sys.argv[1] == "--only":
        which = sys.argv[2] if len(sys.argv) > 2 else ""
        if which == "campaign":
            return run_only_campaign()
        if which == "secrets":
            return run_only_secrets()
        print(f"unknown --only target: {which!r}")
        return 2

    print("== ONE LINE full audit ==\n")

    py = sys.executable
    run("python unit tests", [py, "-m", "unittest", "discover", "-s", "tests/python", "-t", "."])
    run("level validation", [py, "tools/validate_levels.py"])
    run("solver / playtest", [py, "tools/solve_levels.py"])
    run("difficulty report", [py, "tools/difficulty_report.py"])

    # Deterministic regeneration: regen to a temp dir and compare the ENTIRE
    # campaign (index.json + every level_*.json) by path, count and byte content.
    # The committed campaign is never overwritten (regen goes to a temp dir).
    tmp = tempfile.mkdtemp(prefix="oneline_regen_")
    regen_ok = run("regenerate campaign", [py, "tools/generate_levels.py", "--out", tmp])
    if regen_ok:
        try:
            diffs = compare_campaign(os.path.join(REPO, "levels"), tmp)
            if not diffs:
                record("deterministic full campaign", PASS,
                       "all campaign files match byte-for-byte")
            else:
                record("deterministic full campaign", FAIL,
                       f"{len(diffs)} differing file(s): {diffs[:5]}")
                sys.stderr.write("Campaign differences:\n  " + "\n  ".join(diffs) + "\n")
        except Exception as exc:
            record("deterministic full campaign", FAIL, str(exc))
    shutil.rmtree(tmp, ignore_errors=True)

    audit_scans()
    secret_scan()

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

"""Build a paper's Lean project, audit every theorem, and record source hashes."""
from pathlib import Path
import subprocess
import hashlib
import json
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent
NAMESPACE = "FinGNO"
if shutil.which("lake") is None:
    raise SystemExit("Install the pinned Lean toolchain with elan, then put lake on PATH.")

sources = sorted((ROOT/NAMESPACE).glob("*.lean"))
records = []
for path in sources:
    content = path.read_text()
    if re.search(r"\b(sorry|admit)\b|^\s*(axiom|unsafe)\b", content, re.M):
        raise SystemExit(f"Unapproved proof escape found in {path.name}")
    for match in re.finditer(r"^theorem\s+(\w+)", content, re.M):
        records.append({"name": NAMESPACE+"."+match.group(1),
                        "source": str(path.relative_to(ROOT))})
expected_audit = "import "+NAMESPACE+"\n\n" + "\n".join(
    "#print axioms "+r["name"] for r in records)+"\n"
if (ROOT/"Audit.lean").read_text() != expected_audit:
    raise SystemExit("Audit.lean must enumerate every current theorem declaration.")

def run(args, log_name):
    result = subprocess.run(args, cwd=ROOT, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    (ROOT/log_name).write_text(result.stdout)
    if result.returncode:
        print(result.stdout)
        raise SystemExit(result.returncode)
    return result.stdout

version = subprocess.check_output(["lean", "--version"], cwd=ROOT, text=True).strip()
run(["lake", "build"], "build.log")
audit = run(["lake", "env", "lean", "Audit.lean"], "axioms.log")
allowed = {"propext", "Classical.choice", "Quot.sound"}
for record in records:
    match = re.search(re.escape("'"+record["name"]+"'") +
                      r" (?:depends on axioms: \[([^\]]*)\]|does not depend on any axioms)", audit)
    if match is None:
        raise SystemExit(f"Missing axiom audit for {record['name']}")
    axioms = [] if match.group(1) is None else [
        a.strip() for a in match.group(1).split(",") if a.strip()]
    if set(axioms)-allowed:
        raise SystemExit(f"Unexpected axiom dependency in {record['name']}: {axioms}")
    record["axioms"] = axioms

hash_files = sources + [ROOT/f for f in
    (NAMESPACE+".lean", "Audit.lean", "lean-toolchain", "lakefile.toml", "lake-manifest.json")]
hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
          for p in sorted(hash_files)}
report = {"status": "PASS", "lean_version": version,
          "theorem_declarations_checked": len(records),
          "custom_axioms": [], "admitted_proofs": [],
          "declarations": records, "sha256": hashes,
          "scope": "See COVERAGE.md; no claim that every manuscript theorem is mechanized.",
          "runtime": "See README.md for any platform-specific executable discovery adjustment."}
(ROOT/"verification.json").write_text(json.dumps(report, indent=2)+"\n")
print(f"PASS: {len(records)} theorem declarations built and audited; no admitted proofs or custom axioms.")

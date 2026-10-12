"""Package only the explicit public synthetic proof assets; no private export."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]/"public/demos/aero/first-principles-hx-v1"
names = ["README.md", "inputs.json", "verify.py", "proof.tex", "proof.pdf", "results.json",
         "pressure-convergence.csv", "pressure-convergence.svg", "runtime-verification.json"]
entries = []
for name in names:
    data = (root/name).read_bytes()
    entries.append({"path": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
with zipfile.ZipFile(root/"sources.zip", "w", zipfile.ZIP_DEFLATED) as archive:
    for name in names:
        archive.write(root/name, arcname=name)
data = (root/"sources.zip").read_bytes()
entries.append({"path": "sources.zip", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
(root/"manifest.json").write_text(json.dumps({"schema": "aero.public.proof_manifest.v1", "date": "2026-10-12", "files": entries}, indent=2)+"\n", encoding="utf-8")
missing, mismatches = [], []
for entry in entries:
    path = root/entry["path"]
    if not path.is_file():
        missing.append(entry["path"])
    elif hashlib.sha256(path.read_bytes()).hexdigest() != entry["sha256"]:
        mismatches.append(entry["path"])
verification = {"checked": len(entries), "missing": len(missing), "mismatches": len(mismatches), "missing_files": missing, "mismatched_files": mismatches, "custody": "PASS" if not missing and not mismatches else "FAIL"}
(root/"verification.json").write_text(json.dumps(verification, indent=2)+"\n", encoding="utf-8")
print(json.dumps(verification))
if missing or mismatches:
    raise SystemExit(1)

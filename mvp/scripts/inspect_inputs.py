"""Validate supplied extracted archives before making an immutable local copy."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def safe_path(root, name):
    candidate = (root / name).resolve()
    if not candidate.is_relative_to(root.resolve()):
        raise ValueError(f"Escaping archive path: {name}")
    if any(p.is_symlink() for p in [root / name, *(root / name).parents] if p != root.parent):
        raise ValueError(f"Symlink in archive: {name}")
    return candidate


def verify(root):
    checks = []
    for line in (root / "MANIFEST.sha256").read_text(encoding="utf-8-sig").splitlines():
        expected, name = line.split(maxsplit=1)
        name = name.lstrip("*")
        target = safe_path(root, name)
        actual = digest(target) if target.is_file() else None
        checks.append({"path": name, "expected_sha256": expected, "actual_sha256": actual,
                       "status": "MATCH" if actual == expected else "MISMATCH"})
    if any(x["status"] != "MATCH" for x in checks):
        raise ValueError(checks)
    return checks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    bundle = args.bundle.resolve()
    originals = {
        "verification": bundle / "inputs/KASE_BondScope_Verification_Package/KASE_BondScope_Verification_2026-10-22",
        "task1": bundle / "inputs/KASE_BondScope_Task1_results/KASE_BondScope_Task1_2026-10-21",
    }
    report = {"input_surface": "already-extracted directories; original ZIP bytes absent",
              "archives": {}, "bundle_checks": []}
    for entry in json.loads((bundle / "BUNDLE_MANIFEST.json").read_text(encoding="utf-8"))["contents"]:
        f = safe_path(bundle, entry["path"])
        actual = digest(f) if f.is_file() else None
        status = "MISSING_ARCHIVE" if actual is None and f.suffix == ".zip" else (
            "MATCH" if actual == entry["sha256"] else "MISMATCH")
        report["bundle_checks"].append({"path": entry["path"], "status": status, "sha256": actual})
        if status == "MISMATCH":
            raise ValueError(f"Bundle hash mismatch: {f}")
    for name, source in originals.items():
        checks = verify(source)
        dest = ROOT / "data/raw/archive" / name
        for f in source.rglob("*"):
            safe_path(source, f.relative_to(source))
        if dest.exists():
            verify(dest)
        else:
            shutil.copytree(source, dest)
        report["archives"][name] = {"entries_checked": len(checks), "mismatches": 0,
                                    "checks": checks, "copy": str(dest.relative_to(ROOT))}
    out = ROOT / "implementation/input_integrity.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    from pypdf import PdfReader
    pdf = bundle / "inputs/KASE_case_stage1_Halyk_RU 1(2).pdf"
    reader = PdfReader(pdf)
    pages = [p.extract_text() for p in reader.pages]
    target = ROOT / "data/raw/case_text.txt"
    target.write_text("\n\n".join(f"PAGE {i+1}\n{p}" for i, p in enumerate(pages)), encoding="utf-8")
    print(json.dumps({"archives": {k: v["entries_checked"] for k, v in report["archives"].items()},
                      "case_pages": len(pages), "case_sha256": digest(pdf)}, indent=2))


if __name__ == "__main__":
    main()

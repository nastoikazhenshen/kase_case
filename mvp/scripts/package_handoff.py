"""Curated local handoff: one explicit evidence ZIP, never recursive archive discovery."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def main():
    evidence = json.loads((ROOT / "implementation/finalization/local_pack_manifest.json").read_text(encoding="utf8"))
    slides = json.loads((ROOT / "implementation/finalization/slides_manifest.json").read_text(encoding="utf8"))
    finance = json.loads((ROOT / "implementation/finalization/finance_workbook_changes.json").read_text(encoding="utf8"))
    pack = ROOT.parent / evidence["file"]
    assert hashlib.sha256(pack.read_bytes()).hexdigest() == evidence["sha256"]
    selected = [pack, ROOT / "README_run.md", ROOT / "slides_mvp.md", ROOT / "handoff/slides_6_7_notes.md",
                ROOT / "handoff/technical_delivery.md", ROOT / "handoff/data_limits.md", ROOT / "handoff/finance_consistency.md",
                ROOT.parent / finance["output_workbook"], ROOT.parent / slides["screenshot_path"],
                *(ROOT.parent / item["path"] for item in slides["artifacts"])]
    selected.extend(ROOT / "outputs" / name for name in ("report.json", "report.html", "mvp_results.csv", "mvp_results.xlsx"))
    selected.extend(ROOT / "outputs/final/demo" / name for name in ("report.json", "report.html", "mvp_results.csv", "mvp_results.xlsx"))
    selected.extend(sorted((ROOT / "outputs/final/app").glob("*.png")))
    assert len(selected) == len(set(selected))
    assert [p for p in selected if p.suffix.lower() == ".zip"] == [pack]
    records = []
    for path in selected:
        assert path.is_file() and not path.is_symlink() and path.resolve().is_relative_to(ROOT.resolve()), path
        payload = path.read_bytes()
        records.append({"path": path.relative_to(ROOT).as_posix(), "bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()})
    manifest = {"format": "BondScope-Participant2-handoff-1", "implementation_sha": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                "delivery": "LOCAL_ONLY; redistribution rights unresolved", "evidence_pack_sha256": evidence["sha256"], "files": records}
    destination = ROOT / "local_pack/BondScope_Participant2_Final_20261022.zip"
    with ZipFile(destination, "x", compression=ZIP_DEFLATED) as archive:
        for record, path in zip(records, selected):
            archive.writestr(ZipInfo(record["path"], (2026, 10, 22, 0, 0, 0)), path.read_bytes(), compress_type=ZIP_DEFLATED)
        archive.writestr(ZipInfo("handoff_manifest.json", (2026, 10, 22, 0, 0, 0)), json.dumps(manifest, ensure_ascii=False, indent=2))
    with ZipFile(destination) as archive:
        assert archive.testzip() is None
        for record in records:
            assert hashlib.sha256(archive.read(record["path"])).hexdigest() == record["sha256"]
    public = {"file": destination.relative_to(ROOT.parent).as_posix(), "bytes": destination.stat().st_size,
              "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(), "file_count": len(records),
              "implementation_sha": manifest["implementation_sha"], "evidence_pack_sha256": evidence["sha256"],
              "nested_archives": [evidence["file"]], "recursive_archive_inclusion": False, "delivery": "LOCAL_ONLY_NOT_IN_PUBLIC_GIT"}
    (ROOT / "implementation/finalization/handoff_manifest.json").write_text(json.dumps(public, indent=2) + "\n", encoding="utf8")
    print(json.dumps(public))


if __name__ == "__main__":
    main()

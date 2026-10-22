"""Create the local-only evidence ZIP; never add this pack to public version control."""
from __future__ import annotations

import hashlib
import json
import argparse
from pathlib import Path
import sys
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
from mvp.src.repository import load_snapshot


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", default="bondscope-evidence-final-20261022.zip")
    args = parser.parse_args()
    if Path(args.name).name != args.name or not args.name.endswith(".zip") or args.name == "bondscope-evidence.zip":
        raise ValueError("Use a new simple ZIP filename; the previous release is immutable")
    snapshot = load_snapshot()
    slides = json.loads((ROOT / "implementation/finalization/slides_manifest.json").read_text(encoding="utf8"))
    final_slides = {record["path"] for record in slides["artifacts"]}
    final_slides.add(slides["screenshot_path"])
    files = []
    for directory in ("data/raw/archive", "data/raw/acquisition", "data/raw/finalization", "data/raw/style", "data/processed", "outputs", "mvp_screenshots"):
        for path in sorted((ROOT / directory).rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Symlink rejected: {path}")
            if path.name.startswith("slides6_7") and path.relative_to(ROOT.parent).as_posix() not in final_slides:
                continue  # Only the reviewed final slide version; keep drafts locally outside this delivery.
            if path.is_file() and "__pycache__" not in path.parts and path.suffix not in {".pyc", ".tmp", ".zip", ".gz", ".tar"} and path.name != "README.md":
                files.append(path)
    records = [{"path": p.relative_to(ROOT).as_posix(), "bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files]
    manifest = {"format": "BS3-local-evidence-1", "snapshot_sha256": snapshot["release"]["snapshot_sha256"], "files": records}
    directory = ROOT / "local_pack"
    directory.mkdir(exist_ok=True)
    destination = directory / args.name
    with ZipFile(destination, "x", compression=ZIP_DEFLATED) as archive:
        # Fixed ZIP timestamps make the delivery deterministic for identical bytes.
        for record, file in zip(records, files):
            info = ZipInfo(record["path"], (2026, 10, 22, 0, 0, 0))
            archive.writestr(info, file.read_bytes(), compress_type=ZIP_DEFLATED)
        archive.writestr(ZipInfo("pack_manifest.json", (2026, 10, 22, 0, 0, 0)), json.dumps(manifest, ensure_ascii=False, sort_keys=True))
    public = {"file": "mvp/local_pack/" + args.name, "delivery": "LOCAL_ONLY_NOT_IN_PUBLIC_GIT",
              "snapshot_id": snapshot["release"]["snapshot_id"], "bytes": destination.stat().st_size,
              "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(), "file_count": len(files)}
    (ROOT / "implementation/finalization/local_pack_manifest.json").write_text(json.dumps(public, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(public))


if __name__ == "__main__":
    main()

"""Restore the separate local evidence delivery without overwriting different files.

No network access, code execution or general-purpose archive extraction. Paths,
member types, sizes and SHA-256 are verified before the first write.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = ("data/raw/", "data/processed/", "outputs/", "mvp_screenshots/")
MAX_BYTES = 256 * 1024 * 1024


def safe_destination(root, name):
    parts = PurePosixPath(name).parts
    if (not name.startswith(ALLOWED) or "\\" in name or ":" in name or name.startswith("/")
            or any(p in {"", ".", ".."} or p.rstrip(" .") != p for p in name.split("/"))
            or any(re.match(r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)", p, re.I) for p in parts)):
        raise ValueError(f"Unsafe or out-of-scope pack path: {name}")
    root = Path(root).resolve()
    target = root.joinpath(*parts)
    if not target.resolve().is_relative_to(root):
        raise ValueError("Pack path escapes destination")
    if any(p.is_symlink() for p in (target, *target.parents) if p.is_relative_to(root)):
        raise ValueError("Symlink in destination path")
    return target


def restore(pack, root=ROOT):
    with ZipFile(pack) as archive:
        infos = archive.infolist()
        names = [i.filename for i in infos]
        if len(names) != len(set(n.casefold() for n in names)):
            raise ValueError("Duplicate/case-colliding ZIP members")
        if sum(i.file_size for i in infos) > MAX_BYTES:
            raise ValueError("Evidence pack exceeds bounded size")
        if "pack_manifest.json" not in names:
            raise ValueError("Missing pack manifest")
        manifest = json.loads(archive.read("pack_manifest.json"))
        if manifest.get("format") != "BS3-local-evidence-1":
            raise ValueError("Unsupported pack format")
        records = manifest["files"]
        record_map = {r["path"]: r for r in records}
        if len(record_map) != len(records) or set(names) != {*record_map, "pack_manifest.json"}:
            raise ValueError("Manifest/member set mismatch")
        staged = []
        for info in infos:
            mode = info.external_attr >> 16
            if info.is_dir() or stat.S_ISLNK(mode) or (stat.S_IFMT(mode) not in (0, stat.S_IFREG)):
                raise ValueError("Only ordinary files are allowed")
            if info.filename == "pack_manifest.json":
                continue
            target = safe_destination(root, info.filename)
            payload = archive.read(info)
            expected = record_map[info.filename]
            if len(payload) != expected["bytes"] or hashlib.sha256(payload).hexdigest() != expected["sha256"]:
                raise ValueError(f"Pack content hash/size mismatch: {info.filename}")
            if target.exists() and (not target.is_file() or target.read_bytes() != payload):
                raise ValueError(f"Refusing to overwrite different existing content: {info.filename}")
            staged.append((target, payload))
        # The tracked release manifest pins the expected market snapshot for this checkout.
        release_file = Path(root) / "implementation/release_manifest.json"
        if release_file.exists():
            expected = json.loads(release_file.read_text(encoding="utf-8"))["snapshot_sha256"]
            if manifest["snapshot_sha256"] != expected or record_map["data/processed/snapshot.json"]["sha256"] != expected:
                raise ValueError("Pack does not match this checkout's release")
        written = 0
        for target, payload in staged:
            if not target.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as out:
                    out.write(payload)
                written += 1
    return {"verified_files": len(staged), "written_files": written, "snapshot_sha256": manifest["snapshot_sha256"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pack", type=Path)
    args = parser.parse_args()
    result = restore(args.pack)
    sys.path.insert(0, str(ROOT.parent))
    from mvp.src.repository import load_snapshot
    snapshot = load_snapshot()
    result["snapshot_id"] = snapshot["release"]["snapshot_id"]
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

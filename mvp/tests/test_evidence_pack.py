"""Synthetic archive attack fixtures only; never part of market evidence."""
import hashlib
import json
from pathlib import Path
import stat
import tempfile
import unittest
from zipfile import ZipFile, ZipInfo

from mvp.scripts.restore_evidence import restore


class EvidencePackTests(unittest.TestCase):
    def pack(self, folder, name="data/raw/test.txt", payload=b"test-only", bad_hash=False, symlink=False):
        path = Path(folder) / "test.zip"
        manifest = {"format": "BS3-local-evidence-1", "snapshot_sha256": "test-only",
                    "files": [{"path": name, "bytes": len(payload), "sha256": "0" * 64 if bad_hash else hashlib.sha256(payload).hexdigest()}]}
        with ZipFile(path, "w") as zipfile:
            info = ZipInfo(name)
            if symlink:
                info.create_system = 3
                info.external_attr = (stat.S_IFLNK | 0o777) << 16
            zipfile.writestr(info, payload)
            zipfile.writestr("pack_manifest.json", json.dumps(manifest))
        return path

    def test_restore_is_idempotent_and_never_overwrites_different_content(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "destination"
            pack = self.pack(td)
            self.assertEqual(restore(pack, root)["written_files"], 1)
            self.assertEqual(restore(pack, root)["written_files"], 0)
            (root / "data/raw/test.txt").write_bytes(b"teammate-content")
            with self.assertRaisesRegex(ValueError, "overwrite"):
                restore(pack, root)

    def test_traversal_windows_alias_and_code_paths_are_rejected(self):
        for name in ("../escape", "data/raw/../../escape", "data/raw/x:stream", "data/raw/CON.txt", "data/raw/x.", "data/raw/a\\b", "src/app.py"):
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                with self.assertRaises(ValueError):
                    restore(self.pack(td, name), Path(td) / "dest")

    def test_hash_failure_and_symlinks_write_nothing(self):
        for kwargs in ({"bad_hash": True}, {"symlink": True}):
            with tempfile.TemporaryDirectory() as td:
                root = Path(td) / "dest"
                with self.assertRaises(ValueError):
                    restore(self.pack(td, **kwargs), root)
                self.assertFalse(root.exists())


if __name__ == "__main__":
    unittest.main()

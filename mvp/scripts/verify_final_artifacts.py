"""Read-only cross-format checks; requires the separate local final evidence pack."""
from __future__ import annotations

import csv
import hashlib
import json
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
import sys
from zipfile import ZipFile
import xml.etree.ElementTree as ET

import openpyxl
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent))
from mvp.src.demo import DEMO_RULE, demo_report
from mvp.src.repository import load_snapshot


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    expected = demo_report(load_snapshot())
    output = ROOT / "outputs/final/demo"
    report = json.loads((output / "report.json").read_text(encoding="utf8"))
    assert report == expected, "Example JSON is stale"
    with (output / "mvp_results.csv").open(encoding="utf-8-sig", newline="") as source:
        csv_rows = list(csv.DictReader(source))
    assert {r["report_id"] for r in csv_rows} == {report["report_id"]}
    rows = [r for r in csv_rows if r["record_type"] == "EVALUATION"]
    assert len(rows) == len(report["evaluations"]) == 6
    workbook = openpyxl.load_workbook(output / "mvp_results.xlsx", data_only=True)
    obs, rules = workbook["Наблюдения"], workbook["Правила"]
    assert obs["B5"].value == report["report_id"]
    assert obs["B4"].value == report["planned_amount_kzt"]
    amount = Decimal(str(report["planned_amount_kzt"]))
    turnover = Decimal(report["observations"][0]["turnover_mln_kzt"]) * Decimal("1000000")
    ratio = float(amount / turnover)
    assert abs(obs["I9"].value - ratio) < 1e-12
    assert obs["G9"].value is None and obs["H9"].value is None, "Gated prices became values"
    for i, (csv_row, evaluation) in enumerate(zip(rows, report["evaluations"]), start=2):
        assert csv_row["rule"] == rules.cell(i, 3).value == evaluation["rule"]
        assert csv_row["status"] == rules.cell(i, 6).value == evaluation["status"]
        value = evaluation["value"]
        if value is not None:
            assert abs(float(csv_row["value"]) - value) < 1e-12
            assert abs(rules.cell(i, 4).value - value) < 1e-12
        else:
            assert csv_row["value"] == "" and rules.cell(i, 4).value is None
    assert report["report_id"] in (output / "report.html").read_text(encoding="utf8")
    assert "Условный ввод пользователя" in (output / "report.html").read_text(encoding="utf8")
    default = openpyxl.load_workbook(ROOT / "outputs/mvp_results.xlsx", data_only=True)
    assert default["Наблюдения"]["B4"].value is None
    assert default["Наблюдения"]["I9"].value is None

    manifest = json.loads((ROOT / "implementation/finalization/slides_manifest.json").read_text(encoding="utf8"))
    assert manifest["report_id"] == report["report_id"]
    assert manifest["snapshot_id"] == report["snapshot_id"]
    assert digest(ROOT.parent / manifest["screenshot_path"]) == manifest["screenshot_sha256"]
    for artifact in manifest["artifacts"]:
        path = ROOT.parent / artifact["path"]
        assert path.is_file() and path.stat().st_size == artifact["bytes"]
        assert digest(path) == artifact["sha256"], str(path)
    deck = next(ROOT.parent / a["path"] for a in manifest["artifacts"] if a["path"].endswith(".pptx"))
    with ZipFile(deck) as archive:
        slides = [name for name in archive.namelist() if name.startswith("ppt/slides/slide") and name.endswith(".xml")]
        assert len(slides) == 2
        texts = [" ".join(ET.fromstring(archive.read(name)).itertext()) for name in sorted(slides)]
        assert report["report_id"] in texts[0]
        assert f"{float(turnover):,.0f}".replace(",", " ") in texts[0]
        assert f"{ratio * 100:.2f}".replace(".", ",") in texts[0]
        assert all(label in texts[1] for label in ("Монитор", "ликвидности", "События эмитента", "M1", "M6"))
        media_hashes = {hashlib.sha256(archive.read(n)).hexdigest() for n in archive.namelist() if n.startswith("ppt/media/")}
        assert manifest["screenshot_sha256"] in media_hashes, "PPTX does not embed the verified screenshot bytes"
    pdf = next(ROOT.parent / a["path"] for a in manifest["artifacts"] if a["path"].endswith(".pdf"))
    assert len(PdfReader(pdf).pages) == 2
    finance = json.loads((ROOT / "implementation/finalization/finance_workbook_changes.json").read_text(encoding="utf8"))
    assert digest(ROOT.parent / finance["source_workbook"]) == finance["source_sha256"]
    assert digest(ROOT.parent / finance["output_workbook"]) == finance["output_sha256"]
    checks = {"verified_at_utc": datetime.now(timezone.utc).isoformat(), "result": "PASS", "report_id": report["report_id"],
              "checks": ["UI-linked preset JSON equals freshly built canonical report", "CSV/JSON/HTML/XLSX values and gates agree",
                         "default XLSX planned amount remains blank", "slide numerator/denominator/result and report identity agree",
                         "PPTX has exactly two editable slides and embeds verified screenshot", "actual two-page PDF and PNG hashes verified",
                         "original and corrected finance workbook hashes match recorded provenance"],
              "formal_rule": DEMO_RULE, "slides_manifest_sha256": digest(ROOT / "implementation/finalization/slides_manifest.json")}
    (ROOT / "reviews/finalization/artifact_checks.json").write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf8")
    print(json.dumps(checks, ensure_ascii=False))


if __name__ == "__main__":
    main()

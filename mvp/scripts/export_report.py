"""Export the reproducible latest-date report without private user inputs."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from mvp.src.repository import ROOT, load_snapshot
from mvp.src.reports import build_report, report_csv, report_html
from mvp.src.build_snapshot import write_csv


def main():
    snapshot = load_snapshot()
    latest = max(r["trade_date"] for r in snapshot["observations"])
    rows = [r for r in snapshot["observations"] if r["trade_date"] == latest]
    report = build_report(snapshot, rows, latest)
    output = ROOT / "outputs"
    output.mkdir(exist_ok=True)
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "mvp_results.csv").write_bytes(report_csv(report))
    (output / "report.html").write_text(report_html(report), encoding="utf-8")
    write_csv(ROOT / "data/processed/rule_evaluations.csv", report["evaluations"])
    print(report["report_id"])


if __name__ == "__main__":
    main()

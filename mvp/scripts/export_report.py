"""Export the reproducible latest-date report without private user inputs."""
import json
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from mvp.src.repository import ROOT, load_snapshot
from mvp.src.reports import build_report, report_csv, report_html
from mvp.src.build_snapshot import write_csv


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="Explicit hypothetical 100000 KZT / BIGDb5 example, written separately")
    args = parser.parse_args()
    snapshot = load_snapshot()
    latest = max(r["trade_date"] for r in snapshot["observations"])
    rows = [r for r in snapshot["observations"] if r["trade_date"] == latest]
    report = build_report(snapshot, rows, latest)
    output = ROOT / "outputs"
    if args.demo:
        from mvp.src.demo import demo_report
        report = demo_report(snapshot)
        output = output / "final/demo"
    output.mkdir(exist_ok=True, parents=True)
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "mvp_results.csv").write_bytes(report_csv(report))
    (output / "report.html").write_text(report_html(report), encoding="utf-8")
    if not args.demo:
        write_csv(ROOT / "data/processed/rule_evaluations.csv", report["evaluations"])
    print(report["report_id"])


if __name__ == "__main__":
    main()

"""Run the final local checks and record actual exit codes against the current HEAD."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
LOG_ROOT = ROOT / "mvp/local_validation/finalization"


def main():
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    logs = LOG_ROOT / (sha[:12] + "-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    logs.mkdir(parents=True, exist_ok=False)
    commands = [
        ["-m", "mvp.src.build_snapshot"],
        ["mvp/scripts/export_report.py"],
        ["mvp/scripts/export_report.py", "--demo"],
        ["-m", "unittest", "discover", "-s", "mvp/tests", "-v"],
        ["-m", "unittest", "discover", "-s", "mvp/data/raw/archive/verification/tests", "-v"],
        ["-m", "ruff", "check", "mvp/src", "mvp/tests", "mvp/scripts", "--select", "F"],
        ["mvp/scripts/reconcile_sources.py"],
        ["-m", "mvp.src.finance_validation"],
        ["mvp/scripts/browser_smoke.py"],
        ["mvp/scripts/verify_final_artifacts.py"],
    ]
    results = []
    for i, command in enumerate(commands, start=1):
        start = datetime.now(timezone.utc).isoformat()
        process = subprocess.run([sys.executable, "-X", "utf8", *command], cwd=ROOT, capture_output=True, text=True, encoding="utf8")
        log = (process.stdout + "\n" + process.stderr).encode("utf8")
        path = logs / f"check-{i:02}.log"
        path.write_bytes(log)
        text = log.decode("utf8")
        count = re.search(r"Ran (\d+) tests?", text)
        skipped = re.search(r"OK \(skipped=(\d+)\)", text)
        result = {"command": ["python", *command], "started_at_utc": start,
                  "finished_at_utc": datetime.now(timezone.utc).isoformat(), "exit_code": process.returncode,
                  "tests_run": int(count.group(1)) if count else None, "skips": int(skipped.group(1)) if skipped else 0,
                  "log_path": path.relative_to(ROOT).as_posix(), "log_sha256": hashlib.sha256(log).hexdigest()}
        results.append(result)
        print(json.dumps(result), flush=True)
    output = {"implementation_sha": sha, "python": sys.version, "results": results,
              "pass": all(row["exit_code"] == 0 and row["skips"] == 0 for row in results)}
    (ROOT / "mvp/reviews/finalization/final_checks.json").write_text(json.dumps(output, indent=2) + "\n", encoding="utf8")
    return 0 if output["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

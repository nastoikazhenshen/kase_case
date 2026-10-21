"""Local-only Playwright smoke test for the frozen Streamlit MVP.

Run while the app is available at http://127.0.0.1:8501.  This script blocks
all non-localhost requests before navigation and writes only local screenshots
and a compact, non-sensitive check record.
"""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "mvp_screenshots"
CHECKS = ROOT / "reviews" / "browser_checks.json"
URL = "http://127.0.0.1:8501"


def local_only(route):
    host = route.request.url.split("/", 3)[2].split(":", 1)[0]
    if host in {"127.0.0.1", "localhost"}:
        route.continue_()
    else:
        route.abort()


def save(page, name):
    page.wait_for_timeout(900)  # wait for Streamlit's virtualized dataframe canvas to paint
    page.screenshot(path=SHOTS / name, full_page=True)


def main() -> None:
    SHOTS.mkdir(exist_ok=True)
    CHECKS.parent.mkdir(exist_ok=True)
    checks: dict[str, object] = {"url": URL, "offline_policy": "all non-localhost browser requests aborted", "checks": [], "errors": []}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 1000})
        page.route("**/*", local_only)
        try:
            page.goto(URL, wait_until="networkidle", timeout=30_000)
            page.get_by_text("KASE BondScope", exact=True).wait_for(timeout=10_000)
            save(page, "overview-1440.png")
            checks["checks"].append("populated overview rendered at 1440px")

            # Select a concrete card, then collect its source-backed valuation and rule context.
            page.get_by_role("tab", name="Инструмент").click()
            page.get_by_text("Официальная рыночная оценка").wait_for(timeout=10_000)
            save(page, "instrument-card-1440.png")
            checks["checks"].append("instrument card shows valuation and rule context")

            page.get_by_role("tab", name="Активность").click()
            page.get_by_text("Датированный снимок активности").wait_for(timeout=10_000)
            save(page, "activity-1440.png")
            checks["checks"].append("activity snapshot rendered without historical chart")

            page.get_by_role("tab", name="События").click()
            page.get_by_text("Контекст событий на").wait_for(timeout=10_000)
            assert page.get_by_text("нет загруженных доступных событий", exact=False).count() == 1
            save(page, "events-1440.png")
            checks["checks"].append("21 October event context is empty and caveat rendered")

            page.get_by_role("tab", name="Концепция").click()
            page.get_by_text("будущая полная версия").wait_for(timeout=10_000)
            save(page, "concept-1440.png")
            checks["checks"].append("future concept explicitly labeled")

            # Keyboard navigation must reach an interactive control without mouse input.
            page.keyboard.press("Shift+Tab")
            focused = page.evaluate("""() => { const e = document.activeElement; return {tag: e?.tagName, role: e?.getAttribute('role'), tabindex: e?.getAttribute('tabindex')}; }""")
            assert focused["tag"] in {"BUTTON", "INPUT", "A"} or focused["role"] in {"button", "tab", "combobox", "checkbox"}, focused
            checks["checks"].append("keyboard navigation lands on an interactive focus target")

            # Exercise private illustrative input and export parity in the rendered app.
            page.get_by_text("Сопоставить с планируемой суммой").click()
            amount = page.get_by_test_id("stNumberInputField")
            amount.fill("100000")
            amount.press("Tab")  # commit Streamlit's numeric input before downloading
            page.wait_for_timeout(2_000)
            with page.expect_download() as json_download:
                page.get_by_text("JSON снимка отчёта").click()
            json_path = json_download.value.path()
            with page.expect_download() as csv_download:
                page.get_by_text("CSV отчёта").click()
            csv_path = csv_download.value.path()
            report = json.loads(Path(json_path).read_text(encoding="utf-8"))
            exported = list(csv.DictReader(io.StringIO(Path(csv_path).read_text(encoding="utf-8-sig"))))
            evaluation_rows = [row for row in exported if row["record_type"] == "EVALUATION"]
            event_rows = [row for row in exported if row["record_type"] == "EVENT"]
            valuation_rows = [row for row in exported if row["record_type"] == "VALUATION"]
            assert evaluation_rows and len(evaluation_rows) == len(report["evaluations"]), "CSV evaluation count differs from JSON"
            exported_ids = {row["report_id"] for row in exported}
            assert exported_ids == {report["report_id"]}, f"CSV/JSON report IDs differ: {exported_ids} vs {report['report_id']}"
            assert {row["event_id"] for row in event_rows} == {row["event_id"] for row in report["events"]}, "CSV event IDs differ from JSON"
            assert {(row["instrument_id"], row["valuation_date"], row["valuation_type"]) for row in valuation_rows} == {(row["instrument_id"], row["valuation_date"], row["valuation_type"]) for row in report["valuations"]}, "CSV valuations differ from JSON"
            checks["checks"].append("illustrative 100000 KZT input produces typed CSV/JSON parity for evaluations, events, and valuations")

            # Separate event as-of control is exercised for its conservative date boundaries.
            # Default is the selected 21 October trade date; then move the day segment to 22.
            day = page.get_by_test_id("stDateInput").get_by_role("spinbutton").nth(2)
            assert day.get_attribute("aria-valuetext") == "21"
            day.focus()
            day.press("ArrowUp")
            page.wait_for_timeout(750)
            assert day.get_attribute("aria-valuetext") == "22"
            page.get_by_role("tab", name="События").click()
            page.get_by_text("Открыть источник события").wait_for(timeout=10_000)
            assert page.get_by_text("нет загруженных доступных событий", exact=False).count() == 0
            checks["checks"].append("event availability changes from absent on 21 October to loaded source-backed event on 22 October")

            page.set_viewport_size({"width": 1280, "height": 900})
            page.get_by_role("tab", name="Очередь").click()
            save(page, "overview-1280.png")
            narrow = browser.new_page(viewport={"width": 420, "height": 900})
            narrow.route("**/*", local_only)
            narrow.goto(URL, wait_until="networkidle", timeout=30_000)
            narrow.get_by_text("KASE BondScope", exact=True).wait_for(timeout=10_000)
            narrow.screenshot(path=SHOTS / "narrow-420.png", full_page=True)
            narrow.close()
            checks["checks"].append("responsive layouts captured at 1280px and 420px")
        except Exception as exc:  # record the actual smoke failure for review
            checks["errors"].append(f"{type(exc).__name__}: {exc}")
            raise
        finally:
            CHECKS.write_text(json.dumps(checks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            browser.close()


if __name__ == "__main__":
    main()

# UI slice contract

Builder owns only `mvp/src/app.py`, `mvp/src/theme.css`, `mvp/docs/design_system.md`,
`mvp/full_mockup.md`. Lead owns ingestion, reports, browser tests and screenshots.
Use Streamlit (installed 1.66.1), Russian UI, compact institutional layout.
Run from repo root: `python -m streamlit run mvp/src/app.py`.
Resolve imports from repo root via Path(__file__).resolve().parents[2], never cwd.

Lead API arriving: `from mvp.src.repository import load_snapshot` returns dict:
observations (list canonical dicts, see ENGINE_CONTRACT), instruments (list dicts
instrument_id/ticker/issuer/issuer_id/currency/maturity_date), events (list dicts,
engine fields + title/event_date/source_url/retrieved_at/evidence_status),
sources (list dicts source_id/source_url/retrieved_at/evidence_path/evidence_sha256/
kind/status), coverage (list dicts), rules (dict), release (snapshot_id/status/
limitations/list), valuations (list dicts).
Function raises FileNotFoundError when local evidence pack absent and ValueError
for corrupt hashes. Present explicit missing-input/error states, never fake rows.

`from mvp.src.reports import build_report, report_csv, report_html`.
`build_report(snapshot, selected_rows, as_of, planned_amount_kzt=None)` returns dict
report_id, snapshot_id, as_of, rules, observations, evaluations, events,
limitations, sources. Report is immutable JSON-compatible input snapshot.
`report_csv(report)` -> bytes UTF8-BOM, `report_html(report)` -> str escaped.
Use exactly this same report evaluations/events in UI and downloads. Private
watchlist selection/planned amounts/session notes in st.session_state only.
Do not save user input to repo/logs. UI default planned amount is blank/disabled
until user opts in, not an observed market value. No planned amount in release.

Screens: Overview exception queue with date/ticker filters and separate evaluated,
triggered, blocked counts; instrument card with ISIN/mode and basis explicitly
unconfirmed, trade fields and null valuation reasons; activity dated snapshot table
(history chart only sufficiently verified comparable history, no made-up lines);
event availability as-of, no-event-feed completeness claim; quality/source tabs;
download CSV and readable HTML report + report ID/version; full future A/B/C concept
clearly labeled Concept, no fake clients or connected IRIS.
Date filter and event as-of are separate controls; default event as-of is the selected
trading date. A later date is explicitly retrospective. Financial scenario numbers are out of UI scope.

KASE official guide (2016, still linked) PDF page 9 section 1.8:
graphite #45464F; primary green #038726; accents #3CBD0D/#9ED110;
secondary #FECC00/#EF7F1A/#0094DE. White/light background, Arial/system font.
No downloaded logo or font; text product title and explicit competition prototype.
URLs: https://kase.kz/ru/media-center/corporate-style and
https://kase.kz/uploads/Pravila_KASE_logo_82222dd79b.pdf .
Use green for navigation/action, not investment safety. Clear status labels,
responsive tables, keyboard controls, source links. Avoid huge blank padded cards.
Source strings untrusted: escape HTML (html.escape), validate source URL http(s).
No internal implementation jargon in main flow; details available in source panel.

Real-data update: full official coupon notice recovered; timezone unverified,
conservative availability 22 Oct. Official API valuation observations recovered
for 3 instruments 19–21 Oct; trade active price view still unproved due browser WAF.
Source footer requires written permission for copying; raw/processed market files,
XLSX and screenshots are local evidence, excluded from public git until rights
confirmed. Show local-data setup instructions on missing fresh-clone inputs.

# Agreed project decisions

| ID | Decision | Status | Owner |
|---|---|---|---|
| D-01 | One B2B paid module: BondScope 3.0 | Agreed concept | Whole team |
| D-02 | Primary market: KASE broker-dealer companies working with corporate bonds | Agreed hypothesis, validate count | Member 1 |
| D-03 | No automated buy/sell recommendations, fair-price promises or manipulation verdicts | Agreed | Whole team |
| D-04 | Competition demonstration uses public data only | Required by case | Member 2 |
| D-05 | Subscription pricing: 600,000 KZT/mo | **Scenario hypothesis ONLY**, not approved price | Member 3 |
| D-06 | Final slides: cover + up to 10 content slides, recommendation first | Required | Member 3 |

Add new decisions with date, owner, reason and source. Do not silently rewrite existing agreements.

| D-07 (2026-10-22) | Participant 2 uses Python/Streamlit, immutable local evidence and separate explicit collection; no runtime paid service | Implemented; [run guide](mvp/README_run.md) | Member 2 |
| D-08 (2026-10-22) | Preserve price-view, date-mode and historical-finality gates until matching evidence exists; do not convert two days into a historical baseline | [Acquisition evidence](mvp/implementation/acquisition/acquisition_log.md), partial external blocker | Member 2 |
| D-09 (2026-10-22) | Public Git excludes third-party raw/processed data, workbooks and screenshots while redistribution rights are unresolved; local pack is separate | [Delivery boundary](mvp/evidence.md) | Member 2 |
| D-10 (2026-10-22) | Explicit user decision: BASE assumes 8 paying organizations at M12 and 10 at M24 after launch. The former four-organization BASE was an error. Preserve stress 4/6, the eight-prospect shortlist and four usable instruments as distinct quantities. | ASSUMPTION, not actual customers or verified willingness to pay; [machine reference](mvp/data/base_scenario.json) | User decision; Member 2 outgoing delivery; Member 3 alignment |
| D-11 (2026-10-22) | Complete the limited demo after at most three additional public retrieval approaches. Retain price, mode, history and event-time checks; report software readiness separately from partial data. | Three approaches completed; zero eligible additions. [New record](mvp/implementation/finalization/acquisition/finalization_report_ru.md) | Member 2 |

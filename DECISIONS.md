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

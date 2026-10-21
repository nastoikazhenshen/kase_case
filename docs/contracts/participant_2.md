# KASE BondScope 3.0 — team contract

Read `docs/project_context.md`, `docs/WORKFLOW.md`, `README.md`, `HANDOFF.md`, `DECISIONS.md`, `OPEN_QUESTIONS.md` first. This file is self-contained enough to paste into an individual ChatGPT work chat.

One product: B2B paid module for KASE broker-dealers in Kazakhstan's corporate bond market. Modules A abnormal activity (volume, count, prices), B liquidity / pre-trade context (no execution promise), C public issuer events. Reproducible evidence and exception report. Neither buy/sell AI advice nor manipulation verdict nor fair-price estimator.

Competition: six tasks (data/gap; segment/pain/market; product; working public-data demonstrator; price/unit economics; board recommendation/KPIs/risks). Budget ≤40m KZT, pilot 3 people, MVP launch ≤6m, investment payback ≤24 months after launch. Competition demo public data only; full product may propose licensed datasets once confirmed. Cover + ≤10 content slides with recommendation first; Excel/Sheets with KASE data/source URLs and formulas. Submission deadline 23 Oct 2026 12:00 Astana, academy@kase.kz. Registration language, TeamName_Halyk convention. Claim types: FACT (dated URL), CALCULATION (formula/input), ASSUMPTION (unverified). No fabricated prices, events, customers, interviews or trades. Missing data must not be replaced by invented samples.

# Member 2: Data Analytics & MVP

**Branch:** `feature/data-mvp`. **Folder:** `mvp/`.
**Own:** competition task 4 and empirical/technical contribution to tasks 1,3,6.

## Parallel checklist
1. Confirm exact PUBLIC KASE source URL for corporate bonds, date range, permissible downloads, raw file, schema and units. Do not assume availability.
2. Keep source registry and derivation for `instrument_id`, `trade_date`, `turnover_kzt`, `trades_count`, `last_price`, `weighted_avg_price`, `market_price`, `estimated_price`, `issuer_event`. Only use fields actually accessible; document unavailable ones.
3. Compute explainable anomalies with supported samples: volume vs rolling median, trades count vs baseline, last-to-weighted price discrepancy, revival after inactivity. Handle thin trading, nulls and lookahead rigorously; avoid made-up histories.
4. Build one working fragment (Python/Streamlit, Excel or BI) using REAL public data. Card shows source, date, formula, observed values, caveats, no recommendation.
5. Mock full system, modules A/B/C and user watchlists; clearly mark integrations/features not implemented.
6. Define 6-month technical MVP delivery: architecture, ingestion, rules, history, QA, reports, pilot. Specify technical infrastructure/data-licensing assumptions to member 3.
7. Produce charts/screenshots/data so member 3 can actually cite them. Provide limitations explicitly.

## Deliverables
`mvp/src/`, `mvp/requirements.txt`, `mvp/source_registry.md`, `mvp/metrics_methodology.md`, `mvp/evidence.md`, screenshot or actual working demo, `mvp/full_mockup.md`, implementation notes.

## Handoffs
To member 3: final graphs with factual figures/periods, MVP capabilities, estimated build/hosting costs, source URLs and six-month roadmap. To member 1: data-availability limitations.

**First action:** retrieve and inspect one real public dataset and validate two robust computable metrics before attempting UI.
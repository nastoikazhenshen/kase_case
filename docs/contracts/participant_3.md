# KASE BondScope 3.0 — team contract

Read `docs/project_context.md`, `docs/WORKFLOW.md`, `README.md`, `HANDOFF.md`, `DECISIONS.md`, `OPEN_QUESTIONS.md` first. This file is self-contained enough to paste into an individual ChatGPT work chat.

One product: B2B paid module for KASE broker-dealers in Kazakhstan's corporate bond market. Modules A abnormal activity (volume, count, prices), B liquidity / pre-trade context (no execution promise), C public issuer events. Reproducible evidence and exception report. Neither buy/sell AI advice nor manipulation verdict nor fair-price estimator.

Competition: six tasks (data/gap; segment/pain/market; product; working public-data demonstrator; price/unit economics; board recommendation/KPIs/risks). Budget ≤40m KZT, pilot 3 people, MVP launch ≤6m, investment payback ≤24 months after launch. Competition demo public data only; full product may propose licensed datasets once confirmed. Cover + ≤10 content slides with recommendation first; Excel/Sheets with KASE data/source URLs and formulas. Submission deadline 23 Oct 2026 12:00 Astana, academy@kase.kz. Registration language, TeamName_Halyk convention. Claim types: FACT (dated URL), CALCULATION (formula/input), ASSUMPTION (unverified). No fabricated prices, events, customers, interviews or trades. Missing data must not be replaced by invented samples.

# Member 3: Finance, Business Case & Final Pitch

**Branch:** `feature/financial-model`. **Folders:** `finance/`, `presentation/`.
**Own:** task 5, integrated task 6 and final board submission. Do not label unvalidated price as confirmed.

## Parallel checklist
1. Model one organization/month subscription. Historical idea **600,000 KZT per month** is only a HYPOTHESIS to stress-test. Benchmark KASE existing paid tiers and interview-based customer value where available.
2. Forecast eligible KASE broker-dealers and monthly acquisitions; wait for source-backed SAM from member 1, meanwhile explicitly mark scenario assumptions.
3. Build 6-month development+launch budget for three people: payroll + statutory load, integrations, infrastructure, QA/security, permissions/licenses, sales, reserve. Target ≤40m KZT.
4. Build 24-month AFTER-LAUNCH model: customers_t, churn, average paid price, variable costs, fixed OPEX, incremental revenue after any cannibalization, monthly net cash and cumulative `-initial investment + SUM(monthly net cash)`.
5. Operational break-even customer count `CEILING(fixed OPEX/contribution)` is NOT payback. Show exact first month cumulative cash flow ≥0 (or no payback).
6. Three scenarios conservative/base/optimistic with coherent changes in price, additions, churn and OPEX. Explicitly show failure scenario if relevant.
7. First-year 3–5 KPIs (clients, MRR, active watchlists/reports, time savings, retention), target numbers labeled hypothetical; acquisition and risk mitigations.
8. Receive member 1 market and member 2 verified MVP; assemble cover+10 content slides starting board recommendation, including one real live-data result and one full-product mockup. Never invent data to fill missing chart.
9. QA all numbers, formulas, links, file opening, requested registration language, email/file naming and submission by assigned sender before deadline.

## Deliverables
`finance/unit_economics.xlsx`, `finance/assumptions_and_sources.md`, `finance/financial_summary.md`, `finance/risks_and_kpi.md`; `presentation/deck.pptx`, `slide_script.md`, `submission_checklist.md`.

## Coordination
Immediately request member 1: customer segment, eligible broker counts, competitors and verified price references. Member 2: source-backed working demo, metric screenshots and actual development budget. Publish the finance model's assumption table quickly.

**First action:** put formula-based skeleton plus assumption register in `finance/`; prepare 10-slide storyboard concurrently.
# KASE BondScope 3.0 — team contract

Read `docs/project_context.md`, `docs/WORKFLOW.md`, `README.md`, `HANDOFF.md`, `DECISIONS.md`, `OPEN_QUESTIONS.md` first. This file is self-contained enough to paste into an individual ChatGPT work chat.

One product: B2B paid module for KASE broker-dealers in Kazakhstan's corporate bond market. Modules A abnormal activity (volume, count, prices), B liquidity / pre-trade context (no execution promise), C public issuer events. Reproducible evidence and exception report. Neither buy/sell AI advice nor manipulation verdict nor fair-price estimator.

Competition: six tasks (data/gap; segment/pain/market; product; working public-data demonstrator; price/unit economics; board recommendation/KPIs/risks). Budget ≤40m KZT, pilot 3 people, MVP launch ≤6m, investment payback ≤24 months after launch. Competition demo public data only; full product may propose licensed datasets once confirmed. Cover + ≤10 content slides with recommendation first; Excel/Sheets with KASE data/source URLs and formulas. Submission deadline 23 Oct 2026 12:00 Astana, academy@kase.kz. Registration language, TeamName_Halyk convention. Claim types: FACT (dated URL), CALCULATION (formula/input), ASSUMPTION (unverified). No fabricated prices, events, customers, interviews or trades. Missing data must not be replaced by invented samples.

# Member 1: Product & Market Strategy

**Branch:** `feature/market-research`. **Folder:** `research/`.
**Own:** competition tasks 1,2, product portion 3, first-customer part 6. Do not spend deadline time creating MVP or finance model.

## Parallel checklist
1. Define broker-dealer ICP: distinguish organization paying, approving manager, analysts/traders using. Share with member 3 immediately.
2. Map KASE free products/trading results, indicators, issuer disclosures; contracted IRIS Finance, archives, live streams, prices, API. For each: fields, frequency, price/access level, verified URL/date, absent/unverified features.
3. Establish specific user gap vs IRIS, paid archives, Excel, Bloomberg/LSEG and internal broker tools. No assertion of a feature being absent without checking.
4. Define use cases: trading revival after sparse history; proposed order vs historical traded volumes; issuer disclosure + activity change. Attach measurable savings hypotheses.
5. Estimate TAM/SAM/SOM with sourced broker membership roster and explicit screening, *not* assuming every broker buys. Validate pricing interviews, buying cycles and current workflow.
6. Explain acquisition of first organizations through KASE existing B2B channels as a testable hypothesis.
7. Prepare factual slide text for slides 2,3,4,5,8 and recommendations.

## Deliverables
`research/market_map.md`; `customer_segment.md`; `competition_gap.md`; `use_cases_and_interviews.md`; `slides_product.md`.

## Handoffs
To member 2: validated KASE data URLs/fields and exact end-user cases. To member 3: TAM/SAM/SOM, tariff comparisons, expected paying companies, adoption pipeline, GTM, sources and limitations.

**First action:** verify KASE service matrix and publish initial ICP and no-more-than-three testable use cases. Progress independent of other teammates.
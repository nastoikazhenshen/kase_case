# Cross-team handoff board

## Status
- Member 1 (Market): not yet handed off.
- Member 2 (MVP): local limited demo and editable slides 6–7 delivered on `feature/data-mvp`; [current technical handoff](mvp/handoff/technical_delivery.md).
- Member 3 (Finance): draft financial scenarios only; assumptions unvalidated.

## Required format for each handoff
**Date; owner; file/PR link; competition question; claim; type [FACT/CALCULATION/ASSUMPTION]; supporting URL and retrieved date; units; formula if applicable; limitations; receiving owner.**

## Member 1 → 3
Provide source-backed TAM/SAM/SOM, customer role and payer, KASE product comparisons, tariff references and adoption assumptions. Do not treat total KASE members as all purchasable clients.

## Member 2 → 3
Provide verified source files/links, chosen metrics and formulas, charts with exact units and date range, MVP screenshot, technical roadmap and costs.

## Member 3 → 1 and 2
Communicate finance constraints, feasible license price ranges, MVP cutline and presentation data requests. Maintain single source of truth for subscription and client forecasts.

**Never mark a handoff completed until a real file/PR is linked.**

## 2026-10-22 — Member 2 → Members 1 and 3

Participant 2 delivered the local real-data prototype and [technical handoff](mvp/handoff/technical_delivery.md)
on `feature/data-mvp`. FACT: five instruments/two retained dates, nine official
valuation records and one recovered full notice. CALCULATION: reproducible daily
context with KZT/ratio units; [formulas](mvp/metrics_dictionary.md).
ASSUMPTION: thresholds and future IRIS integration. [Sources and retrieval evidence](mvp/source_registry.md),
[data limits](mvp/handoff/data_limits.md), [scenario-version/cell corrections for Member 3](mvp/handoff/finance_consistency.md).
Market evidence/screenshots/XLSX remain in a separate local package pending reuse rights;
public Git contains code/manifests. Historical and price-view gates remain open.

## 2026-10-22 — Member 2 finalization, superseding earlier delivery summary

The explicit user-approved BASE is **8 paying organizations at M12 / 10 at M24 after launch**, an ASSUMPTION. [Finance reconciliation and corrected-copy location](mvp/handoff/finance_consistency.md) record independent recomputation, preservation of the source workbook and exact suggestions for `origin/feature/financial-model`; that teammate branch was not changed.

Software/demo status: `READY_WITH_LIMITATIONS`. Market-data status: `PARTIAL_DATA`; the original partial snapshot is retained. Three additional public retrieval approaches added no eligible observations. Six rules are implemented; one amount/day-turnover rule is computable on four latest-date rows after explicit user input. Five rules remain gated.

Actual editable [slides 6–7 and previews](mvp/implementation/finalization/slides_6_7_record.md), [speaker notes](mvp/handoff/slides_6_7_notes.md), and [launch guide](mvp/README_run.md) are ready for assembly into the team's deck. Binaries and source-derived evidence remain local. Final tested SHA, review and package checksums are in [the final report](mvp/reviews/final_report_ru.md).

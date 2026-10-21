# Team workflow & merge contract

## Git rules
- `main`: agreed shared baseline, do not push feature work directly.
- Member 1: `feature/market-research` → `research/`.
- Member 2: `feature/data-mvp` → `mvp/`.
- Member 3: `feature/financial-model` → `finance/` and `presentation/`.
- Add documented cross-team requests to `HANDOFF.md` by PR, or coordinate in group chat when time-critical.
- Each PR must state: what changed, factual sources, assumptions, tests, limitations, dependency on others, and which competition question is answered.
- Only merge reviewed and confirmed outputs; do not rewrite another member's files without coordination.
- Merge PRs as soon as stable; sync your branch with `main` before further merges.

## Parallel handoffs
- Member 1 → Member 3: verified ICP & customer counts, source URLs, alternative/product gaps, acquisition assumptions.
- Member 1 → Member 2: source locations, confirmed fields, customer use cases.
- Member 2 → Member 3: reproducible KPI/graphs, screenshot/demo and architecture, MVP cost constraints, sources.
- Member 3 → all: actual pricing hypothesis, cost constraints, story of 10-slide board deck.

## File integrity
- `FACT`: date/URL/origin. `CALCULATION`: input dataset and formula. `ASSUMPTION`: explicit unvalidated estimate.
- Public repository: NEVER upload confidential/paid data or personal information.
- Keep raw public data files compact and record retrieval date/URL; no invented data.
- Finance file model and slides must have a consistent snapshot (client count, price, OPEX, CAPEX, month of payback).
- GitHub cannot effectively diff binary XLSX and PPTX. Mirror important parameters in `finance/assumptions_and_sources.md`.

## Time-critical checklist
1. All six tasks addressed.
2. Public-data MVP verified.
3. One primary customer segment.
4. Under 40m KZT and launch within 6 months.
5. Payback checked including all operating costs and commercial cash flow, within 24m AFTER launch.
6. First slide recommendation, max 10 content slides, sources, Excel formulas.
7. Final files manually verified and emailed by assigned team member before official deadline.

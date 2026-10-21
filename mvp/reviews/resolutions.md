# Adversarial findings and remediation

Actual independent reviewer: `gpt-5.6-terra` / high; routing evidence in
`agent_manifest.json`. Findings were returned through the collaboration channel.
The table records engineering dispositions; final independent verdict is separate.

| Finding | Severity / reproduction | Remedy and regression evidence |
|---|---|---|
| Early contract: selected tab, date-mode, history and missing-data claims | P1 risk: quote convention cannot prove the tab; two days cannot supply 10 prior rows | Price/history gates retained; no date-mode backfill; official browser/SSR attempts and blockers documented |
| Date precision became available at midnight on publication day | P1: DATE publication with verified timezone | Next-day availability for DATE precision; minute/second aware boundaries and UTC equivalence tested |
| Evaluation as-of substituted retrieval time | P1: retrieval after trading date | Explicit observation_as_of or disclosed retrospective end-of-day +05 policy; regression rejects naive timestamps |
| Historical current/finality mismatch and unvalidated baseline rows | P1: mix interim/EOD or corrupt prior turnover | Require eligible current finality, identical baseline finality, validate prior rows; regression tests |
| Rounded-zero inconsistency | P2: nonzero turnover labeled ROUNDED_ZERO | Enforce zero turnover with positive trade count; preserve missing vs exact zero |
| Price-gap sign lost; price gate incorrectly blocked turnover context (lead findings) | P1: signed value became absolute; unverified price blocked independent activity ratio | Signed percentage retained; absolute threshold only; price gate applies to price rules only |
| P1-PROV-01 revalidation timestamps dropped | P1: revision manifest used completion field while builder read retrieved_at only | Canonical retrieval uses actual completed_at, retains start/end and status; revision-shape and real-context regressions |
| P1-PROV-02 contradictory event verification | P1: full notice plus current search-excerpt field | Consistent full-notice fields and current evidence ID; original evidence IDs/status retained under legacy fields |
| P1-XLSX-01 dates rendered as serial numbers | P1: preview displayed 46316 | Human-readable date text and timezone-preserving instant text; visible regenerated previews, live formula/zero/input checks |
| P1-EXPORT-01 CSV lost event/valuation context | P1: JSON/HTML had context absent in CSV | Typed EVALUATION/EVENT/VALUATION/SOURCE CSV rows; both as-of dates and actual browser CSV/JSON identity tests |
| Row source URLs incomplete | P2: multiple source IDs but only primary URL | Report resolves all IDs through registry, carries baseline proof IDs too; provenance set comparison |
| Stale path aliases (lead finding) | P1: source_file/raw_file old paths survived beside normalized evidence_path | Aliases normalized, originals explicitly retained; master-source and path-alias corruption tests |
| P0-RUN-01 / P1-RUN delivery path absent during interim review | Release blocker until demonstrated | Safe pack restore implemented; traversal/symlink/hash/idempotence tests; exact local pack and clean-clone proof required for final verdict |
| Cache sidecar could override actual digest (lead finding) | P1: bytes differ from sidecar | Cache hash/source URL check, exact observed-route allowlist; stale-sidecar and unobserved-route tests |
| P2-DOC interim restore text and Python version drift | P2: documentation described planned extractor/Python3.11 | Delivered extractor documented; lead runtime pinned/tested Python3.12.14. Reviewer also exercised a separate Python3.13 runtime |
| Release review artifacts missing during implementation | Release blocker | This record, routing manifest, final independent review and final verification report supplied before release |

External limitations D01–D03 and finance/rights decisions remain open; they are not
resolved by passing code tests. No historical-data success or KASE endorsement is claimed.

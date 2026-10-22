# Independent adversarial finalization review

## Verdict

**ACCEPTED for the stated limited, offline demonstrator and local handoff scope.**

Reviewed implementation commit: `7fe1ca8ffcd728378349e09cd716be9918182b5f`.

No open P0 or P1 implementation defects were reproduced. This verdict does not
claim a production market-data release: the price, history, rights and
commercial-validation gates remain intentionally open.

## Evidence reviewed

- Snapshot `BS3-40698bfc0c453479`; demonstration report
  `BS3-REPORT-a9c167a239e236660e1a`.
- Final local evidence pack
  `mvp/local_pack/bondscope-evidence-final-20261022.zip`, SHA-256
  `c893261e7787aaaa0ad10d2903db86d4dd7ab926ae47a53c591fdd746a1c84e1`.
  Independent ZIP inspection found 185 manifest members, 185 payload members,
  no case-colliding duplicates, no nested ZIP, and zero hash/size mismatches.
  It includes only v5 slide artifacts among `slides6_7*` files.
- Finance source workbook SHA-256
  `9cfaf368374565280560c66a3534e15045645ca1a3e825eba0d9698c04b2e68b` and
  corrected local workbook SHA-256
  `742c6539fb1b5776d92db9fb311434aa23bdc1705e03c73e876ff1d6b3c67601`.
- v5 PPTX, raster-PDF and PNG render manifest. I visually inspected both PNG
  renders and the finance render previews. Slide 6 contains the real frozen
  offline app frame, the explicit hypothetical user input, and an independently verified report-derived ratio.
  Slide 7 is fully visible and uses the agreed A/B/C concepts.
- `mvp/reviews/finalization/clean_clone_check.json`: fresh Python 3.12.14
  environment, expected missing-data failure before restore, 185 verified and
  written files on restore, 53 application tests plus 18 archive tests, and
  byte parity for snapshot/default/demo report outputs.

## Independent checks run

- `mvp/.venv/Scripts/python.exe mvp/scripts/verify_final_artifacts.py` — PASS.
  It independently matched JSON/CSV/HTML/XLSX, default blank input, two-slide
  PPTX embedded screenshot bytes, rendered PDF/PNG hashes, and finance hashes.
- Focused finance, demo, analytics, events, repository-report and acquisition
  suite — 42 tests PASS.
- Pack manifest/member/hash inspection described above — PASS.

The recorded candidate final check additionally shows 53 application tests,
18 archive tests, reconciliation, finance validation, 12 browser checks and
cross-format verification at exit code zero. The fresh-clone record repeats
53 + 18 tests after restoration.

## Findings resolved in this candidate

- **P1-FIN-TEST:** the source-workbook regression now reads formula structure
  and detailed numeric inputs correctly; all four finance tests pass.
- **P1-FIN-PROVENANCE / P1-FIN-BRANCH:** final finance hash is synchronized;
  the actual `origin/feature/financial-model` v4 reference is recorded as
  distinct from the v5 assumption. The unsupported 12–18 SAM range remains an
  explicit unresolved conflict, not an adopted assumption.
- **P1-SLIDE-TRACE / P1-SLIDE-CLIP:** v5 has an immutable source-image hash,
  editable two-slide PPTX, actual two-page raster PDF and PNG renders. The
  cropped prior Slide 7 render and placeholder documentation are resolved.
- **P1 data safeguards:** price-view, mode, finality and history gates remain
  preserved; the timezone-unverified CLSGb11 event remains unavailable on 21
  October and only appears in later retrospective context.

## Remaining P2

- **P2-LINT-SCOPE:** `final_checks.json` and the clean-clone record run
  `ruff check ... --select F`, which passes. A broader unqualified
  `ruff check mvp/src mvp/tests mvp/scripts` reports 60 non-fatal style and
  modernization findings. Describe the successful result as the Ruff F/fatal
  subset, not as a fully clean default Ruff run. This does not affect the
  functional or evidence checks above.

## External limitations retained

- Active price view is unverified, only four 21 October trading modes are
  verified, there is no eligible prior-history series, and published
  finality is not certified EOD. Five of six rules therefore remain gated.
- The event feed is incomplete; CLSGb11 uses the conservative next-day policy
  because publication timezone is not printed.
- Raw evidence, final outputs and packs are local-only pending redistribution
  rights. KASE/IRIS/API integration is conceptual rather than implemented.
- The 600,000 KZT, 8/M12 and 10/M24 scenario is an assumption, not observed
  demand, paid contracts or validated willingness to pay. Native Excel or
  LibreOffice recalculation/print rendering remains outside the executed
  artifact-tool validation.

## Curated handoff-pack audit

The curated local handoff mvp/local_pack/BondScope_Participant2_Final_20261022.zip has SHA-256 6674530a68576a430ab0278de8c87b058f1b68517ed9795add7327d8f89ac9dd. Its manifest identifies implementation 7fe1ca8ffcd728378349e09cd716be9918182b5f, lists 29 delivered files, and names the evidence pack SHA-256 c893261e7787aaaa0ad10d2903db86d4dd7ab926ae47a53c591fdd746a1c84e1. Independent inspection found 29 payload members plus the manifest, no duplicate case-folded names, all member hashes/sizes valid, and exactly one nested archive: the manifest-named evidence ZIP. Recursive archive inclusion is false.

# Finalization remediation record

Tested implementation: `7fe1ca8ffcd728378349e09cd716be9918182b5f`.

| Finding | Final correction | Verification |
|---|---|---|
| Financial test validated only self-consistent JSON; formula strings caused an intermediate failure | Bind the 24-month sales path, cost inputs, detailed startup calculation and formula structure to the immutable source workbook | Four finance tests, independent CLI, 53-test final suite and fresh clone pass |
| Incorrect financial branch lookup and stale hash | Inspect `origin/feature/financial-model`; distinguish v4 legacy from v5; synchronize final workbook SHA in current records | Reviewer and cross-format hash checks pass |
| SAM provenance was insufficient | Preserve C33, mark unresolved conflicting ranges in F33; prepare teammate-owned-file suggestions | Full 16-sheet comparison reports only allowlisted changes |
| Slide placeholder record, wrong A/B/C meanings and cropped roadmap | Create actual v5 editable PPTX and render it; correct A/B/C and fitting layout | Two slides, actual PNG/PDF, visual inspection by lead/reviewer, geometry/reimport checks |
| Re-running browser smoke changed the screenshot file used by a slide | Freeze the exact checked bytes into a versioned slide-source PNG; generate numbers/IDs from canonical report | Preserved failing intermediate `attempt_bfc19df.json`; final checks and fresh clone now verify embedded bytes and all output hashes |
| Fresh-clone verifier output folder absent | Create the verifier output parent; use unique per-SHA final-check log directories | Clean restore and complete rerun pass; previous logs preserved |
| Bundled authoring package was damaged during an attempted local font workaround | Restore only the exact installed official runtime package files with hash checks; remove only verified agent-created empty shim files | Runtime recovery record; supported authoring/render pipeline successfully builds final workbooks/slides |

No validity gate was relaxed, no observation invented, no immutable archive test removed or modified. Accepted remaining P2: the requested Ruff F subset passes; full default lint has 60 style/modernization findings. External price/history/finality/event-time/rights and commercial-model limitations are documented separately, not reported as fixed defects.

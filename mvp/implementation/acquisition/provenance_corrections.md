# Provenance correction log

## 2026-10-22 — CLSGb15 trade-info manifest digest

`evidence_manifest.json` previously recorded
`183ff0fdf846880f91bf7ad5b221bd479991b350736ee9d6e0bf4c33f9706adbd`
for `CLSGb15.trade-info.json`. A full local byte audit found the immutable
file's actual SHA-256 is
`183ff0fd846880f91bf7ad5b221bd479991b350736ee9d6e0bf4c33f9706adbd`
and its size is 1,616 bytes. The erroneous digest has an extra `f` after the
first eight hexadecimal characters. No source byte or market value changed.

The manifest was corrected only after that byte audit. The original incorrect
string is retained here so the correction is traceable.

## 2026-10-22 — controlled revalidation revisions

The original `market-valuations.json` and `CLSGb11-event-1578268.html` remain
immutable. One new anonymous GET was made for each already-observed source and
saved under `mvp/data/raw/acquisition/2026-10-22/revisions/2026-10-22/` with
collector start/end times and allowlisted response headers in adjacent
`.provenance.json` files. The valuation bytes are identical to the original.
The notice HTML digest differs because the server-rendered page changed outside
the notice body; it is a new revision, not an overwrite or claim that the event
changed.

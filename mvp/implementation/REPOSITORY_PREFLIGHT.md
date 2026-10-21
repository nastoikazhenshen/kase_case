# Repository preflight — 22 October 2026

Development checkout: `E:/kase_case/kase_case`.
SSH clone and `git fetch origin --prune` succeeded. Remote is
`git@github.com:nastoikazhenshen/kase_case.git`; default branch is `main`.
Initial main and designated Participant 2 branch both point to
`bcd24725855b92a86eb23f720bcd921b7aa5d837`. Clean checkout; no existing local work.
Selected existing remote `feature/data-mvp` as a local tracking branch.
Finance branch at `b107441df62a92eabd5f7f705aefab384c874e08` was read, not merged.
No AGENTS.md files found in the repository. Role contracts and working agreement read.

Stack: Python deterministic analytics and Streamlit local UI. No runtime LLM,
database or external service required. Acquisition is a separate explicit step.
All implementation belongs under `mvp/`; only additive root handoffs and reviewed
project-local Codex configuration are permitted.

The supplied bundle contains already-extracted input directories; ZIP files named
in its manifest are absent. Verify inner manifests and retain this difference.
Do not claim original ZIP byte hashes were checked in this execution.

Installed Codex: `codex-cli 0.163.0-alpha.10.2`. Bundled catalog includes
`gpt-5.6-terra`, including medium/high reasoning. Explicit spawn requests succeeded.
Session turn metadata independently confirms lead `gpt-6-astra` / xhigh,
reviewer `gpt-5.6-terra` / high, data worker `gpt-5.6-terra` / medium.
The sandbox launcher fails when enumerating unrelated BitLocker-locked D:;
approved escalated shell operations work. No sandbox settings were weakened.

Template schema compared with official subagent/configuration references:
https://learn.chatgpt.com/docs/agent-configuration/subagents
https://learn.chatgpt.com/docs/config-file/config-reference
`--strict-config` is unsupported for `codex debug`. Compatibility was then checked with
`codex exec --strict-config` and a deliberately absent `--output-schema` path: valid
agent fields reached the missing-schema check before any model request; an unknown
configuration-key control was rejected by strict parsing. The same check passed
after installing the four project-local templates with refusal to overwrite existing
files. Global configuration and permission settings were not modified. Template
comments are preserved as origin context; these are now active project-local files.
The builder's session metadata also confirms `gpt-5.6-terra` / medium. See
`reviews/agent_manifest.json` for independently observed routing, not self-reported identity.

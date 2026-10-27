# Wealthlab agent instructions

Read README.md, CONTEXT.md and the relevant docs/adr/ before changes.

Only public code, original documentation, public-source references and synthetic fixtures belong here. Never publish private household records, adviser communications, local source paths, account identifiers, credentials or downloaded market data without established redistribution rights. Private inputs and generated results remain in a user-selected directory outside this repository.

Follow ponytail: reuse tested libraries and existing functions; keep concrete modules small. Never simplify away financial accounting, uncertainty, validation or requested features. Establish a runnable check for nontrivial calculations.

Use gh-stack for dependent work. Create each layer before its code; keep ownership in the correct layer. Each feature ticket delivers inputs, computation, UI output and meaningful checks. Validate the exact current head, obtain an independent ChatGPT-Sol 6.1 (`gpt-6.1-sol`) review, address all findings and rerun affected checks. Publish and re-read a submitted native GitHub PR review tied to that full commit SHA; a local report or review of an earlier head is insufficient. See docs/development.md for the review protocol. Do not merge with unresolved findings or failing/unverified required checks. Private data must never be sent to review bots.

First-party Python gates: CC <= 8, MI >= 50, module SLOC <= 300, function span <= 60 physical lines. Tests and tooling are included. Do not weaken thresholds to pass a change.

## Agent skills

### Issue tracker

GitHub Issues in pavelkrotkov/wealthlab, inferred from origin. Inherited convention: use gh CLI. See docs/agents/issue-tracker.md.

### Triage labels

Use the inherited canonical labels. See docs/agents/triage-labels.md.

### Domain docs

One CONTEXT.md and docs/adr/. See docs/agents/domain.md.

Before adding complexity for a speculative or vanishingly unlikely race or security edge case, explain the concrete failure mode, likelihood, and complexity cost to the user and get their buy-in. Do not silently expand scope for theoretical robustness.
